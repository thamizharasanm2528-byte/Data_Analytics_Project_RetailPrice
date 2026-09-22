# AI-Powered Retail Sales Analytics and Sales Prediction

A complete machine learning system for predicting weekly retail sales using the Walmart Store Sales Forecasting dataset. Built as an internship project demonstrating **Data Analytics + AI/ML + Interactive Dashboard** capabilities.

---

## Project Overview

Retail businesses need accurate weekly sales forecasts to optimize inventory, staffing, and promotional strategies. This project:

1. **Analyzes** historical sales data across 45 stores and 81 departments
2. **Identifies** seasonal patterns, holiday effects, and external factor relationships
3. **Trains** multiple ML models and selects the best performer via time-based validation
4. **Predicts** weekly sales for any store-department-date combination
5. **Visualizes** insights through an interactive Streamlit dashboard

## Problem Statement

Given historical weekly sales data from 45 Walmart stores (each with multiple departments), along with external features (temperature, fuel price, CPI, unemployment, and promotional markdowns), predict future weekly sales per store-department.

## Objectives

- Perform comprehensive EDA to understand sales patterns
- Build a reproducible ML pipeline with proper time-based validation
- Compare multiple regression models objectively
- Create an interactive dashboard for business stakeholders
- Generate automated, data-driven business insights

---

## Dataset Description

| File | Rows | Columns | Description |
|------|------|---------|-------------|
| `train.csv` | 421,570 | 5 | Historical weekly sales (Feb 2010 - Oct 2012) |
| `test.csv` | 115,064 | 4 | Future weeks for prediction (Nov 2012 - Jul 2013) |
| `features.csv` | 8,190 | 12 | Store-level weekly features |
| `stores.csv` | 45 | 3 | Store metadata (type & size) |

**Target variable:** `Weekly_Sales` (float, range: -$4,988 to $693,099)

**Key features:** Store, Department, Date, Temperature, Fuel_Price, MarkDown1-5, CPI, Unemployment, IsHoliday, Store Type, Store Size

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| Python 3.10+ | Core language |
| pandas | Data manipulation |
| NumPy | Numerical operations |
| scikit-learn | ML models & metrics |
| matplotlib & seaborn | Static visualizations |
| Plotly | Interactive charts |
| Streamlit | Dashboard framework |
| XGBoost | Gradient boosting |
| joblib | Model serialization |
| pytest | Testing |

---

## Project Architecture

```
walmart-recruiting-store-sales-forecasting/
|
|-- train.csv, test.csv, features.csv, stores.csv
|
|-- src/
|   |-- config.py                # Central configuration
|   |-- data_preprocessing.py    # Load, merge, clean, encode
|   |-- feature_engineering.py   # Temporal + derived features
|   |-- eda.py                   # Exploratory Data Analysis
|   |-- train.py                 # Train + evaluate + save models
|   |-- evaluate.py              # Metrics + comparison
|   |-- predict.py               # Prediction pipeline
|
|-- models/
|   |-- final_model.pkl
|   |-- feature_columns.pkl
|
|-- outputs/
|   |-- figures/                 # 13 EDA + model visualizations
|   |-- metrics/model_comparison.csv
|   |-- predictions/test_predictions.csv
|
|-- app/app.py                   # Streamlit dashboard
|-- tests/test_pipeline.py       # 16 pipeline tests
|-- requirements.txt
|-- IMPLEMENTATION_PLAN.md
|-- README.md
```

---

## Data Preprocessing

1. **Schema validation** for all CSV files
2. **Date parsing** to datetime
3. **Merging** train/test + features (on Store, Date, IsHoliday) + stores (on Store)
4. **Missing values:**
   - MarkDown1-5: filled with 0 (no promotion = no markdown)
   - CPI/Unemployment: forward-fill then backward-fill per store
5. **Categorical encoding:** Store Type (A=2, B=1, C=0), IsHoliday (0/1)
6. **No outlier removal** -- negative sales (returns) and extreme positives (holidays) are valid business data

## Exploratory Data Analysis

10 professional visualizations covering:
- Sales distribution (histogram + box plot)
- Weekly/monthly sales trends
- Seasonal patterns by week-of-year
- Store performance (top/bottom, by type, size vs sales)
- Department rankings
- Holiday vs non-holiday impact (+7.1% holiday premium)
- External factors (Temperature, Fuel, CPI, Unemployment)
- Correlation heatmap
- Store size vs sales relationship

## Feature Engineering

**Temporal features:** Year, Month, WeekOfYear, DayOfWeek, Quarter, IsMonthStart, IsMonthEnd

**Derived features:** TotalMarkDown, HasMarkDown

**Data leakage prevention:** No future data used; time-based validation split at 2012-07-01

---

## Machine Learning Models

### Model Comparison (Time-Based Validation)

| Model | MAE | RMSE | R-squared | MAPE |
|-------|-----|------|----|------|
| Naive Mean Baseline | $2,495 | $5,081 | 0.9465 | 39.8% |
| Linear Regression | $14,640 | $20,963 | 0.0893 | 711.4% |
| **Random Forest** | **$2,076** | **$4,005** | **0.9668** | **29.8%** |
| Gradient Boosting | $3,516 | $5,860 | 0.9288 | 105.6% |
| XGBoost | $2,548 | $4,261 | 0.9624 | 71.9% |

### Final Model: Random Forest

- **Selected by:** Lowest RMSE on time-based validation set
- **R-squared:** 0.9668 (explains 96.7% of variance)
- **MAE:** $2,076 average error per prediction
- **Top features:** Department (64.7%), Store Size (19.1%), Store (5.3%), WeekOfYear (3.8%)

### Why Not Other Models?

- **Linear Regression** failed badly (R-squared=0.06) because the relationships are highly non-linear
- **Gradient Boosting** underperformed Random Forest here, likely due to hyperparameter sensitivity and the high-cardinality of Store/Dept features
- **Naive Mean Baseline** was surprisingly strong, confirming that store-department identity is the dominant predictor

---

## Evaluation Metrics

| Metric | Meaning |
|--------|---------|
| MAE | Average dollar error per prediction |
| RMSE | Penalizes large errors more heavily |
| R-squared | Proportion of variance explained (0-1) |
| MAPE | Percentage error (rows with |actual| < $100 excluded) |

---

## Dashboard

Interactive Streamlit dashboard with 8 pages:

1. **Overview** -- KPI cards + quick charts
2. **Sales Trends** -- Weekly, monthly, seasonal tabs
3. **Store Analysis** -- Rankings + size vs sales scatter
4. **Department Analysis** -- Top 20 departments
5. **Holiday Impact** -- Holiday vs non-holiday comparison
6. **Model Performance** -- Metrics table + comparison charts + feature importance
7. **Predict Sales** -- Input form with real-time prediction
8. **Business Insights** -- Auto-generated data-driven insights

---

## How to Install

```bash
# Clone or download the project
cd walmart-recruiting-store-sales-forecasting

# Install dependencies
pip install -r requirements.txt
```

## How to Run

### 1. Train the model
```bash
python -m src.train
```

### 2. Run EDA (generates visualizations)
```bash
python -m src.eda
```

### 3. Launch the dashboard
```bash
streamlit run app/app.py
```

### 4. Run tests
```bash
python -m pytest tests/test_pipeline.py -v
```

### 5. Make a prediction from CLI
```bash
python -m src.predict
```

### 6. Run Jupyter Analysis Notebook
Open and run `notebooks/Thamizharasan_AI-Powered_Retail_Sales_Analytics_and_Sales_Prediction.ipynb` in VS Code or JupyterLab.

---

## Example Prediction

```
Store 1, Dept 1, Date 2013-01-04:
  Predicted Weekly Sales: $15,432.50
  Historical Average: $19,247.33
```

---

## Business Insights

- **Store 20** generated the highest historical sales of $301M
- **Department 92** is the top performer with $484M in total sales
- **Holiday weeks** show +7.1% higher average sales ($17,036 vs $15,901)
- **Sales peak in November-December** due to holiday shopping
- **Store size** has a positive correlation (0.79) with average sales
- **Markdowns** show +1.9% effect on average weekly sales

---

## Limitations

- Model uses aggregate weekly data; daily granularity could improve accuracy
- Markdown data is missing for 50-64% of records (pre-2011)
- External factors (Temperature, CPI, etc.) show weak direct correlation with sales
- Model does not account for competition, store renovations, or new product launches
- Random Forest does not extrapolate well beyond training data range

## Future Improvements

- Add LSTM/Prophet for time-series specific modeling
- Incorporate additional external data (weather events, local events)
- Implement store-specific or department-specific models
- Add real-time data ingestion pipeline
- Deploy as a cloud-hosted web application
- Add A/B testing framework for promotional strategies

---

## License

This project is for educational and internship demonstration purposes.

Dataset source: [Walmart Recruiting - Store Sales Forecasting (Kaggle)](https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting)
