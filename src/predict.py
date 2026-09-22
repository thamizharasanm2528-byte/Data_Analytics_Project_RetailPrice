"""
Prediction Module
------------------
Loads the trained model and provides prediction functionality.
Uses the SAME preprocessing and feature engineering logic as training.
"""
import os
import pandas as pd
import numpy as np
import joblib

from src.config import (
    MODEL_PATH, FEATURE_COLUMNS_PATH, PREPROCESSOR_PATH,
    FEATURES_PATH, STORES_PATH, MARKDOWN_COLS,
)
from src.data_preprocessing import (
    load_csv, parse_dates, handle_missing_values, encode_categoricals,
)
from src.feature_engineering import create_temporal_features, create_derived_features


def load_trained_model():
    """Load the trained model and associated artifacts."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"No trained model found at {MODEL_PATH}. "
            f"Run src/train.py first."
        )

    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)

    scaler = None
    if os.path.exists(PREPROCESSOR_PATH):
        scaler = joblib.load(PREPROCESSOR_PATH)

    return model, feature_columns, scaler


def predict_single(store, dept, date, is_holiday,
                   temperature, fuel_price, cpi, unemployment,
                   markdown1=0, markdown2=0, markdown3=0,
                   markdown4=0, markdown5=0,
                   store_type="A", store_size=150000):
    """
    Predict weekly sales for a single input.

    Parameters
    ----------
    store : int
        Store number (1-45).
    dept : int
        Department number.
    date : str
        Date string (YYYY-MM-DD).
    is_holiday : bool
        Whether the week contains a holiday.
    temperature : float
        Average temperature.
    fuel_price : float
        Fuel price.
    cpi : float
        Consumer Price Index.
    unemployment : float
        Unemployment rate.
    markdown1-5 : float
        Markdown promotional values (default 0).
    store_type : str
        Store type A/B/C (used if store not in stores.csv).
    store_size : int
        Store size in sq ft (used if store not in stores.csv).

    Returns
    -------
    float
        Predicted weekly sales.
    """
    model, feature_columns, scaler = load_trained_model()

    # Build input dataframe matching the preprocessing pipeline
    input_data = pd.DataFrame([{
        "Store": store,
        "Dept": dept,
        "Date": date,
        "IsHoliday": is_holiday,
        "Temperature": temperature,
        "Fuel_Price": fuel_price,
        "MarkDown1": markdown1,
        "MarkDown2": markdown2,
        "MarkDown3": markdown3,
        "MarkDown4": markdown4,
        "MarkDown5": markdown5,
        "CPI": cpi,
        "Unemployment": unemployment,
    }])

    # Try to get store info from stores.csv
    try:
        stores = load_csv(STORES_PATH)
        store_info = stores[stores["Store"] == store]
        if len(store_info) > 0:
            store_type = store_info.iloc[0]["Type"]
            store_size = store_info.iloc[0]["Size"]
    except Exception:
        pass

    type_map = {"A": 2, "B": 1, "C": 0}
    input_data["Type_encoded"] = type_map.get(store_type, 1)
    input_data["Size"] = store_size

    # Parse dates and create features
    input_data["Date"] = pd.to_datetime(input_data["Date"])
    input_data["IsHoliday"] = input_data["IsHoliday"].astype(int)
    input_data = create_temporal_features(input_data)
    input_data = create_derived_features(input_data)

    # Drop Date column
    input_data = input_data.drop(columns=["Date"])

    # Ensure all expected columns exist
    for col in feature_columns:
        if col not in input_data.columns:
            input_data[col] = 0

    # Keep only the expected columns in the right order
    input_data = input_data[feature_columns]

    # Apply scaler if needed (Linear Regression)
    if scaler is not None:
        non_id_cols = [c for c in feature_columns if c not in ["Store", "Dept"]]
        input_data[non_id_cols] = scaler.transform(input_data[non_id_cols])

    prediction = model.predict(input_data)[0]
    return round(prediction, 2)


def predict_batch(input_df):
    """
    Predict weekly sales for a batch of inputs.
    input_df must contain: Store, Dept, Date, IsHoliday,
    Temperature, Fuel_Price, CPI, Unemployment, MarkDown1-5.

    Returns the input_df with a Predicted_Weekly_Sales column added.
    """
    model, feature_columns, scaler = load_trained_model()

    df = input_df.copy()

    # Load store info
    try:
        stores = load_csv(STORES_PATH)
        df = df.merge(stores, on="Store", how="left")
    except Exception:
        if "Type" not in df.columns:
            df["Type"] = "A"
        if "Size" not in df.columns:
            df["Size"] = 150000

    # Preprocessing
    df = parse_dates(df)
    df = handle_missing_values(df)
    df = encode_categoricals(df)

    # Feature engineering
    df = create_temporal_features(df)
    df = create_derived_features(df)

    # Prepare features
    df_features = df.drop(columns=["Date"], errors="ignore")
    for col in feature_columns:
        if col not in df_features.columns:
            df_features[col] = 0
    df_features = df_features[feature_columns]

    # Apply scaler if needed
    if scaler is not None:
        non_id_cols = [c for c in feature_columns if c not in ["Store", "Dept"]]
        df_features[non_id_cols] = scaler.transform(df_features[non_id_cols])

    predictions = model.predict(df_features)
    result = input_df.copy()
    result["Predicted_Weekly_Sales"] = predictions.round(2)
    return result


if __name__ == "__main__":
    # Example prediction
    print("Example prediction:")
    pred = predict_single(
        store=1, dept=1, date="2013-01-04", is_holiday=False,
        temperature=40.0, fuel_price=3.5, cpi=220.0, unemployment=6.5,
    )
    print(f"  Store 1, Dept 1, 2013-01-04: ${pred:,.2f}")
