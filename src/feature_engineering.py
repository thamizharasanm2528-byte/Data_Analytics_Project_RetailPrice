"""
Feature Engineering Module
---------------------------
Creates temporal, derived, and interaction features
from the preprocessed dataset. All transformations use
only information available at prediction time (no leakage).
"""
import pandas as pd
import numpy as np
from src.config import MARKDOWN_COLS, TARGET_COL


def create_temporal_features(df):
    """
    Extract temporal features from the Date column.
    Requires Date to be datetime64 type.
    """
    df = df.copy()

    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"])

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["WeekOfYear"] = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeek"] = df["Date"].dt.dayofweek
    df["Quarter"] = df["Date"].dt.quarter
    df["IsMonthStart"] = df["Date"].dt.is_month_start.astype(int)
    df["IsMonthEnd"] = df["Date"].dt.is_month_end.astype(int)

    print(f"  Created temporal features: Year, Month, WeekOfYear, "
          f"DayOfWeek, Quarter, IsMonthStart, IsMonthEnd")
    return df


def create_derived_features(df):
    """
    Create derived features from existing columns.
    - TotalMarkDown: sum of all markdown columns
    - HasMarkDown: binary indicator of any markdown activity
    """
    df = df.copy()

    # Total markdown spend
    available_md = [c for c in MARKDOWN_COLS if c in df.columns]
    if available_md:
        df["TotalMarkDown"] = df[available_md].sum(axis=1)
        df["HasMarkDown"] = (df["TotalMarkDown"] > 0).astype(int)
        print(f"  Created derived features: TotalMarkDown, HasMarkDown")

    return df


def prepare_features(df, is_training=True):
    """
    Apply all feature engineering and prepare the final feature matrix.

    Parameters
    ----------
    df : pd.DataFrame
        Preprocessed dataframe (output of data_preprocessing.preprocess).
    is_training : bool
        If True, also return the target column.

    Returns
    -------
    X : pd.DataFrame
        Feature matrix (Date column dropped).
    y : pd.Series or None
        Target variable (only if is_training=True).
    """
    print("Feature Engineering...")
    df = create_temporal_features(df)
    df = create_derived_features(df)

    # Drop columns not used as features
    drop_cols = ["Date"]
    if is_training and TARGET_COL in df.columns:
        y = df[TARGET_COL].copy()
        drop_cols.append(TARGET_COL)
    else:
        y = None

    X = df.drop(columns=[c for c in drop_cols if c in df.columns])

    print(f"  Feature matrix: {X.shape[0]:,} rows × {X.shape[1]} features")
    if y is not None:
        print(f"  Target: {TARGET_COL} "
              f"(mean={y.mean():,.2f}, std={y.std():,.2f})\n")

    return X, y


def get_feature_names(X):
    """Return the list of feature column names."""
    return list(X.columns)
