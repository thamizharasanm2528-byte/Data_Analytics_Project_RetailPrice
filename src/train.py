"""
Model Training Module
----------------------
Trains multiple regression models, performs time-based validation,
evaluates and compares models, selects the best one, and saves it.
"""
import os
import sys
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance

from src.config import (
    RANDOM_STATE, VALIDATION_SPLIT_DATE,
    LINEAR_REGRESSION_PARAMS, RANDOM_FOREST_PARAMS, GRADIENT_BOOSTING_PARAMS,
    MODEL_PATH, FEATURE_COLUMNS_PATH, PREPROCESSOR_PATH,
    FIGURES_DIR, MODELS_DIR,
)
from src.data_preprocessing import get_preprocessed_data
from src.feature_engineering import prepare_features, get_feature_names
from src.evaluate import (
    compare_models, select_best_model, save_comparison,
    plot_model_comparison, plot_actual_vs_predicted, plot_residuals,
)


# --- Baseline Model ----------------------------------------------------------

class NaiveMeanBaseline:
    """
    Predicts the historical mean Weekly_Sales for each (Store, Dept)
    combination. Falls back to the global mean for unseen combinations.
    """
    def __init__(self):
        self.store_dept_means = {}
        self.global_mean = 0

    def fit(self, X, y):
        df = X[["Store", "Dept"]].copy()
        df["target"] = y.values
        self.store_dept_means = df.groupby(["Store", "Dept"])["target"].mean().to_dict()
        self.global_mean = y.mean()
        return self

    def predict(self, X):
        return np.array([
            self.store_dept_means.get((row["Store"], row["Dept"]), self.global_mean)
            for _, row in X[["Store", "Dept"]].iterrows()
        ])


# --- Prediction Functions ----------------------------------------------------

def predict_baseline(model, X):
    return model.predict(X)


def predict_linear(model_tuple, X):
    """Linear regression needs scaled features."""
    model, scaler, feature_cols = model_tuple
    X_scaled = pd.DataFrame(scaler.transform(X[feature_cols]),
                            columns=feature_cols, index=X.index)
    return model.predict(X_scaled)


def predict_tree_model(model, X):
    return model.predict(X)


# --- Time-Based Validation Split ---------------------------------------------

def time_based_split(X, y, date_series, split_date=VALIDATION_SPLIT_DATE):
    """
    Split data chronologically. All rows before split_date go to training,
    the rest to validation.
    """
    split_dt = pd.to_datetime(split_date)
    train_mask = date_series < split_dt
    val_mask = date_series >= split_dt

    X_train, X_val = X[train_mask], X[val_mask]
    y_train, y_val = y[train_mask], y[val_mask]

    print(f"Time-based split at {split_date}:")
    print(f"  Training:   {X_train.shape[0]:,} rows "
          f"({date_series[train_mask].min().date()} -> "
          f"{date_series[train_mask].max().date()})")
    print(f"  Validation: {X_val.shape[0]:,} rows "
          f"({date_series[val_mask].min().date()} -> "
          f"{date_series[val_mask].max().date()})\n")

    return X_train, X_val, y_train, y_val


# --- Training Functions ------------------------------------------------------

def train_all_models(X_train, y_train):
    """
    Train all candidate models and return them in a dict.
    Format: {name: (model_object, predict_function)}
    """
    models = {}

    # 1. Naive Mean Baseline
    print("Training Naive Mean Baseline...")
    baseline = NaiveMeanBaseline()
    baseline.fit(X_train, y_train)
    models["Naive Mean Baseline"] = (baseline, predict_baseline)

    # 2. Linear Regression (with scaling)
    print("Training Linear Regression...")
    feature_cols = [c for c in X_train.columns
                    if c not in ["Store", "Dept"]]
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train[feature_cols]),
        columns=feature_cols, index=X_train.index
    )
    lr = LinearRegression(**LINEAR_REGRESSION_PARAMS)
    lr.fit(X_train_scaled, y_train)
    models["Linear Regression"] = ((lr, scaler, feature_cols), predict_linear)

    # 3. Random Forest
    print("Training Random Forest...")
    rf = RandomForestRegressor(**RANDOM_FOREST_PARAMS)
    rf.fit(X_train, y_train)
    models["Random Forest"] = (rf, predict_tree_model)

    # 4. Histogram Gradient Boosting
    print("Training Gradient Boosting (HistGBR)...")
    hgb = HistGradientBoostingRegressor(**GRADIENT_BOOSTING_PARAMS)
    hgb.fit(X_train, y_train)
    models["Gradient Boosting"] = (hgb, predict_tree_model)

    print(f"\nAll {len(models)} models trained successfully.\n")
    return models


# --- Feature Importance ------------------------------------------------------

def plot_feature_importance(model, feature_names, model_name, save_dir=FIGURES_DIR):
    """
    Plot feature importance for tree-based models.
    Uses built-in feature_importances_ if available.
    """
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        print(f"  {model_name} does not support feature_importances_. Skipping.")
        return

    # Sort by importance
    indices = np.argsort(importances)[::-1]
    top_n = min(20, len(feature_names))
    top_indices = indices[:top_n]

    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, top_n))
    y_pos = range(top_n)

    ax.barh(y_pos, importances[top_indices][::-1], color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([feature_names[i] for i in top_indices][::-1], fontsize=10)
    ax.set_xlabel("Feature Importance", fontsize=12)
    ax.set_title(f"Top {top_n} Feature Importances — {model_name}",
                 fontsize=14, fontweight="bold")

    # Add note about correlation vs causation
    ax.text(0.98, 0.02,
            "Note: Feature importance indicates predictive\n"
            "value, not causal relationship.",
            transform=ax.transAxes, fontsize=8, ha="right", va="bottom",
            style="italic", color="gray",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow",
                      edgecolor="gray", alpha=0.8))

    plt.tight_layout()
    path = os.path.join(save_dir, "feature_importance.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Feature importance plot saved to {os.path.basename(path)}")

    # Print top features
    print(f"\n  Top 10 features for {model_name}:")
    for i in range(min(10, len(feature_names))):
        idx = indices[i]
        print(f"    {i+1}. {feature_names[idx]}: {importances[idx]:.4f}")
    print()


# --- Save Model & Artifacts --------------------------------------------------

def save_final_model(model, feature_columns, scaler=None):
    """Save the final model and associated artifacts."""
    joblib.dump(model, MODEL_PATH)
    print(f"  Model saved to {os.path.basename(MODEL_PATH)}")

    joblib.dump(feature_columns, FEATURE_COLUMNS_PATH)
    print(f"  Feature columns saved to {os.path.basename(FEATURE_COLUMNS_PATH)}")

    if scaler is not None:
        joblib.dump(scaler, PREPROCESSOR_PATH)
        print(f"  Preprocessor saved to {os.path.basename(PREPROCESSOR_PATH)}")


# --- Main Training Pipeline --------------------------------------------------

def run_training_pipeline():
    """Execute the complete training pipeline."""
    print("=" * 70)
    print("AI-POWERED RETAIL SALES ANALYTICS — TRAINING PIPELINE")
    print("=" * 70 + "\n")

    # Step 1: Load and preprocess data
    train_processed, test_processed = get_preprocessed_data()

    # Save the date column before feature engineering drops it
    date_series = train_processed["Date"].copy()

    # Step 2: Feature engineering
    X, y = prepare_features(train_processed, is_training=True)
    feature_names = get_feature_names(X)

    # Step 3: Time-based validation split
    X_train, X_val, y_train, y_val = time_based_split(X, y, date_series)

    # Step 4: Train all models
    models = train_all_models(X_train, y_train)

    # Step 5: Evaluate and compare
    print("Evaluating models on validation set...")
    comparison_df, predictions_dict = compare_models(models, X_val, y_val)

    # Step 6: Save comparison metrics
    save_comparison(comparison_df)
    plot_model_comparison(comparison_df)

    # Step 7: Select best model
    best_name, best_model, best_predict_fn, best_metrics = select_best_model(
        comparison_df, models, primary_metric="RMSE"
    )

    # Step 8: Visualize best model performance
    best_preds = predictions_dict[best_name]
    plot_actual_vs_predicted(y_val, best_preds, best_name)
    plot_residuals(y_val, best_preds, best_name)

    # Step 9: Feature importance for best model
    if best_name in ["Random Forest", "Gradient Boosting"]:
        actual_model = best_model
    elif isinstance(best_model, tuple):
        actual_model = best_model[0]
    else:
        actual_model = best_model
    plot_feature_importance(actual_model, feature_names, best_name)

    # Step 10: Retrain best model on ALL training data for final deployment
    print("-" * 70)
    print(f"Retraining {best_name} on full training data for deployment...")
    print("-" * 70)

    if best_name == "Naive Mean Baseline":
        final_model = NaiveMeanBaseline()
        final_model.fit(X, y)
        save_final_model(final_model, feature_names)

    elif best_name == "Linear Regression":
        _, scaler, feat_cols = best_model
        scaler_full = StandardScaler()
        X_scaled_full = pd.DataFrame(
            scaler_full.fit_transform(X[feat_cols]),
            columns=feat_cols, index=X.index
        )
        lr_final = LinearRegression()
        lr_final.fit(X_scaled_full, y)
        save_final_model(lr_final, feature_names, scaler=scaler_full)

    elif best_name == "Random Forest":
        rf_final = RandomForestRegressor(**RANDOM_FOREST_PARAMS)
        rf_final.fit(X, y)
        save_final_model(rf_final, feature_names)

    elif best_name == "Gradient Boosting":
        hgb_final = HistGradientBoostingRegressor(**GRADIENT_BOOSTING_PARAMS)
        hgb_final.fit(X, y)
        save_final_model(hgb_final, feature_names)

    # Step 11: Generate test predictions
    print("\nGenerating predictions for test set...")
    X_test, _ = prepare_features(test_processed, is_training=False)

    # Ensure test has same columns as training
    for col in feature_names:
        if col not in X_test.columns:
            X_test[col] = 0
    X_test = X_test[feature_names]

    final_model = joblib.load(MODEL_PATH)

    if best_name == "Linear Regression":
        scaler_loaded = joblib.load(PREPROCESSOR_PATH)
        feat_cols = [c for c in feature_names if c not in ["Store", "Dept"]]
        X_test_scaled = pd.DataFrame(
            scaler_loaded.transform(X_test[feat_cols]),
            columns=feat_cols, index=X_test.index
        )
        test_preds = final_model.predict(X_test_scaled)
    else:
        test_preds = final_model.predict(X_test)

    # Save predictions
    from src.config import TEST_PREDICTIONS_PATH
    pred_df = test_processed[["Store", "Dept", "Date"]].copy()
    pred_df["Predicted_Weekly_Sales"] = test_preds
    pred_df.to_csv(TEST_PREDICTIONS_PATH, index=False)
    print(f"  Test predictions saved ({len(pred_df):,} rows)")

    print("\n" + "=" * 70)
    print("TRAINING PIPELINE COMPLETE")
    print("=" * 70)
    print(f"\nFinal model: {best_name}")
    print(f"Validation MAE:  ${best_metrics['MAE']:,.2f}")
    print(f"Validation RMSE: ${best_metrics['RMSE']:,.2f}")
    print(f"Validation R²:   {best_metrics['R2']}")
    print(f"Validation MAPE: {best_metrics['MAPE']}%")

    return best_name, best_metrics


if __name__ == "__main__":
    run_training_pipeline()
