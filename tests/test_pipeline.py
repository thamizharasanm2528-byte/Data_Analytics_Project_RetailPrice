"""
Pipeline Tests
───────────────
Basic tests to verify the end-to-end pipeline works correctly.
"""
import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    TRAIN_PATH, TEST_PATH, FEATURES_PATH, STORES_PATH,
    MODEL_PATH, FEATURE_COLUMNS_PATH,
)


class TestDataLoading:
    """Test that all CSV files load correctly."""

    def test_train_loads(self):
        df = pd.read_csv(TRAIN_PATH)
        assert len(df) > 0, "train.csv is empty"
        assert "Weekly_Sales" in df.columns, "Missing target column"

    def test_test_loads(self):
        df = pd.read_csv(TEST_PATH)
        assert len(df) > 0, "test.csv is empty"
        assert "Weekly_Sales" not in df.columns, "Test should not have target"

    def test_features_loads(self):
        df = pd.read_csv(FEATURES_PATH)
        assert len(df) > 0, "features.csv is empty"
        assert "Temperature" in df.columns

    def test_stores_loads(self):
        df = pd.read_csv(STORES_PATH)
        assert len(df) == 45, f"Expected 45 stores, got {len(df)}"
        assert set(df.columns) == {"Store", "Type", "Size"}

    def test_store_ids_match(self):
        train = pd.read_csv(TRAIN_PATH)
        test = pd.read_csv(TEST_PATH)
        stores = pd.read_csv(STORES_PATH)
        assert set(train["Store"].unique()) == set(stores["Store"].unique())
        assert set(test["Store"].unique()) == set(stores["Store"].unique())


class TestDataMerging:
    """Test that data merging works correctly."""

    def test_merge_preserves_rows(self):
        from src.data_preprocessing import load_all_data, merge_data
        train, _, features, stores = load_all_data()
        merged = merge_data(train, features, stores)
        assert len(merged) == len(train), \
            f"Merge changed row count: {len(train)} -> {len(merged)}"

    def test_merge_adds_columns(self):
        from src.data_preprocessing import load_all_data, merge_data
        train, _, features, stores = load_all_data()
        merged = merge_data(train, features, stores)
        assert "Temperature" in merged.columns
        assert "Size" in merged.columns


class TestFeatureEngineering:
    """Test feature engineering output."""

    def test_temporal_features_created(self):
        from src.data_preprocessing import load_all_data, preprocess
        from src.feature_engineering import prepare_features
        train, _, features, stores = load_all_data()
        processed = preprocess(train, features, stores)
        X, y = prepare_features(processed, is_training=True)

        for col in ["Year", "Month", "WeekOfYear", "DayOfWeek", "Quarter"]:
            assert col in X.columns, f"Missing temporal feature: {col}"

    def test_derived_features_created(self):
        from src.data_preprocessing import load_all_data, preprocess
        from src.feature_engineering import prepare_features
        train, _, features, stores = load_all_data()
        processed = preprocess(train, features, stores)
        X, y = prepare_features(processed, is_training=True)

        assert "TotalMarkDown" in X.columns
        assert "HasMarkDown" in X.columns

    def test_no_target_leakage(self):
        from src.data_preprocessing import load_all_data, preprocess
        from src.feature_engineering import prepare_features
        train, _, features, stores = load_all_data()
        processed = preprocess(train, features, stores)
        X, y = prepare_features(processed, is_training=True)

        assert "Weekly_Sales" not in X.columns, "Target leaked into features!"
        assert "Date" not in X.columns, "Date column should be dropped"

    def test_no_missing_values(self):
        from src.data_preprocessing import load_all_data, preprocess
        from src.feature_engineering import prepare_features
        train, _, features, stores = load_all_data()
        processed = preprocess(train, features, stores)
        X, y = prepare_features(processed, is_training=True)

        assert X.isnull().sum().sum() == 0, \
            f"Features contain missing values: {X.isnull().sum()[X.isnull().sum() > 0]}"


class TestMissingValueHandling:
    """Test missing value handling logic."""

    def test_markdowns_filled(self):
        from src.data_preprocessing import handle_missing_values
        df = pd.DataFrame({
            "Store": [1, 1],
            "MarkDown1": [np.nan, 100],
            "MarkDown2": [np.nan, np.nan],
            "MarkDown3": [50, np.nan],
            "MarkDown4": [np.nan, 200],
            "MarkDown5": [np.nan, np.nan],
        })
        result = handle_missing_values(df)
        assert result["MarkDown1"].iloc[0] == 0
        assert result["MarkDown2"].sum() == 0


class TestModelPipeline:
    """Test model loading and prediction (requires trained model)."""

    @pytest.fixture(autouse=True)
    def skip_if_no_model(self):
        if not os.path.exists(MODEL_PATH):
            pytest.skip("No trained model found. Run src/train.py first.")

    def test_model_loads(self):
        import joblib
        model = joblib.load(MODEL_PATH)
        assert model is not None

    def test_feature_columns_load(self):
        import joblib
        cols = joblib.load(FEATURE_COLUMNS_PATH)
        assert isinstance(cols, list)
        assert len(cols) > 0

    def test_prediction_returns_number(self):
        from src.predict import predict_single
        result = predict_single(
            store=1, dept=1, date="2013-01-04", is_holiday=False,
            temperature=40.0, fuel_price=3.5, cpi=220.0, unemployment=6.5,
        )
        assert isinstance(result, float)

    def test_prediction_reasonable_range(self):
        from src.predict import predict_single
        result = predict_single(
            store=1, dept=1, date="2013-01-04", is_holiday=False,
            temperature=40.0, fuel_price=3.5, cpi=220.0, unemployment=6.5,
        )
        # Weekly sales should be within a reasonable range
        assert -10000 < result < 1000000, \
            f"Prediction ${result} seems unreasonable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
