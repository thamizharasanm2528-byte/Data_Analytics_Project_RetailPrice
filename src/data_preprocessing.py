"""
Data Preprocessing Module
-------------------------
Handles loading, validation, merging, cleaning, and encoding of the
Walmart Store Sales Forecasting dataset.
"""
import pandas as pd
import numpy as np
from src.config import (
    TRAIN_PATH, TEST_PATH, FEATURES_PATH, STORES_PATH,
    MERGE_KEYS_FEATURES, MERGE_KEYS_STORES,
    MARKDOWN_COLS, TARGET_COL,
)


def load_csv(path, parse_dates=None):
    """Load a CSV file with basic validation."""
    df = pd.read_csv(path, parse_dates=parse_dates)
    print(f"  Loaded {path.split(chr(92))[-1].split('/')[-1]}: "
          f"{df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


def load_all_data():
    """Load all four core dataset files."""
    print("Loading datasets...")
    train = load_csv(TRAIN_PATH)
    test = load_csv(TEST_PATH)
    features = load_csv(FEATURES_PATH)
    stores = load_csv(STORES_PATH)
    print()
    return train, test, features, stores


def validate_schemas(train, test, features, stores):
    """Verify expected columns exist in each dataframe."""
    expected = {
        "train": ["Store", "Dept", "Date", "Weekly_Sales", "IsHoliday"],
        "test": ["Store", "Dept", "Date", "IsHoliday"],
        "features": ["Store", "Date", "Temperature", "Fuel_Price",
                      "MarkDown1", "MarkDown2", "MarkDown3", "MarkDown4",
                      "MarkDown5", "CPI", "Unemployment", "IsHoliday"],
        "stores": ["Store", "Type", "Size"],
    }
    dataframes = {"train": train, "test": test,
                  "features": features, "stores": stores}

    for name, cols in expected.items():
        missing = set(cols) - set(dataframes[name].columns)
        if missing:
            raise ValueError(
                f"Schema validation failed for {name}: "
                f"missing columns {missing}"
            )
    print("Schema validation passed for all datasets.\n")


def parse_dates(df):
    """Convert the Date column to datetime."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def merge_data(df, features, stores):
    """
    Merge a train or test dataframe with features and stores.

    Merge order:
      1. df + features  on (Store, Date, IsHoliday)
      2. result + stores on (Store)
    """
    # Parse dates consistently before merging
    df = parse_dates(df)
    features = parse_dates(features)

    initial_rows = len(df)

    # Merge with features
    merged = df.merge(features, on=MERGE_KEYS_FEATURES, how="left")
    if len(merged) != initial_rows:
        print(f"  WARNING: Row count changed after features merge: "
              f"{initial_rows:,} -> {len(merged):,}")

    # Merge with stores
    merged = merged.merge(stores, on=MERGE_KEYS_STORES, how="left")
    if len(merged) != initial_rows:
        print(f"  WARNING: Row count changed after stores merge: "
              f"{initial_rows:,} -> {len(merged):,}")

    # Check for duplicates introduced by merging
    dups = merged.duplicated().sum()
    if dups > 0:
        print(f"  WARNING: {dups:,} duplicate rows found after merge")

    print(f"  Merged shape: {merged.shape[0]:,} rows × {merged.shape[1]} cols")
    return merged


def handle_missing_values(df):
    """
    Handle missing values according to the data engineering plan:
    - MarkDown1-5: fill with 0 (no promotion = no markdown)
    - CPI: forward-fill then backward-fill per store
    - Unemployment: forward-fill then backward-fill per store
    """
    df = df.copy()

    # MarkDown columns: missing means no promotion was active
    for col in MARKDOWN_COLS:
        if col in df.columns:
            n_missing = df[col].isna().sum()
            if n_missing > 0:
                df[col] = df[col].fillna(0)
                print(f"  Filled {n_missing:,} missing values in {col} with 0")

    # CPI and Unemployment: forward-fill then backward-fill within each store
    for col in ["CPI", "Unemployment"]:
        if col in df.columns:
            n_missing = df[col].isna().sum()
            if n_missing > 0:
                df[col] = df.groupby("Store")[col].transform(
                    lambda s: s.ffill().bfill()
                )
                remaining = df[col].isna().sum()
                print(f"  Filled {n_missing - remaining:,}/{n_missing:,} "
                      f"missing values in {col} via ffill+bfill")
                if remaining > 0:
                    # Fallback: fill with overall median
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    print(f"  Filled remaining {remaining:,} with "
                          f"median ({median_val:.2f})")

    return df


def encode_categoricals(df):
    """
    Encode categorical variables:
    - Store Type (A/B/C) -> ordinal integer (A=2, B=1, C=0)
      based on correlation with store size
    - IsHoliday -> int (0/1)
    """
    df = df.copy()

    # Encode Store Type
    if "Type" in df.columns:
        type_map = {"A": 2, "B": 1, "C": 0}
        df["Type_encoded"] = df["Type"].map(type_map)
        df = df.drop(columns=["Type"])
        print("  Encoded Store Type: A=2, B=1, C=0")

    # Encode IsHoliday
    if "IsHoliday" in df.columns:
        df["IsHoliday"] = df["IsHoliday"].astype(int)

    return df


def preprocess(df, features, stores):
    """
    Full preprocessing pipeline:
      1. Merge datasets
      2. Handle missing values
      3. Encode categoricals
    """
    print("Preprocessing...")
    merged = merge_data(df, features, stores)
    cleaned = handle_missing_values(merged)
    encoded = encode_categoricals(cleaned)

    remaining_nulls = encoded.isnull().sum()
    total_nulls = remaining_nulls.sum()
    if total_nulls > 0:
        print(f"\n  Remaining missing values:\n{remaining_nulls[remaining_nulls > 0]}")
    else:
        print("  No missing values remain after preprocessing.")

    print(f"  Final shape: {encoded.shape[0]:,} rows × {encoded.shape[1]} cols\n")
    return encoded


def get_preprocessed_data():
    """
    Convenience function: load all data, validate, and preprocess.
    Returns preprocessed train and test DataFrames.
    """
    train, test, features, stores = load_all_data()
    validate_schemas(train, test, features, stores)

    print("--- Processing Training Data ---")
    train_processed = preprocess(train, features, stores)

    print("--- Processing Test Data ---")
    test_processed = preprocess(test, features, stores)

    return train_processed, test_processed


if __name__ == "__main__":
    train_processed, test_processed = get_preprocessed_data()
    print("Training data sample:")
    print(train_processed.head())
    print(f"\nTraining columns: {list(train_processed.columns)}")
    print(f"\nTest data sample:")
    print(test_processed.head())
