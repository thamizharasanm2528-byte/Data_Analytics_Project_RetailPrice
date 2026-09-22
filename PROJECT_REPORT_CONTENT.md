# PROJECT REPORT: AI-Powered Retail Sales Analytics and Sales Prediction

## 1. Introduction

This project applies machine learning to predict weekly retail sales for Walmart stores. Using historical data from 45 stores and 81 departments (Feb 2010 - Oct 2012), we built and compared 5 regression models to forecast future weekly sales per store-department combination.

**Domain:** Data Analytics using AI  
**Dataset:** Walmart Store Sales Forecasting (Kaggle)

## 2. Problem Statement

Given historical weekly sales with external features (temperature, fuel price, CPI, unemployment, promotional markdowns), predict future weekly sales for each store-department. This is a regression problem with a temporal dimension requiring time-based validation to avoid data leakage.

## 3. Objectives

1. Perform comprehensive EDA to understand sales patterns and seasonality
2. Build a reproducible ML pipeline with proper time-based validation
3. Compare 5 regression models objectively using consistent metrics
4. Generate predictions for the test dataset
5. Create an interactive Streamlit dashboard for stakeholders
6. Extract data-driven business insights

## 4. Dataset Description

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| train.csv | 421,570 | 5 | Historical weekly sales |
| test.csv | 115,064 | 4 | Future weeks for prediction |
| features.csv | 8,190 | 12 | Store-level weekly features |
| stores.csv | 45 | 3 | Store metadata |
| sampleSubmission.csv | 115,064 | 2 | Expected output format |

**Target variable:** `Weekly_Sales` (range: -$4,988 to $693,099)

## 5. Methodology

### 5.1 Data Preprocessing
- Schema validation of all CSV files
- Date parsing to datetime format
- Missing value handling: MarkDown1-5 filled with 0, CPI/Unemployment forward-filled per store
- Categorical encoding: Store Type (A=2, B=1, C=0)
- Merge train/test with features and stores datasets

### 5.2 Feature Engineering
- **Temporal features:** Year, Month, WeekOfYear, DayOfWeek, Quarter, IsMonthStart, IsMonthEnd
- **Derived features:** TotalMarkDown, HasMarkDown
- **Data leakage prevention:** Time-based validation split at 2012-07-01
- **Total features:** 23

### 5.3 Models Trained
1. Naive Mean Baseline (store-department average)
2. Linear Regression (with standard scaling)
3. Random Forest Regressor (100 trees, max_depth=15)
4. HistGradientBoostingRegressor (200 iterations, max_depth=6)
5. XGBRegressor (200 estimators, max_depth=8)

## 6. Results

### Model Comparison (Time-Based Validation)

| Model | MAE ($) | RMSE ($) | R-squared | MAPE (%) |
|-------|---------|----------|-----------|----------|
| Naive Mean Baseline | 2,495 | 5,081 | 0.9465 | 39.8 |
| Linear Regression | 14,640 | 20,963 | 0.0893 | 711.4 |
| **Random Forest** | **2,076** | **4,005** | **0.9668** | **29.8** |
| HistGradientBoosting | 3,516 | 5,860 | 0.9288 | 105.6 |
| XGBoost | 2,548 | 4,261 | 0.9624 | 71.9 |

### Final Model: Random Forest
- Selected programmatically by lowest RMSE
- Explains 96.7% of sales variance
- Average prediction error: $2,076 per store-department per week

### Top Predictive Features
Department, Store Size, Store ID, WeekOfYear, and CPI were the most important features based on permutation importance.

## 7. Key Business Insights

1. **Store 20** generated the highest historical sales
2. **Department 92** leads in total sales
3. **Holiday weeks** showed ~7% higher average sales
4. **November/December** are peak sales months (holiday shopping)
5. **Store size** has a strong positive correlation with average sales
6. **Type A stores** (largest) consistently outperform others
7. **Markdowns** showed modest +1.9% average sales effect
8. **External factors** (Temperature, CPI, etc.) showed weak direct correlations

## 8. Deliverables

| Deliverable | Location |
|-------------|----------|
| Analysis Notebook | `notebooks/retail_sales_analysis.ipynb` |
| Trained Model | `models/final_model.pkl` |
| Test Predictions | `outputs/predictions/Walmart_Sales_Predictions.csv` |
| Submission File | `outputs/predictions/walmart_submission.csv` |
| Interactive Dashboard | `app/app.py` (Streamlit) |
| Model Comparison | `outputs/metrics/model_comparison.csv` |
| EDA Visualizations | `outputs/figures/` |

## 9. Limitations

- Weekly granularity limits daily-level insights
- MarkDown data missing for ~50-64% of early records
- External factors showed weak direct correlation with sales
- Model cannot extrapolate beyond training data range
- No causal analysis performed; findings are correlational

## 10. Future Scope

- Time-series specific models (Prophet, LSTM)
- Store-specific or department-specific models
- Additional data sources (weather events, demographics)
- Hyperparameter tuning with Bayesian optimization
- Real-time forecasting service with automated retraining
- Confidence intervals on predictions

## 11. Technologies Used

Python, pandas, NumPy, scikit-learn, XGBoost, matplotlib, seaborn, Plotly, Streamlit, joblib

## 12. How to Run

```bash
pip install -r requirements.txt
python -m src.train           # Train models
streamlit run app/app.py      # Launch dashboard
python -m pytest tests/ -v    # Run tests
```
