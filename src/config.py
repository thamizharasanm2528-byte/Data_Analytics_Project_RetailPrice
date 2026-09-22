"""
Central configuration for the Retail Sales Analytics project.
All paths, constants, and hyperparameters are defined here.
"""
import os

# --- Project Root -------------------------------------------------------------
# Determine project root dynamically (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Data Paths ---------------------------------------------------------------
TRAIN_PATH = os.path.join(PROJECT_ROOT, "train.csv")
TEST_PATH = os.path.join(PROJECT_ROOT, "test.csv")
FEATURES_PATH = os.path.join(PROJECT_ROOT, "features.csv")
STORES_PATH = os.path.join(PROJECT_ROOT, "stores.csv")
SAMPLE_SUBMISSION_PATH = os.path.join(PROJECT_ROOT, "sampleSubmission.csv")

# --- Output Paths -------------------------------------------------------------
FIGURES_DIR = os.path.join(PROJECT_ROOT, "outputs", "figures")
METRICS_DIR = os.path.join(PROJECT_ROOT, "outputs", "metrics")
PREDICTIONS_DIR = os.path.join(PROJECT_ROOT, "outputs", "predictions")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

MODEL_PATH = os.path.join(MODELS_DIR, "final_model.pkl")
FEATURE_COLUMNS_PATH = os.path.join(MODELS_DIR, "feature_columns.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.pkl")
MODEL_COMPARISON_PATH = os.path.join(METRICS_DIR, "model_comparison.csv")
TEST_PREDICTIONS_PATH = os.path.join(PREDICTIONS_DIR, "test_predictions.csv")

# --- Random Seed --------------------------------------------------------------
RANDOM_STATE = 42

# --- Merge Keys ---------------------------------------------------------------
MERGE_KEYS_FEATURES = ["Store", "Date", "IsHoliday"]
MERGE_KEYS_STORES = ["Store"]

# --- Feature Lists ------------------------------------------------------------
MARKDOWN_COLS = ["MarkDown1", "MarkDown2", "MarkDown3", "MarkDown4", "MarkDown5"]
EXTERNAL_FEATURES = ["Temperature", "Fuel_Price", "CPI", "Unemployment"]
TEMPORAL_FEATURES = ["Year", "Month", "WeekOfYear", "DayOfWeek", "Quarter",
                     "IsMonthStart", "IsMonthEnd"]
DERIVED_FEATURES = ["TotalMarkDown", "HasMarkDown"]
STORE_FEATURES = ["Type_encoded", "Size"]

TARGET_COL = "Weekly_Sales"

# --- Validation Split ---------------------------------------------------------
# Time-based split: ~85% train, ~15% validation
VALIDATION_SPLIT_DATE = "2012-07-01"

# --- Model Hyperparameters ----------------------------------------------------
LINEAR_REGRESSION_PARAMS = {}  # Default sklearn params

RANDOM_FOREST_PARAMS = {
    "n_estimators": 100,
    "max_depth": 15,
    "min_samples_leaf": 5,
    "n_jobs": -1,
    "random_state": RANDOM_STATE,
}

GRADIENT_BOOSTING_PARAMS = {
    "max_iter": 200,
    "max_depth": 6,
    "learning_rate": 0.1,
    "random_state": RANDOM_STATE,
}

# --- MAPE Threshold ----------------------------------------------------------
# Exclude rows where |actual| < this value when computing MAPE
MAPE_MIN_THRESHOLD = 100

# --- Ensure output directories exist -----------------------------------------
for _dir in [FIGURES_DIR, METRICS_DIR, PREDICTIONS_DIR, MODELS_DIR]:
    os.makedirs(_dir, exist_ok=True)
