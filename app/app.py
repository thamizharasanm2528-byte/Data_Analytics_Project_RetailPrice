"""
AI-Powered Retail Sales Analytics Dashboard
=============================================
Streamlit dashboard for interactive sales analysis and prediction.
"""
import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.config import (
    TRAIN_PATH, FEATURES_PATH, STORES_PATH,
    MODEL_PATH, FEATURE_COLUMNS_PATH, PREPROCESSOR_PATH,
    FIGURES_DIR, MODEL_COMPARISON_PATH, TARGET_COL,
)

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI-Powered Retail Sales Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1565C0, #7B1FA2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #888;
        margin-bottom: 2rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid #475569;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-top: 0.3rem;
    }
    .insight-box {
        background: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Data Loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    """Load and preprocess data for the dashboard."""
    train = pd.read_csv(TRAIN_PATH)
    train["Date"] = pd.to_datetime(train["Date"])
    features = pd.read_csv(FEATURES_PATH)
    features["Date"] = pd.to_datetime(features["Date"])
    stores = pd.read_csv(STORES_PATH)

    # Merge
    merged = train.merge(features, on=["Store", "Date", "IsHoliday"], how="left")
    merged = merged.merge(stores, on="Store", how="left")

    return train, features, stores, merged


@st.cache_resource
def load_model():
    """Load the trained model."""
    if not os.path.exists(MODEL_PATH):
        return None, None, None
    model = joblib.load(MODEL_PATH)
    feature_cols = joblib.load(FEATURE_COLUMNS_PATH)
    scaler = None
    if os.path.exists(PREPROCESSOR_PATH):
        scaler = joblib.load(PREPROCESSOR_PATH)
    return model, feature_cols, scaler


@st.cache_data
def load_model_comparison():
    """Load model comparison metrics."""
    if os.path.exists(MODEL_COMPARISON_PATH):
        return pd.read_csv(MODEL_COMPARISON_PATH)
    return None


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def render_kpi(label, value, icon=""):
    """Render a styled KPI card."""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{icon} {value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def make_prediction(model, feature_cols, scaler, input_dict, stores_df):
    """Run prediction for given inputs."""
    from src.feature_engineering import create_temporal_features, create_derived_features

    df = pd.DataFrame([input_dict])
    df["Date"] = pd.to_datetime(df["Date"])

    # Add store info
    store_info = stores_df[stores_df["Store"] == input_dict["Store"]]
    if len(store_info) > 0:
        type_map = {"A": 2, "B": 1, "C": 0}
        df["Type_encoded"] = type_map.get(store_info.iloc[0]["Type"], 1)
        df["Size"] = store_info.iloc[0]["Size"]
    else:
        df["Type_encoded"] = 1
        df["Size"] = 130000

    df["IsHoliday"] = int(df["IsHoliday"].iloc[0])

    # Feature engineering
    df = create_temporal_features(df)
    df = create_derived_features(df)
    df = df.drop(columns=["Date"], errors="ignore")

    # Align columns
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_cols]

    # Scale if needed
    if scaler is not None:
        non_id_cols = [c for c in feature_cols if c not in ["Store", "Dept"]]
        df[non_id_cols] = scaler.transform(df[non_id_cols])

    prediction = model.predict(df)[0]
    return round(prediction, 2)


def generate_insights(merged):
    """Generate data-driven business insights."""
    insights = []

    # Best store
    store_sales = merged.groupby("Store")[TARGET_COL].sum().sort_values(ascending=False)
    best_store = store_sales.index[0]
    best_store_sales = store_sales.iloc[0]
    insights.append(
        f"Store {best_store} generated the highest historical sales "
        f"of ${best_store_sales:,.0f}."
    )

    # Best department
    dept_sales = merged.groupby("Dept")[TARGET_COL].sum().sort_values(ascending=False)
    best_dept = dept_sales.index[0]
    insights.append(
        f"Department {best_dept} is the top-performing department "
        f"with ${dept_sales.iloc[0]:,.0f} in total sales."
    )

    # Holiday impact
    hol_avg = merged[merged["IsHoliday"] == True][TARGET_COL].mean()
    non_hol_avg = merged[merged["IsHoliday"] == False][TARGET_COL].mean()
    pct = ((hol_avg - non_hol_avg) / non_hol_avg) * 100
    insights.append(
        f"Holiday weeks show {pct:+.1f}% higher average sales "
        f"(${hol_avg:,.0f} vs ${non_hol_avg:,.0f})."
    )

    # Seasonal peak
    monthly = merged.groupby(merged["Date"].dt.month)[TARGET_COL].mean()
    peak_month = monthly.idxmax()
    month_names = {1: "January", 2: "February", 3: "March", 4: "April",
                   5: "May", 6: "June", 7: "July", 8: "August",
                   9: "September", 10: "October", 11: "November", 12: "December"}
    insights.append(
        f"Sales peak in {month_names.get(peak_month, peak_month)} "
        f"with an average of ${monthly.max():,.0f} per week."
    )

    # Store size relationship
    if "Size" in merged.columns:
        store_info = merged.groupby("Store").agg({
            TARGET_COL: "mean", "Size": "first"
        })
        corr = store_info["Size"].corr(store_info[TARGET_COL])
        if abs(corr) > 0.3:
            direction = "positive" if corr > 0 else "negative"
            insights.append(
                f"Store size shows a {direction} correlation ({corr:.2f}) "
                f"with average weekly sales."
            )

    # Worst performing store
    worst_store = store_sales.index[-1]
    insights.append(
        f"Store {worst_store} has the lowest total sales at "
        f"${store_sales.iloc[-1]:,.0f} -- it may need strategic review."
    )

    # Markdown effect
    md_cols = [c for c in merged.columns if "MarkDown" in c and c != "TotalMarkDown"]
    if md_cols:
        has_md = merged[md_cols].fillna(0).sum(axis=1) > 0
        md_avg = merged[has_md][TARGET_COL].mean()
        no_md_avg = merged[~has_md][TARGET_COL].mean()
        md_pct = ((md_avg - no_md_avg) / no_md_avg) * 100
        insights.append(
            f"Weeks with active markdowns show {md_pct:+.1f}% "
            f"difference in average sales compared to non-markdown weeks."
        )

    return insights


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------
def main():
    # Load data
    train, features, stores, merged = load_data()
    model, feature_cols, scaler = load_model()
    comparison_df = load_model_comparison()

    # Header
    st.markdown('<div class="main-header">AI-Powered Retail Sales Analytics</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Walmart Store Sales Forecasting | '
                'Interactive Dashboard</div>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Overview", "Sales Trends", "Store Analysis",
         "Department Analysis", "Holiday Impact",
         "Model Performance", "Predict Sales", "Business Insights"],
        index=0,
    )

    # ===================================================================
    # PAGE: Overview
    # ===================================================================
    if page == "Overview":
        st.header("Key Performance Indicators")

        total_sales = merged[TARGET_COL].sum()
        avg_sales = merged[TARGET_COL].mean()
        n_stores = merged["Store"].nunique()
        n_depts = merged["Dept"].nunique()
        best_store = merged.groupby("Store")[TARGET_COL].sum().idxmax()
        best_dept = merged.groupby("Dept")[TARGET_COL].sum().idxmax()

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1:
            render_kpi("Total Sales", f"${total_sales/1e9:.2f}B", "💰")
        with c2:
            render_kpi("Avg Weekly Sales", f"${avg_sales:,.0f}", "📊")
        with c3:
            render_kpi("Number of Stores", f"{n_stores}", "🏪")
        with c4:
            render_kpi("Departments", f"{n_depts}", "📦")
        with c5:
            render_kpi("Best Store", f"#{best_store}", "🏆")
        with c6:
            render_kpi("Best Dept", f"#{best_dept}", "⭐")

        st.markdown("---")

        # Quick charts
        col1, col2 = st.columns(2)

        with col1:
            weekly = merged.groupby("Date")[TARGET_COL].sum().reset_index()
            fig = px.line(weekly, x="Date", y=TARGET_COL,
                          title="Total Weekly Sales Over Time",
                          labels={TARGET_COL: "Total Sales ($)", "Date": "Date"})
            fig.update_traces(line_color="#38bdf8")
            fig.update_layout(template="plotly_dark",
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width='stretch')

        with col2:
            # Sales by store type
            type_sales = merged.groupby("Type")[TARGET_COL].mean().reset_index()
            fig = px.bar(type_sales, x="Type", y=TARGET_COL,
                         title="Average Sales by Store Type",
                         labels={TARGET_COL: "Avg Sales ($)", "Type": "Store Type"},
                         color="Type",
                         color_discrete_sequence=["#38bdf8", "#fbbf24", "#f87171"])
            fig.update_layout(template="plotly_dark",
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)",
                              showlegend=False)
            st.plotly_chart(fig, width='stretch')

    # ===================================================================
    # PAGE: Sales Trends
    # ===================================================================
    elif page == "Sales Trends":
        st.header("Sales Trends Analysis")

        tab1, tab2, tab3 = st.tabs(["Weekly", "Monthly", "Seasonal"])

        with tab1:
            weekly = merged.groupby("Date")[TARGET_COL].sum().reset_index()
            fig = px.line(weekly, x="Date", y=TARGET_COL,
                          title="Weekly Total Sales",
                          labels={TARGET_COL: "Total Sales ($)"})
            fig.update_traces(line_color="#38bdf8")
            fig.update_layout(template="plotly_dark",
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width='stretch')

        with tab2:
            merged_m = merged.copy()
            merged_m["YearMonth"] = merged_m["Date"].dt.to_period("M").astype(str)
            monthly = merged_m.groupby("YearMonth")[TARGET_COL].sum().reset_index()
            fig = px.bar(monthly, x="YearMonth", y=TARGET_COL,
                         title="Monthly Total Sales",
                         labels={TARGET_COL: "Total Sales ($)",
                                 "YearMonth": "Month"})
            fig.update_traces(marker_color="#fbbf24")
            fig.update_layout(template="plotly_dark",
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)",
                              xaxis_tickangle=-45)
            st.plotly_chart(fig, width='stretch')

        with tab3:
            merged_s = merged.copy()
            merged_s["WeekOfYear"] = merged_s["Date"].dt.isocalendar().week.astype(int)
            seasonal = merged_s.groupby("WeekOfYear")[TARGET_COL].mean().reset_index()
            fig = px.line(seasonal, x="WeekOfYear", y=TARGET_COL,
                          title="Average Sales by Week of Year (Seasonal Pattern)",
                          labels={TARGET_COL: "Avg Sales ($)",
                                  "WeekOfYear": "Week of Year"})
            fig.update_traces(line_color="#a78bfa", line_width=2.5)
            fig.update_layout(template="plotly_dark",
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width='stretch')

    # ===================================================================
    # PAGE: Store Analysis
    # ===================================================================
    elif page == "Store Analysis":
        st.header("Store Performance Analysis")

        col1, col2 = st.columns(2)

        with col1:
            store_total = merged.groupby("Store")[TARGET_COL].sum().reset_index()
            store_total = store_total.sort_values(TARGET_COL, ascending=False)
            fig = px.bar(store_total, x="Store", y=TARGET_COL,
                         title="Total Sales by Store",
                         labels={TARGET_COL: "Total Sales ($)"},
                         color=TARGET_COL,
                         color_continuous_scale="Blues")
            fig.update_layout(template="plotly_dark",
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width='stretch')

        with col2:
            if "Size" in merged.columns:
                store_info = merged.groupby("Store").agg({
                    TARGET_COL: "mean", "Size": "first", "Type": "first"
                }).reset_index()
                fig = px.scatter(store_info, x="Size", y=TARGET_COL,
                                 color="Type", size=TARGET_COL,
                                 title="Store Size vs Average Sales",
                                 labels={TARGET_COL: "Avg Sales ($)",
                                         "Size": "Store Size (sq ft)"},
                                 color_discrete_sequence=["#38bdf8", "#fbbf24", "#f87171"])
                fig.update_layout(template="plotly_dark",
                                  plot_bgcolor="rgba(0,0,0,0)",
                                  paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, width='stretch')

    # ===================================================================
    # PAGE: Department Analysis
    # ===================================================================
    elif page == "Department Analysis":
        st.header("Department Performance Analysis")

        dept_total = merged.groupby("Dept")[TARGET_COL].sum().reset_index()
        dept_total = dept_total.sort_values(TARGET_COL, ascending=False).head(20)

        fig = px.bar(dept_total, x="Dept", y=TARGET_COL,
                     title="Top 20 Departments by Total Sales",
                     labels={TARGET_COL: "Total Sales ($)", "Dept": "Department"},
                     color=TARGET_COL,
                     color_continuous_scale="Viridis")
        fig.update_layout(template="plotly_dark",
                          plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch')

    # ===================================================================
    # PAGE: Holiday Impact
    # ===================================================================
    elif page == "Holiday Impact":
        st.header("Holiday vs Non-Holiday Analysis")

        col1, col2 = st.columns(2)

        with col1:
            hol_data = merged.groupby("IsHoliday")[TARGET_COL].mean().reset_index()
            hol_data["IsHoliday"] = hol_data["IsHoliday"].map(
                {True: "Holiday", False: "Non-Holiday"})
            fig = px.bar(hol_data, x="IsHoliday", y=TARGET_COL,
                         title="Average Sales: Holiday vs Non-Holiday",
                         labels={TARGET_COL: "Avg Sales ($)",
                                 "IsHoliday": ""},
                         color="IsHoliday",
                         color_discrete_sequence=["#38bdf8", "#f87171"])
            fig.update_layout(template="plotly_dark",
                              plot_bgcolor="rgba(0,0,0,0)",
                              paper_bgcolor="rgba(0,0,0,0)",
                              showlegend=False)
            st.plotly_chart(fig, width='stretch')

        with col2:
            fig = make_subplots()
            cap = merged[TARGET_COL].quantile(0.95)
            hol_sales = merged[merged["IsHoliday"] == True][TARGET_COL]
            non_hol_sales = merged[merged["IsHoliday"] == False][TARGET_COL]

            fig.add_trace(go.Histogram(
                x=non_hol_sales[non_hol_sales <= cap],
                name="Non-Holiday", opacity=0.6,
                marker_color="#38bdf8"))
            fig.add_trace(go.Histogram(
                x=hol_sales[hol_sales <= cap],
                name="Holiday", opacity=0.6,
                marker_color="#f87171"))
            fig.update_layout(
                title="Sales Distribution by Holiday Status",
                xaxis_title="Weekly Sales ($)",
                yaxis_title="Frequency",
                barmode="overlay",
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width='stretch')

    # ===================================================================
    # PAGE: Model Performance
    # ===================================================================
    elif page == "Model Performance":
        st.header("Machine Learning Model Performance")

        if comparison_df is not None:
            st.subheader("Model Comparison")
            st.dataframe(comparison_df.style.highlight_min(
                subset=["MAE", "RMSE"], color="#1a472a"
            ).highlight_max(subset=["R2"], color="#1a472a"),
                         use_container_width=True)

            # Comparison charts
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(comparison_df, x="Model", y="RMSE",
                             title="RMSE by Model (Lower is Better)",
                             color="Model",
                             color_discrete_sequence=["#38bdf8", "#fbbf24",
                                                      "#a78bfa", "#f87171"])
                fig.update_layout(template="plotly_dark",
                                  plot_bgcolor="rgba(0,0,0,0)",
                                  paper_bgcolor="rgba(0,0,0,0)",
                                  showlegend=False)
                st.plotly_chart(fig, width='stretch')

            with col2:
                fig = px.bar(comparison_df, x="Model", y="R2",
                             title="R-squared by Model (Higher is Better)",
                             color="Model",
                             color_discrete_sequence=["#38bdf8", "#fbbf24",
                                                      "#a78bfa", "#f87171"])
                fig.update_layout(template="plotly_dark",
                                  plot_bgcolor="rgba(0,0,0,0)",
                                  paper_bgcolor="rgba(0,0,0,0)",
                                  showlegend=False,
                                  yaxis_range=[0, 1])
                st.plotly_chart(fig, width='stretch')

        # Feature importance image
        fi_path = os.path.join(FIGURES_DIR, "feature_importance.png")
        if os.path.exists(fi_path):
            st.subheader("Feature Importance")
            st.image(fi_path, use_container_width=True)
            st.caption("Feature importance indicates predictive value, "
                       "not causal relationship.")

    # ===================================================================
    # PAGE: Predict Sales
    # ===================================================================
    elif page == "Predict Sales":
        st.header("Sales Prediction")

        if model is None:
            st.warning("No trained model found. Please run `python -m src.train` first.")
            return

        st.info("Enter the parameters below to predict weekly sales.")

        col1, col2, col3 = st.columns(3)

        with col1:
            store = st.selectbox("Store", sorted(stores["Store"].unique()),
                                 index=0, key="pred_store")
            dept = st.number_input("Department", min_value=1, max_value=99,
                                   value=1, key="pred_dept")
            date = st.date_input("Date", key="pred_date")
            is_holiday = st.checkbox("Is Holiday Week?", key="pred_holiday")

        with col2:
            temperature = st.number_input("Temperature (F)", value=60.0,
                                          key="pred_temp")
            fuel_price = st.number_input("Fuel Price ($)", value=3.50,
                                         min_value=0.0, key="pred_fuel")
            cpi = st.number_input("CPI", value=220.0, min_value=0.0,
                                  key="pred_cpi")
            unemployment = st.number_input("Unemployment Rate (%)", value=7.0,
                                           min_value=0.0, max_value=30.0,
                                           key="pred_unemp")

        with col3:
            md1 = st.number_input("MarkDown1", value=0.0, min_value=0.0,
                                  key="pred_md1")
            md2 = st.number_input("MarkDown2", value=0.0, min_value=0.0,
                                  key="pred_md2")
            md3 = st.number_input("MarkDown3", value=0.0, min_value=0.0,
                                  key="pred_md3")
            md4 = st.number_input("MarkDown4", value=0.0, min_value=0.0,
                                  key="pred_md4")
            md5 = st.number_input("MarkDown5", value=0.0, min_value=0.0,
                                  key="pred_md5")

        if st.button("Predict Weekly Sales", type="primary", key="pred_button"):
            input_dict = {
                "Store": store, "Dept": dept,
                "Date": str(date), "IsHoliday": is_holiday,
                "Temperature": temperature, "Fuel_Price": fuel_price,
                "CPI": cpi, "Unemployment": unemployment,
                "MarkDown1": md1, "MarkDown2": md2, "MarkDown3": md3,
                "MarkDown4": md4, "MarkDown5": md5,
            }

            try:
                prediction = make_prediction(model, feature_cols, scaler,
                                             input_dict, stores)
                st.success(f"**Predicted Weekly Sales: ${prediction:,.2f}**")

                # Context
                hist = merged[(merged["Store"] == store) &
                              (merged["Dept"] == dept)][TARGET_COL]
                if len(hist) > 0:
                    st.info(
                        f"Historical average for Store {store}, "
                        f"Dept {dept}: ${hist.mean():,.2f} | "
                        f"Range: ${hist.min():,.2f} - ${hist.max():,.2f}"
                    )
            except Exception as e:
                st.error(f"Prediction error: {e}")

    # ===================================================================
    # PAGE: Business Insights
    # ===================================================================
    elif page == "Business Insights":
        st.header("AI-Generated Business Insights")
        st.markdown("*All insights are computed from the actual dataset -- "
                    "nothing is hard-coded.*")

        insights = generate_insights(merged)
        for i, insight in enumerate(insights, 1):
            st.markdown(
                f'<div class="insight-box">'
                f'<strong>Insight {i}:</strong> {insight}</div>',
                unsafe_allow_html=True
            )

        # Model insight
        if comparison_df is not None and model is not None:
            best = comparison_df.loc[
                comparison_df["RMSE"].astype(float).idxmin()
            ]
            st.markdown(
                f'<div class="insight-box">'
                f'<strong>Model Insight:</strong> '
                f'The best-performing model is <b>{best["Model"]}</b> '
                f'with RMSE=${best["RMSE"]:,.2f}, MAE=${best["MAE"]:,.2f}, '
                f'and R2={best["R2"]}. This means the model explains '
                f'{float(best["R2"])*100:.1f}% of the variance in weekly sales.'
                f'</div>',
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
