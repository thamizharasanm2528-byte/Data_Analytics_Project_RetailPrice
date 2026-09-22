"""
Model Evaluation Module
------------------------
Computes metrics (MAE, RMSE, R², MAPE), creates comparison
tables, and generates evaluation visualizations.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.config import MAPE_MIN_THRESHOLD, METRICS_DIR, FIGURES_DIR, MODEL_COMPARISON_PATH


def compute_mape(y_true, y_pred, threshold=MAPE_MIN_THRESHOLD):
    """
    Compute Mean Absolute Percentage Error, excluding rows
    where |y_true| < threshold to avoid division-by-near-zero.

    Returns (mape_value, n_excluded).
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    mask = np.abs(y_true) >= threshold
    n_excluded = (~mask).sum()

    if mask.sum() == 0:
        return np.nan, n_excluded

    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
    return mape, n_excluded


def compute_metrics(y_true, y_pred):
    """
    Compute all evaluation metrics for a single model.

    Returns a dict with MAE, RMSE, R2, MAPE, and MAPE_excluded_count.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape, n_excluded = compute_mape(y_true, y_pred)

    return {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "R2": round(r2, 4),
        "MAPE": round(mape, 2) if not np.isnan(mape) else "N/A",
        "MAPE_excluded_count": int(n_excluded),
    }


def compare_models(models_dict, X_val, y_val):
    """
    Evaluate multiple models on the validation set and create
    a comparison DataFrame.

    Parameters
    ----------
    models_dict : dict
        {model_name: (model_object, predict_fn)} where predict_fn
        takes (model, X) and returns predictions.
    X_val : pd.DataFrame
        Validation features.
    y_val : pd.Series
        Validation target.

    Returns
    -------
    comparison_df : pd.DataFrame
        Model comparison table.
    predictions_dict : dict
        {model_name: y_pred} for further analysis.
    """
    results = []
    predictions_dict = {}

    for name, (model, predict_fn) in models_dict.items():
        print(f"  Evaluating: {name}...")
        y_pred = predict_fn(model, X_val)
        metrics = compute_metrics(y_val, y_pred)
        metrics["Model"] = name
        results.append(metrics)
        predictions_dict[name] = y_pred

    comparison_df = pd.DataFrame(results)
    comparison_df = comparison_df[["Model", "MAE", "RMSE", "R2", "MAPE"]]

    print(f"\n{'-'*70}")
    print("MODEL COMPARISON (Validation Set)")
    print(f"{'-'*70}")
    print(comparison_df.to_string(index=False))
    print(f"{'-'*70}\n")

    return comparison_df, predictions_dict


def select_best_model(comparison_df, models_dict, primary_metric="RMSE"):
    """
    Select the best model based on the primary metric.
    For RMSE and MAE: lower is better.
    For R2: higher is better.
    """
    df = comparison_df.copy()

    if primary_metric in ["RMSE", "MAE"]:
        best_idx = df[primary_metric].astype(float).idxmin()
    else:
        best_idx = df[primary_metric].astype(float).idxmax()

    best_name = df.loc[best_idx, "Model"]
    best_metrics = df.loc[best_idx].to_dict()

    print(f"Best model (by {primary_metric}): {best_name}")
    print(f"  MAE:  {best_metrics['MAE']}")
    print(f"  RMSE: {best_metrics['RMSE']}")
    print(f"  R²:   {best_metrics['R2']}")
    print(f"  MAPE: {best_metrics['MAPE']}%\n")

    best_model, best_predict_fn = models_dict[best_name]
    return best_name, best_model, best_predict_fn, best_metrics


def save_comparison(comparison_df, path=MODEL_COMPARISON_PATH):
    """Save model comparison to CSV."""
    comparison_df.to_csv(path, index=False)
    print(f"  Model comparison saved to {os.path.basename(path)}")


def plot_model_comparison(comparison_df, save_dir=FIGURES_DIR):
    """Create bar charts comparing model metrics."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    models = comparison_df["Model"].tolist()
    x = range(len(models))
    colors = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]

    # MAE
    axes[0].bar(x, comparison_df["MAE"].astype(float), color=colors[:len(models)])
    axes[0].set_title("Mean Absolute Error (MAE)", fontsize=13, fontweight="bold")
    axes[0].set_ylabel("MAE ($)")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(models, rotation=15, ha="right", fontsize=9)

    # RMSE
    axes[1].bar(x, comparison_df["RMSE"].astype(float), color=colors[:len(models)])
    axes[1].set_title("Root Mean Squared Error (RMSE)", fontsize=13, fontweight="bold")
    axes[1].set_ylabel("RMSE ($)")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(models, rotation=15, ha="right", fontsize=9)

    # R²
    axes[2].bar(x, comparison_df["R2"].astype(float), color=colors[:len(models)])
    axes[2].set_title("R² Score", fontsize=13, fontweight="bold")
    axes[2].set_ylabel("R²")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(models, rotation=15, ha="right", fontsize=9)
    axes[2].set_ylim(0, 1.05)

    plt.tight_layout()
    path = os.path.join(save_dir, "model_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Model comparison chart saved to {os.path.basename(path)}")


def plot_actual_vs_predicted(y_true, y_pred, model_name, save_dir=FIGURES_DIR):
    """Scatter plot of actual vs predicted values."""
    fig, ax = plt.subplots(figsize=(8, 8))

    # Sample for performance (plot at most 10k points)
    n = len(y_true)
    if n > 10000:
        idx = np.random.RandomState(42).choice(n, 10000, replace=False)
        y_true_s = np.array(y_true)[idx]
        y_pred_s = np.array(y_pred)[idx]
    else:
        y_true_s = np.array(y_true)
        y_pred_s = np.array(y_pred)

    ax.scatter(y_true_s, y_pred_s, alpha=0.15, s=5, color="#2196F3")
    min_val = min(y_true_s.min(), y_pred_s.min())
    max_val = max(y_true_s.max(), y_pred_s.max())
    ax.plot([min_val, max_val], [min_val, max_val], "r--", lw=1.5,
            label="Perfect Prediction")
    ax.set_xlabel("Actual Weekly Sales ($)", fontsize=12)
    ax.set_ylabel("Predicted Weekly Sales ($)", fontsize=12)
    ax.set_title(f"Actual vs Predicted — {model_name}", fontsize=14,
                 fontweight="bold")
    ax.legend()
    plt.tight_layout()

    path = os.path.join(save_dir, "actual_vs_predicted.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Actual vs Predicted plot saved to {os.path.basename(path)}")


def plot_residuals(y_true, y_pred, model_name, save_dir=FIGURES_DIR):
    """Histogram of residuals."""
    residuals = np.array(y_true) - np.array(y_pred)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(residuals, bins=80, color="#4CAF50", edgecolor="white", alpha=0.8)
    ax.axvline(0, color="red", linestyle="--", linewidth=1.5)
    ax.set_xlabel("Residual (Actual - Predicted) ($)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title(f"Residual Distribution — {model_name}", fontsize=14,
                 fontweight="bold")
    plt.tight_layout()

    path = os.path.join(save_dir, "residuals.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Residual plot saved to {os.path.basename(path)}")
