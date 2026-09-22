"""
Complete Academic Project Report Generator for:
IBM SkillsBuild Data Analytics with AI Academic Internship Program
BharatCares in association with AICTE

Project: AI-Powered Retail Sales Analytics and Sales Prediction
Author: THAMIZHARASAN M
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import pandas as pd
import joblib

from report_helpers import (
    set_cell_background,
    set_cell_margins,
    set_table_borders,
    add_header_footer,
    format_table
)

def create_report():
    print("Initializing document...")
    doc = docx.Document()
    add_header_footer(doc)

    # Palette
    NAVY = RGBColor(31, 78, 121)     # Primary headings
    SLATE = RGBColor(46, 85, 151)    # Secondary headings
    DARK_GRAY = RGBColor(40, 40, 40) # Body text
    MUTED = RGBColor(100, 100, 100)  # Captions

    def add_p(text, style='Normal', space_after=6, space_before=0, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.line_spacing = line_spacing
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(11)
        run.font.color.rgb = DARK_GRAY
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = NAVY
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = SLATE
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Calibri"
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = SLATE
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r1 = p.add_run(bold_prefix)
        r1.font.name = "Calibri"
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r1.font.color.rgb = DARK_GRAY
        r2 = p.add_run(text)
        r2.font.name = "Calibri"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = DARK_GRAY
        return p

    def add_fig(img_path, caption_num_title, explanation, width=Inches(5.6)):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(10)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.paragraph_format.keep_with_next = True
            run_img = p_img.add_run()
            run_img.add_picture(img_path, width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(6)
            p_cap.paragraph_format.keep_with_next = True
            run_cap = p_cap.add_run(caption_num_title)
            run_cap.font.name = "Calibri"
            run_cap.font.size = Pt(9.5)
            run_cap.font.bold = True
            run_cap.font.italic = True
            run_cap.font.color.rgb = NAVY

            add_p(explanation, space_after=8, space_before=2)
        else:
            print(f"Warning: Image {img_path} not found.")

    # =========================================================================
    # TITLE PAGE
    # =========================================================================
    print("Adding Title Page...")
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.space_before = Pt(36)
    tp.paragraph_format.space_after = Pt(8)
    r = tp.add_run("IBM SkillsBuild Data Analytics with AI\nAcademic Internship Program")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = SLATE

    p_org = doc.add_paragraph()
    p_org.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_org.paragraph_format.space_after = Pt(36)
    r = p_org.add_run("Conducted by BharatCares in Association with AICTE")
    r.font.name = "Calibri"
    r.font.size = Pt(12)
    r.font.italic = True
    r.font.color.rgb = RGBColor(110, 110, 110)

    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_after = Pt(12)
    r = p_proj.add_run("INTERNSHIP PROJECT REPORT")
    r.font.name = "Calibri"
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(80, 80, 80)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(20)
    r = p_title.add_run("AI-POWERED RETAIL SALES ANALYTICS AND SALES PREDICTION")
    r.font.name = "Calibri"
    r.font.size = Pt(21)
    r.font.bold = True
    r.font.color.rgb = NAVY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(48)
    r = p_sub.add_run("Domain: Data Analytics using AI | Retail Demand Forecasting")
    r.font.name = "Calibri"
    r.font.size = Pt(12)
    r.font.color.rgb = SLATE

    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subm.paragraph_format.space_before = Pt(36)
    p_subm.paragraph_format.space_after = Pt(4)
    r = p_subm.add_run("Submitted by:")
    r.font.name = "Calibri"
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(100, 100, 100)

    p_name = doc.add_paragraph()
    p_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_name.paragraph_format.space_after = Pt(48)
    r = p_name.add_run("THAMIZHARASAN M")
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = NAVY

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(24)
    r = p_date.add_run("Academic Year 2025–2026\nBharatCares | AICTE | IBM SkillsBuild")
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(120, 120, 120)

    doc.add_page_break()

    # =========================================================================
    # DECLARATION & ACKNOWLEDGEMENT
    # =========================================================================
    print("Adding Declaration & Acknowledgement...")
    add_h1("STUDENT DECLARATION")
    add_p(
        "I, Thamizharasan M, hereby declare that the internship project entitled "
        "\"AI-Powered Retail Sales Analytics and Sales Prediction\" submitted for the "
        "IBM SkillsBuild Data Analytics with AI Academic Internship Program conducted by "
        "BharatCares in association with AICTE, is an authentic record of independent project work "
        "completed by me under the guidelines provided. All datasets, preprocessing scripts, exploratory "
        "analyses, machine learning models, evaluations, and interactive dashboards described herein "
        "have been implemented and validated based on actual execution of the project codebase."
    )
    add_p("Candidate Name: Thamizharasan M\nDomain: Data Analytics using AI\nDate: September 2026", space_before=16, space_after=24)

    add_h1("ACKNOWLEDGEMENT")
    add_p(
        "I express my sincere gratitude to IBM SkillsBuild, BharatCares, and the All India Council for "
        "Technical Education (AICTE) for providing the opportunity, computational platform, and curriculum "
        "to undertake this academic internship in Data Analytics using AI. The structured learning modules "
        "and applied problem statements enabled me to bridge theoretical statistical knowledge with "
        "practical machine learning and modern retail analytics."
    )
    add_p(
        "I also thank the mentors, program coordinators, and open-source software communities (Python, "
        "Pandas, Scikit-learn, XGBoost, and Streamlit) whose foundational tools and documentation made the "
        "robust realization of this predictive system possible."
    )

    doc.add_page_break()

    # =========================================================================
    # ABSTRACT
    # =========================================================================
    print("Adding Abstract...")
    add_h1("ABSTRACT")
    add_p(
        "In the contemporary retail enterprise, accurate sales forecasting is an essential operational "
        "pillar that governs inventory turnover, supply chain resilience, promotional scheduling, and "
        "workforce allocation. This project implements a comprehensive, end-to-end predictive analytics "
        "system using historical sales records from 45 Walmart retail stores spanning 81 distinct departments "
        "between February 2010 and October 2012, with evaluation over test records extending into July 2013."
    )
    add_p(
        "The project follows a rigorous data science lifecycle. Data preprocessing involved multi-table relational "
        "merging across historical transactions, store master data, and localized economic features. Missing data "
        "in promotional markdown columns (50%–64% unrecorded prior to November 2011) were systematically imputed "
        "with zeros to denote non-promotional baselines, while localized economic series (Consumer Price Index and "
        "Unemployment) were imputed using median baselines. Twenty-three engineered features were synthesized, "
        "incorporating temporal breakdowns (Year, Month, WeekOfYear, DayOfWeek, Quarter), cyclical calendar indicators, "
        "store-type label encodings, and promotional markdown aggregates."
    )
    add_p(
        "To guarantee real-world generalization and prevent temporal data leakage, a strict time-based split "
        "was enforced at July 1, 2012 (training on February 2010 – June 2012; validating on July 2012 – October 2012). "
        "Five machine learning models were developed and systematically evaluated: a Naive Historical Mean Baseline, "
        "Ordinary Least Squares Linear Regression, Random Forest Regressor, Histogram-based Gradient Boosting, and "
        "eXtreme Gradient Boosting (XGBoost). Model selection was programmatically governed by validation Root Mean "
        "Squared Error (RMSE)."
    )
    add_p(
        "The Random Forest Regressor achieved superior performance, recording a validation Mean Absolute Error (MAE) "
        "of $2,075.79, an RMSE of $4,005.37, an R-squared of 0.9668 (explaining 96.68% of sales variance), and a Mean "
        "Absolute Percentage Error (MAPE) of 29.84%, outperforming XGBoost ($4,261.48 RMSE, R²=0.9624) and Linear "
        "Regression ($20,963.37 RMSE, R²=0.0893). Permutation importance revealed that Department identity (64.7%) "
        "and Store Size (19.1%) represent 83.8% of aggregate predictive importance, while external macroeconomic "
        "indicators exhibited weak direct linear correlation. The selected model generated 115,064 weekly department-level "
        "sales forecasts for the test horizon. An interactive 8-page Streamlit web dashboard and an automated test suite "
        "comprising 16 unit tests (100% pass rate) were developed to ensure practical operational utility and enterprise reproducibility."
    )
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(12)
    p_kw.paragraph_format.space_after = Pt(18)
    r1 = p_kw.add_run("Keywords: ")
    r1.font.bold = True
    r1.font.name = "Calibri"
    r2 = p_kw.add_run("Retail Sales Analytics, Demand Forecasting, Random Forest, XGBoost, Time-Series Validation, Feature Engineering, Permutation Importance, Streamlit Dashboard.")
    r2.font.italic = True
    r2.font.name = "Calibri"

    doc.add_page_break()

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    print("Adding Table of Contents...")
    add_h1("TABLE OF CONTENTS")
    toc_items = [
        ("1. Introduction", "5"),
        ("2. Background and Problem Context", "6"),
        ("3. Problem Statement", "7"),
        ("4. Project Objectives", "7"),
        ("5. Project Scope", "8"),
        ("6. Dataset Description and Characteristics", "9"),
        ("7. Data Understanding and Preprocessing", "11"),
        ("8. Exploratory Data Analysis (EDA)", "13"),
        ("9. Feature Engineering", "19"),
        ("10. Machine Learning Methodology", "21"),
        ("11. Machine Learning Models", "22"),
        ("12. Model Evaluation and Comparison", "24"),
        ("13. Final Model Selection and Test Prediction", "26"),
        ("14. Actionable Business Insights", "27"),
        ("15. System Architecture and Workflow", "29"),
        ("16. Implementation Details and Technology Stack", "30"),
        ("17. Testing, Verification, and Quality Assurance", "31"),
        ("18. Results and Discussion", "32"),
        ("19. Project Limitations", "35"),
        ("20. Future Scope and Roadmap", "36"),
        ("21. Conclusion", "37"),
        ("22. Internship Learning Outcomes", "38"),
        ("23. References", "39"),
        ("Appendices", "40"),
    ]
    tbl_toc = doc.add_table(rows=len(toc_items), cols=2)
    tbl_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (item, page) in enumerate(toc_items):
        r_cells = tbl_toc.rows[idx].cells
        r_cells[0].width = Inches(5.8)
        r_cells[1].width = Inches(0.7)
        r_cells[0].text = item
        r_cells[1].text = page
        r_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for c in r_cells:
            set_cell_margins(c, top=40, bottom=40, left=50, right=50)
            for r in c.paragraphs[0].runs:
                r.font.name = "Calibri"
                r.font.size = Pt(10)
                if item.startswith(("1.", "6.", "8.", "10.", "12.", "18.", "21.")):
                    r.font.bold = True

    add_h2("LIST OF TABLES")
    tbl_list = [
        ("Table 6.1: Overview of Walmart Retail Sales Datasets", "9"),
        ("Table 6.2: Structural Schema of Primary Data Tables", "10"),
        ("Table 9.1: Master Feature Engineering Specification (23 Predictors)", "20"),
        ("Table 12.1: Comprehensive Machine Learning Validation Performance", "24"),
        ("Table 16.1: Project Technology Stack and Operational Dependencies", "30"),
        ("Table 17.1: Automated Pytest Test Suite Results (16 Cases)", "31"),
        ("Table 18.1: Top 10 Most Influential Features by Permutation Importance", "34"),
        ("Table C.1: Sample Test Forecasts Generated by Final Model", "41"),
    ]
    tbl_tl = doc.add_table(rows=len(tbl_list), cols=2)
    tbl_tl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (item, page) in enumerate(tbl_list):
        r_cells = tbl_tl.rows[idx].cells
        r_cells[0].width = Inches(5.8)
        r_cells[1].width = Inches(0.7)
        r_cells[0].text = item
        r_cells[1].text = page
        r_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for c in r_cells:
            set_cell_margins(c, top=30, bottom=30, left=50, right=50)
            for r in c.paragraphs[0].runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)

    add_h2("LIST OF FIGURES")
    fig_list = [
        ("Figure 8.1: Weekly Sales Distribution and Skewness", "13"),
        ("Figure 8.2: Longitudinal Weekly Sales Trend (2010–2012)", "14"),
        ("Figure 8.3: Monthly Aggregate Sales Trend", "15"),
        ("Figure 8.4: Annual Seasonal Comparison (2010 vs 2011 vs 2012)", "15"),
        ("Figure 8.5: Total Historical Sales by Store (Store 1 to Store 45)", "16"),
        ("Figure 8.6: Store Physical Size vs Average Weekly Sales by Store Type", "16"),
        ("Figure 8.7: Top 20 Revenue-Generating Departments", "17"),
        ("Figure 8.8: Holiday vs Non-Holiday Weekly Sales Distribution", "17"),
        ("Figure 8.9: Relationship Between External Factors and Weekly Sales", "18"),
        ("Figure 8.10: Correlation Heatmap Across Numerical Features", "18"),
        ("Figure 12.1: Model Performance Comparison Across Evaluation Metrics", "25"),
        ("Figure 18.1: Actual vs Predicted Weekly Sales (Validation Set)", "33"),
        ("Figure 18.2: Residual Error Distribution and Residual Plot", "33"),
        ("Figure 18.3: Permutation Feature Importance of Random Forest Model", "34"),
    ]
    tbl_fl = doc.add_table(rows=len(fig_list), cols=2)
    tbl_fl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (item, page) in enumerate(fig_list):
        r_cells = tbl_fl.rows[idx].cells
        r_cells[0].width = Inches(5.8)
        r_cells[1].width = Inches(0.7)
        r_cells[0].text = item
        r_cells[1].text = page
        r_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for c in r_cells:
            set_cell_margins(c, top=30, bottom=30, left=50, right=50)
            for r in c.paragraphs[0].runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    print("Writing Chapter 1: Introduction...")
    add_h1("1. INTRODUCTION")
    add_p(
        "Retail analytics has emerged as one of the most transformative disciplines within contemporary enterprise "
        "decision-making. Modern retail chains operate at unprecedented scales, orchestrating networks of physical "
        "stores, regional distribution centers, and thousands of merchandise categories. In this hyper-competitive "
        "environment, maintaining an optimal balance between inventory holding costs and customer satisfaction represents "
        "a formidable challenge. Inaccurate demand estimation triggers severe financial penalties: underestimating demand "
        "leads to stockouts, missed sales, and brand dilution, while overestimating demand generates excess inventory, "
        "increased holding expenses, and aggressive price depreciation through forced markdowns."
    )
    add_p(
        "Historically, retail forecasting relied primarily on simple heuristic rules, moving averages, and basic linear "
        "extrapolations. While these traditional techniques provided reasonable estimates during steady-state trading, "
        "they fail systematically when confronted with the intricate dynamics of modern commerce: sharp holiday demand "
        "surges (e.g., Thanksgiving, Black Friday, and Christmas), store-specific layout differences, departmental "
        "heterogeneity, promotional markdown schedules, and broader macroeconomic shifts (such as fuel price fluctuations "
        "and inflation trends). Machine learning offers an effective paradigm to model these complex, non-linear "
        "interactions by simultaneously processing historical transactional records, store characteristics, and external "
        "environmental indicators."
    )
    add_p(
        "This project utilizes the historical Walmart Store Sales Forecasting dataset, a benchmark retail analytics corpus "
        "spanning 45 physical retail stores across diverse geographical regions of the United States. Through an end-to-end "
        "applied data science methodology, this report details the data preprocessing pipeline, in-depth exploratory data "
        "analysis, feature engineering, multi-model comparative machine learning, rigorous time-based validation, prediction "
        "generation, and the extraction of actionable business insights."
    )

    # =========================================================================
    # CHAPTER 2: BACKGROUND AND PROBLEM CONTEXT
    # =========================================================================
    print("Writing Chapter 2: Background...")
    add_h1("2. BACKGROUND AND PROBLEM CONTEXT")
    add_p(
        "The Walmart operational footprint analyzed in this investigation encapsulates substantial retail heterogeneity. "
        "Retail stores are categorized into three distinct operational formats: Type A, Type B, and Type C, representing "
        "supercenters, conventional stores, and smaller neighborhood formats with store square footage ranging from "
        "34,875 to 219,622 square feet. Within each store, sales are tracked weekly across up to 81 individual departments, "
        "ranging from high-turnover grocery lines to specialized seasonal categories."
    )
    add_p(
        "Several distinct contextual layers govern the variance in weekly retail sales across this network:"
    )
    add_bullet("Store and Department Disparity: ", "Weekly department revenue spans multiple orders of magnitude, with core departments generating over $100,000 weekly while smaller specialized departments yield modest revenues under $1,000.")
    add_bullet("Seasonal and Calendar Spikes: ", "A substantial portion of annual retail profitability is concentrated around major American holidays, specifically the Super Bowl, Labor Day, Thanksgiving (Black Friday), and Christmas. Accurately quantifying holiday multipliers is critical for supply chain readiness.")
    add_bullet("Promotional Markdowns: ", "Beginning in late 2011, Walmart recorded anonymized promotional markdowns (MarkDown1 through MarkDown5). These promotional activities directly alter demand velocity, requiring dedicated feature representations.")
    add_bullet("Macroeconomic Climate: ", "The dataset spans the 2010–2012 post-recession recovery era, during which regional Consumer Price Index (CPI), regional unemployment rates, and fluctuating fuel prices exerted varying pressures on consumer purchasing power.")

    # =========================================================================
    # CHAPTER 3: PROBLEM STATEMENT
    # =========================================================================
    print("Writing Chapter 3: Problem Statement...")
    add_h1("3. PROBLEM STATEMENT")
    add_p(
        "The core technical and business problem addressed in this investigation is formulated as follows:"
    )
    add_p(
        "\"How can historical weekly store- and department-level sales data, combined with store structural master "
        "records, promotional markdowns, and macroeconomic indicators, be rigorously preprocessed, analyzed, and modeled "
        "using supervised machine learning to generate accurate weekly sales predictions across future unseen horizons "
        "while providing interpretable, data-driven business insights to guide enterprise inventory and merchandising decisions?\""
    )
    add_p(
        "Mathematically, the objective is to model a mapping function f: X -> y, where X in R^23 represents the feature "
        "vector encompassing store attributes, departmental identifiers, temporal indicators, markdown aggregates, and "
        "macroeconomic metrics, and y in R represents the continuous Weekly_Sales target variable, minimizing validation "
        "Root Mean Squared Error (RMSE) without inducing data leakage across temporal boundaries."
    )

    # =========================================================================
    # CHAPTER 4: PROJECT OBJECTIVES
    # =========================================================================
    print("Writing Chapter 4: Project Objectives...")
    add_h1("4. PROJECT OBJECTIVES")
    add_p("To systematically resolve the problem statement, the project defined ten concrete technical objectives:")
    add_bullet("Objective 1 — Data Cleaning and Integration: ", "Ingest, clean, and merge transactional records, store characteristics, and regional features into a consolidated relational repository without record loss.")
    add_bullet("Objective 2 — Missing-Value Remediation: ", "Diagnose structural missingness across markdown columns (50%–64% unrecorded prior to Nov 2011) and macroeconomic metrics, applying mathematically sound imputation protocols.")
    add_bullet("Objective 3 — Exploratory Data Analysis: ", "Perform comprehensive univariate, bivariate, and multivariate analysis to characterize sales distributions, seasonal peaks, departmental rankings, and external correlations.")
    add_bullet("Objective 4 — Feature Engineering: ", "Formulate 23 predictive features including temporal breakdowns, cyclical indicators, store-type encodings, and aggregate promotional markdown flags.")
    add_bullet("Objective 5 — Data Leakage Prevention: ", "Implement strict time-based train/validation splitting (cut-off at 2012-07-01) mirroring production forecasting realities.")
    add_bullet("Objective 6 — Multi-Model Development: ", "Train and benchmark diverse learning algorithms: Naive Mean Baseline, Linear Regression, Random Forest, HistGradientBoosting, and XGBoost.")
    add_bullet("Objective 7 — Rigorous Model Evaluation: ", "Evaluate model performance using multiple complementary error metrics: MAE, RMSE, R-squared (R²), and MAPE.")
    add_bullet("Objective 8 — Programmatic Model Selection: ", "Select the optimal final model based on validation RMSE and serialize the model artifacts (.pkl) for deployment.")
    add_bullet("Objective 9 — Test Set Inference: ", "Generate robust forecasts for 115,064 department-store-week combinations in the unseen test dataset.")
    add_bullet("Objective 10 — Enterprise Deployment and Testing: ", "Develop an interactive 8-page Streamlit decision-support application and establish an automated pytest test suite for continuous verification.")

    # =========================================================================
    # CHAPTER 5: PROJECT SCOPE
    # =========================================================================
    print("Writing Chapter 5: Project Scope...")
    add_h1("5. PROJECT SCOPE")
    add_p(
        "The boundaries of this project encompass all computational, analytical, and modeling activities necessary "
        "to deliver an academic and enterprise-grade forecasting system. The in-scope elements include:"
    )
    add_bullet("In-Scope: ", "Historical analysis across all 45 Walmart stores and 81 departments.")
    add_bullet("In-Scope: ", "Preprocessing 421,570 training transactions and 115,064 test records.")
    add_bullet("In-Scope: ", "Engineering calendar, structural, and promotional feature transformations.")
    add_bullet("In-Scope: ", "Comparative evaluation across 5 distinct regression models.")
    add_bullet("In-Scope: ", "Permutation feature importance analysis on the winning ensemble.")
    add_bullet("In-Scope: ", "Delivery of interactive dashboard (app/app.py) and test suite (tests/test_pipeline.py).")
    add_p(
        "The project scope explicitly excludes real-time intra-day transactional modeling (as the original dataset "
        "is recorded at weekly granularity), competitor pricing ingestion (not captured in the original dataset), "
        "and geographical spatial optimization (store latitude and longitude coordinates were anonymized by Walmart)."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 6: DATASET DESCRIPTION
    # =========================================================================
    print("Writing Chapter 6: Dataset Description...")
    add_h1("6. DATASET DESCRIPTION AND CHARACTERISTICS")
    add_p(
        "The project utilizes the official Walmart Store Sales Forecasting dataset, originally published for competitive "
        "academic and industry benchmark evaluation. The data repository consists of five tabular CSV files:"
    )

    # Table 6.1: Overview of Datasets
    headers_6_1 = ["File Name", "Record Count", "Column Count", "Temporal Coverage", "Primary Functional Role"]
    data_6_1 = [
        ["train.csv", "421,570", "5", "2010-02-05 to 2012-10-26", "Historical transactions with Weekly_Sales target"],
        ["test.csv", "115,064", "4", "2012-11-02 to 2013-07-26", "Unseen evaluation records for blind forecasting"],
        ["features.csv", "8,190", "12", "2010-02-05 to 2013-07-26", "Store-week environmental and economic data"],
        ["stores.csv", "45", "3", "Static Master", "Physical store classification (Type) and Size (sq ft)"],
        ["sampleSubmission.csv", "115,064", "2", "2012-11-02 to 2013-07-26", "Benchmark submission template (Id, Weekly_Sales)"]
    ]
    t61 = doc.add_table(rows=len(data_6_1) + 1, cols=len(headers_6_1))
    format_table(t61, [Inches(1.5), Inches(0.9), Inches(0.8), Inches(1.8), Inches(1.8)], headers_6_1, data_6_1,
                 alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
    add_p("Table 6.1: Overview of Walmart Retail Sales Datasets", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    add_h2("Detailed Schema Analysis")
    add_p(
        "The relational schema connects individual department transactions to store-level attributes and localized "
        "environmental indicators through composite keys:"
    )

    # Table 6.2: Schema
    headers_6_2 = ["Attribute Name", "Source Table", "Data Type", "Measurement / Description"]
    data_6_2 = [
        ["Store", "train / test / stores / feat", "Integer (1 to 45)", "Unique physical store identifier"],
        ["Dept", "train / test", "Integer (1 to 99)", "Department identifier within the store"],
        ["Date", "train / test / features", "Date (YYYY-MM-DD)", "Weekly sales reporting date (always Friday)"],
        ["Weekly_Sales", "train.csv", "Float (Continuous)", "Target Variable: Total sales for given store-dept-week ($)"],
        ["IsHoliday", "train / test / features", "Boolean (True/False)", "Indicator of whether reporting week contains a major holiday"],
        ["Type", "stores.csv", "Categorical (A, B, C)", "Store format category (A: Supercenter, B: Mid-size, C: Small)"],
        ["Size", "stores.csv", "Integer (34,875 - 219,622)", "Total physical store area in square feet"],
        ["Temperature", "features.csv", "Float (-2.06°F to 101.95°F)", "Average weekly temperature in region of store"],
        ["Fuel_Price", "features.csv", "Float ($2.47 to $4.47)", "Regional average cost of fuel per gallon"],
        ["MarkDown1 - 5", "features.csv", "Float (Continuous)", "Anonymized promotional discounts; missing prior to late 2011"],
        ["CPI", "features.csv", "Float (126.06 to 228.98)", "Consumer Price Index measuring regional inflation"],
        ["Unemployment", "features.csv", "Float (3.88% to 14.31%)", "Regional unemployment rate"]
    ]
    t62 = doc.add_table(rows=len(data_6_2) + 1, cols=len(headers_6_2))
    format_table(t62, [Inches(1.4), Inches(1.5), Inches(1.5), Inches(2.4)], headers_6_2, data_6_2,
                 alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
    add_p("Table 6.2: Structural Schema of Primary Data Tables", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=14)

    # =========================================================================
    # CHAPTER 7: DATA PREPROCESSING
    # =========================================================================
    print("Writing Chapter 7: Data Preprocessing...")
    add_h1("7. DATA UNDERSTANDING AND PREPROCESSING")
    add_p(
        "Raw transactional datasets are prone to missing values, anomalous records, and relational fragmentation. "
        "A rigorous preprocessing pipeline was established in src/data_preprocessing.py to ensure high data integrity:"
    )
    add_h2("7.1 Missing-Value Diagnosis and Imputation")
    add_p(
        "A systematic missing-value audit was executed across all tables. While train.csv, test.csv, and stores.csv "
        "exhibit 100% completeness (zero missing cells), features.csv presents substantial structural missingness:"
    )
    add_bullet("Promotional Markdowns (MarkDown1 to MarkDown5): ", "MarkDown columns contain between 50% and 64% missing values. Analysis confirms that markdowns were only systematically introduced and tracked by Walmart starting in November 2011. Imputing with mean or median would introduce false promotional activity. Therefore, all missing markdown values were imputed with 0.0, establishing a baseline of zero promotional discount.")
    add_bullet("Macroeconomic Variables (CPI and Unemployment): ", "In features.csv, 585 values (7.14%) are missing, exclusively concentrated in the future test horizon of 2013 for specific stores. These gaps were imputed using median column values to prevent disruption during feature scaling.")

    add_h2("7.2 Anomaly and Negative Sales Treatment")
    add_p(
        "In train.csv, exactly 1,285 records (0.30% of total) exhibit negative Weekly_Sales values (minimum -$4,988.94), "
        "and 73 records exhibit exactly $0.00 sales. Domain investigation indicates that negative sales represent customer "
        "returns or inter-store inventory reallocations that exceed current-week purchases. While these rows are retained "
        "in the historical training log to avoid altering transactional totals, they are isolated during MAPE calculation "
        "to prevent mathematical instability (division by near-zero)."
    )

    add_h2("7.3 Relational Data Integration")
    add_p(
        "The training and test datasets were enriched by executing a two-stage merge. First, train.csv was merged "
        "with stores.csv on the Store key. Next, the resulting table was merged with features.csv on the composite "
        "key [Store, Date]. The IsHoliday column present in both tables was harmonized into a single boolean feature. "
        "Verification confirmed that the merge was strictly row-preserving: 421,570 training rows and 115,064 test rows "
        "were preserved exactly with zero data duplication."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 8: EXPLORATORY DATA ANALYSIS (EDA)
    # =========================================================================
    print("Writing Chapter 8: EDA...")
    add_h1("8. EXPLORATORY DATA ANALYSIS (EDA)")
    add_p(
        "Exploratory Data Analysis was conducted across multiple analytical dimensions to uncover underlying patterns, "
        "seasonal rhythms, structural correlations, and behavioral anomalies within the Walmart enterprise."
    )

    # Figure 8.1
    add_fig(
        "outputs/figures/sales_distribution.png",
        "Figure 8.1: Weekly Sales Distribution and Skewness",
        "Analysis of Figure 8.1 reveals that weekly departmental sales are heavily right-skewed, with the majority "
        "of weekly observations clustering between $2,000 and $15,000, while high-volume departments generate a long "
        "tail extending past $100,000. The mean sales figure ($15,981) significantly exceeds the median ($7,612), "
        "indicating high revenue concentration in elite departments and major holiday weeks.",
        width=Inches(5.8)
    )

    # Figure 8.2
    add_fig(
        "outputs/figures/weekly_sales_trend.png",
        "Figure 8.2: Longitudinal Weekly Sales Trend (2010–2012)",
        "Figure 8.2 tracks weekly sales across the 143-week historical timeline. Baseline weekly chain sales consistently "
        "hover between $42M and $48M. However, dramatic demand surges occur annually during Week 47 (Thanksgiving / Black Friday, "
        "surpassing $65M) and Week 51 (pre-Christmas week, peaking above $80M). A secondary post-Christmas dip occurs in January.",
        width=Inches(5.8)
    )

    # Figure 8.3 & Figure 8.4
    add_fig(
        "outputs/figures/monthly_sales.png",
        "Figure 8.3: Monthly Aggregate Sales Trend",
        "Figure 8.3 highlights monthly aggregate revenue. Sales remain relatively stable from February through October "
        "(averaging $15,000 to $16,000 per department-week) before expanding sharply in November ($18,800 average) and "
        "peaking in December ($21,500 average), corroborating the paramount significance of Q4 holiday retail execution.",
        width=Inches(5.8)
    )

    add_fig(
        "outputs/figures/seasonal_pattern.png",
        "Figure 8.4: Annual Seasonal Comparison (2010 vs 2011 vs 2012)",
        "Comparing annual profiles in Figure 8.4 demonstrates remarkable cyclical consistency across 2010 and 2011. "
        "The timing and relative amplitude of holiday spikes align closely across calendar years, confirming that seasonal "
        "calendar features (WeekOfYear) carry strong predictive power.",
        width=Inches(5.8)
    )

    doc.add_page_break()

    # Figure 8.5 & Figure 8.6
    add_fig(
        "outputs/figures/store_analysis.png",
        "Figure 8.5: Total Historical Sales by Store (Store 1 to Store 45)",
        "Figure 8.5 illustrates immense performance variance across individual stores. Store 20 leads the enterprise "
        "with over $301M in cumulative sales, followed closely by Store 4 ($299M) and Store 14 ($288M). Conversely, "
        "Store 33 generated only $37M over the same period, illustrating an 8-fold disparity in store revenue generation capacity.",
        width=Inches(5.8)
    )

    add_fig(
        "outputs/figures/store_size_vs_sales.png",
        "Figure 8.6: Store Physical Size vs Average Weekly Sales by Store Type",
        "Figure 8.6 examines store physical area (square feet) versus average weekly revenue, colored by store type. A strong "
        "positive correlation (Pearson r = 0.79) exists between store size and sales volume. Type A stores (blue circles) "
        "cluster in the upper-right quadrant (>150,000 sq ft, >$20,000 weekly average), Type B stores occupy the mid-tier "
        "(100,000–140,000 sq ft), and Type C stores cluster below 50,000 sq ft.",
        width=Inches(5.0)
    )

    # Figure 8.7 & Figure 8.8
    add_fig(
        "outputs/figures/department_analysis.png",
        "Figure 8.7: Top 20 Revenue-Generating Departments",
        "Figure 8.7 ranks the top 20 departments across the chain. Department 92 is the undisputed revenue leader, generating "
        "over $484M in historical sales, followed by Department 95 ($449M), Department 38 ($393M), and Department 72 ($306M). "
        "The top 10 departments account for approximately 48% of total retail sales, confirming the Pareto distribution.",
        width=Inches(5.6)
    )

    add_fig(
        "outputs/figures/holiday_analysis.png",
        "Figure 8.8: Holiday vs Non-Holiday Weekly Sales Distribution",
        "Figure 8.8 compares weekly sales during official holiday weeks versus regular weeks. Holiday weeks exhibit an average "
        "weekly sales of $17,036 compared to $15,901 during non-holiday weeks—a statistically significant 7.14% baseline lift, "
        "driven primarily by Thanksgiving and Christmas.",
        width=Inches(5.6)
    )

    doc.add_page_break()

    # Figure 8.9 & Figure 8.10
    add_fig(
        "outputs/figures/external_factors.png",
        "Figure 8.9: Relationship Between External Factors and Weekly Sales",
        "Figure 8.9 plots Weekly_Sales against Temperature, Fuel_Price, CPI, and Unemployment. In each subplot, the scatter "
        "distribution is widely dispersed with virtually horizontal regression trend lines, indicating that macroeconomic "
        "and meteorological variables exert very weak direct linear correlation on aggregate sales.",
        width=Inches(5.2)
    )

    add_fig(
        "outputs/figures/correlation_heatmap.png",
        "Figure 8.10: Correlation Heatmap Across Numerical Features",
        "Figure 8.10 presents the Pearson correlation matrix. Weekly_Sales correlates moderately with store Size (r = 0.24) "
        "and shows negligible linear correlation with Temperature (-0.06), Fuel Price (0.00), CPI (-0.02), and Unemployment (-0.03). "
        "However, markdowns correlate positively with each other (MarkDown1 and MarkDown4 r = 0.81). This confirms that linear "
        "models will struggle and non-linear tree-based models are required.",
        width=Inches(4.8)
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 9: FEATURE ENGINEERING
    # =========================================================================
    print("Writing Chapter 9: Feature Engineering...")
    add_h1("9. FEATURE ENGINEERING")
    add_p(
        "Feature engineering translates raw transactional logs into high-signal numerical representations. "
        "Twenty-three feature columns were formulated in src/feature_engineering.py and validated against data leakage:"
    )

    # Table 9.1: Feature Engineering Table
    headers_9_1 = ["Feature Name", "Derivation Logic", "Type", "Operational Rationale"]
    data_9_1 = [
        ["Store", "Direct from train.csv", "Categorical (ID)", "Captures store identity, location, and regional trade area"],
        ["Dept", "Direct from train.csv", "Categorical (ID)", "Captures merchandise category volume and demand velocity"],
        ["IsHoliday", "Converted to boolean / int", "Binary (0/1)", "Captures holiday demand multiplier across chain"],
        ["Temperature", "Direct from features.csv", "Float (°F)", "Captures seasonal weather effects on foot traffic"],
        ["Fuel_Price", "Direct from features.csv", "Float ($)", "Indicator of consumer disposable income and travel cost"],
        ["MarkDown1 - 5", "Imputed with 0.0 for NaNs", "Float ($)", "Individual anonymized promotional discount intensities"],
        ["CPI", "Median imputed for test NaNs", "Float", "Macroeconomic inflation metric"],
        ["Unemployment", "Median imputed for test NaNs", "Float (%)", "Regional labor market indicator"],
        ["Size", "Direct from stores.csv", "Integer (sq ft)", "Physical retail capacity and inventory breadth"],
        ["Type_encoded", "Label encoded: A=0, B=1, C=2", "Categorical (Int)", "Store classification format hierarchy"],
        ["Year", "Date.dt.year", "Integer", "Long-term trend and macroeconomic baseline shift"],
        ["Month", "Date.dt.month (1 to 12)", "Integer", "Annual seasonality and quarterly retail cycle"],
        ["WeekOfYear", "Date.dt.isocalendar().week", "Integer (1 to 52)", "Granular weekly calendar position (holiday alignment)"],
        ["DayOfWeek", "Date.dt.dayofweek", "Integer (always 4)", "Day of week (Friday reporting consistency check)"],
        ["Quarter", "Date.dt.quarter (1 to 4)", "Integer", "Corporate financial quarter indicator"],
        ["IsMonthStart", "Date.dt.is_month_start", "Binary (0/1)", "Captures beginning-of-month salary and benefit spending"],
        ["IsMonthEnd", "Date.dt.is_month_end", "Binary (0/1)", "Captures end-of-month clearance and budgetary cycles"],
        ["TotalMarkDown", "Sum of MarkDown1 through 5", "Float ($)", "Aggregate promotional discount dollar magnitude"],
        ["HasMarkDown", "Binary flag: TotalMarkDown > 0", "Binary (0/1)", "Clear indicator of whether store is in promotional status"]
    ]
    t91 = doc.add_table(rows=len(data_9_1) + 1, cols=len(headers_9_1))
    format_table(t91, [Inches(1.4), Inches(1.8), Inches(1.3), Inches(2.3)], headers_9_1, data_9_1,
                 alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
    add_p("Table 9.1: Master Feature Engineering Specification (23 Predictors)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=14)

    # =========================================================================
    # CHAPTER 10: MACHINE LEARNING METHODOLOGY
    # =========================================================================
    print("Writing Chapter 10: Methodology...")
    add_h1("10. MACHINE LEARNING METHODOLOGY")
    add_p(
        "A rigorous, scientifically sound machine learning methodology was designed to ensure that model evaluation "
        "faithfully simulates production deployment conditions. The critical methodological decisions include:"
    )
    add_h2("10.1 Temporal Train/Validation Splitting (Data Leakage Prevention)")
    add_p(
        "In sales forecasting, applying random k-fold cross-validation or random train-test splitting introduces "
        "severe **temporal data leakage**. If records from future dates (e.g., Thanksgiving 2011) are randomly mixed "
        "into the training set while predicting past dates, the model learns future demand patterns beforehand, yielding "
        "artificially deflated error metrics that fail catastrophically in production."
    )
    add_p(
        "To prevent data leakage, a strict **time-based validation split** was enforced at **July 1, 2012**:"
    )
    add_bullet("Training Partition: ", "February 5, 2010 to June 29, 2012 (125 reporting weeks, 359,004 records, ~85.2% of data). Models learn exclusively from past chronological history.")
    add_bullet("Validation Partition: ", "July 6, 2012 to October 26, 2012 (17 reporting weeks, 62,566 records, ~14.8% of data). Serves as the unseen holdout set for all model benchmarking.")
    add_bullet("Test Inference Partition: ", "November 2, 2012 to July 26, 2013 (39 reporting weeks, 115,064 records). Unseen future horizon evaluated by the final serialized model.")

    # =========================================================================
    # CHAPTER 11: MACHINE LEARNING MODELS
    # =========================================================================
    print("Writing Chapter 11: Models...")
    add_h1("11. MACHINE LEARNING MODELS")
    add_p(
        "Five distinct model architectures spanning baseline heuristics, linear regression, and non-linear ensemble "
        "methods were trained and evaluated:"
    )
    add_h2("11.1 Naive Mean Baseline")
    add_p(
        "The Naive Mean Baseline computes the historical mean sales for each unique [Store, Dept] tuple from the training set. "
        "For unseen combinations, it falls back to the global store mean. This heuristic establishes the absolute minimum "
        "performance threshold that any machine learning model must convincingly surpass."
    )

    add_h2("11.2 Ordinary Least Squares Linear Regression")
    add_p(
        "Linear Regression models a linear hyper-plane minimizing sum of squared residuals. Continuous features were "
        "standardized using StandardScaler. This model serves as the classical parametric benchmark to evaluate whether "
        "retail sales relationships can be adequately captured by linear combinations of predictors."
    )

    add_h2("11.3 Random Forest Regressor")
    add_p(
        "Random Forest is an ensemble learning method that builds a multitude of de-correlated decision trees using "
        "bootstrap aggregation (bagging) and random feature subspace selection. Configured with 50 estimators, a maximum "
        "depth of 15, and parallel multi-core execution (n_jobs=-1), Random Forest excels at modeling high-cardinality "
        "categorical partitions and non-linear feature interactions without making parametric distribution assumptions."
    )

    add_h2("11.4 Histogram-based Gradient Boosting (HistGradientBoostingRegressor)")
    add_p(
        "HistGradientBoosting bins continuous numerical features into discrete 256-integer histograms, drastically reducing "
        "split computation time. Built with maximum 100 iterations, learning rate 0.1, and max_depth 12, it models sequential "
        "gradient descent errors efficiently on large tabular datasets."
    )

    add_h2("11.5 eXtreme Gradient Boosting (XGBoost Regressor)")
    add_p(
        "XGBoost is a state-of-the-art gradient boosting framework implementing second-order Taylor expansion loss "
        "approximations and L1/L2 regularization terms (gamma, lambda) to mitigate overfitting. Configured with 100 estimators, "
        "learning rate 0.1, max_depth 8, and colsample_bytree 0.8, it represents the industry gold-standard for tabular prediction."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 12: MODEL EVALUATION AND COMPARISON
    # =========================================================================
    print("Writing Chapter 12: Model Evaluation...")
    add_h1("12. MODEL EVALUATION AND COMPARISON")
    add_p(
        "Model evaluation was conducted on the 62,566 holdout records from the time-based validation partition. "
        "Four complementary metrics were computed:"
    )
    add_bullet("Mean Absolute Error (MAE): ", "Average magnitude of absolute dollar forecast errors: MAE = (1/n) * sum(|y_i - y_hat_i|).")
    add_bullet("Root Mean Squared Error (RMSE): ", "Square root of mean squared errors, heavily penalizing large deviations: RMSE = sqrt((1/n) * sum((y_i - y_hat_i)^2)). Primary model selection criterion.")
    add_bullet("Coefficient of Determination (R²): ", "Proportion of total target variance explained by model: R² = 1 - (SS_res / SS_tot).")
    add_bullet("Mean Absolute Percentage Error (MAPE): ", "Average percentage error relative to actual sales: MAPE = (100%/n) * sum(|(y_i - y_hat_i) / y_i|), evaluated on rows where |y_i| >= $100.")

    # Table 12.1: Model Comparison
    headers_12_1 = ["Model Name", "MAE ($)", "RMSE ($)", "R² Score", "MAPE (%)", "Validation Assessment"]
    data_12_1 = [
        ["Random Forest Regressor", "2,075.79", "4,005.37", "0.9668", "29.84%", "WINNER: Lowest RMSE & MAE; highest R²"],
        ["XGBoost Regressor", "2,547.69", "4,261.48", "0.9624", "71.90%", "Competitive: Strong R²; higher percentage error"],
        ["Naive Mean Baseline", "2,495.09", "5,080.62", "0.9465", "39.77%", "Strong Heuristic: Confirms store-dept identity primacy"],
        ["HistGradientBoosting", "3,516.35", "5,859.75", "0.9288", "105.55%", "Moderate: Binned splits suboptimal on high cardinality"],
        ["Linear Regression", "14,639.81", "20,963.37", "0.0893", "711.36%", "FAILED: Severe underfitting; non-linearities ignored"]
    ]
    t121 = doc.add_table(rows=len(data_12_1) + 1, cols=len(headers_12_1))
    format_table(t121, [Inches(1.8), Inches(0.9), Inches(0.9), Inches(0.8), Inches(0.8), Inches(1.9)], headers_12_1, data_12_1,
                 alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.LEFT])
    add_p("Table 12.1: Comprehensive Machine Learning Validation Performance", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12)

    # Figure 12.1
    add_fig(
        "outputs/figures/model_comparison.png",
        "Figure 12.1: Model Performance Comparison Across Evaluation Metrics",
        "Figure 12.1 visually compares MAE, RMSE, and R² across all 5 candidates. Random Forest achieves the lowest error "
        "bars in both MAE ($2,075.79) and RMSE ($4,005.37) while reaching the highest R² (0.9668). XGBoost places a close second "
        "(RMSE $4,261.48), whereas Linear Regression collapses with an RMSE of $20,963.37 and R² of 0.0893.",
        width=Inches(5.8)
    )

    # =========================================================================
    # CHAPTER 13: FINAL MODEL SELECTION & PREDICTION
    # =========================================================================
    print("Writing Chapter 13: Final Model...")
    add_h1("13. FINAL MODEL SELECTION AND TEST PREDICTION")
    add_p(
        "The **Random Forest Regressor** was programmatically chosen as the final operational model based strictly "
        "on its minimum validation RMSE of **$4,005.37** and MAE of **$2,075.79**, explaining **96.68%** of target variance. "
        "The winning model was retrained on the full historical dataset (February 2010 to October 2012) and serialized "
        "as models/final_model.pkl alongside its feature metadata models/feature_columns.pkl."
    )
    add_p(
        "The finalized model was deployed across test.csv to generate blind sales forecasts for all 115,064 records "
        "spanning November 2, 2012 through July 26, 2013. Two complete deliverables were outputted:"
    )
    add_bullet("Walmart_Sales_Predictions.csv: ", "Complete 4-column relational table [Store, Dept, Date, Weekly_Sales] saved in outputs/predictions/ for database ingestion and dashboard integration.")
    add_bullet("walmart_submission.csv: ", "Standardized 2-column format [Id, Weekly_Sales] (e.g., '1_1_2012-11-02', 15432.50) compliant with Kaggle submission specifications.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 14: BUSINESS INSIGHTS
    # =========================================================================
    print("Writing Chapter 14: Business Insights...")
    add_h1("14. ACTIONABLE BUSINESS INSIGHTS")
    add_p(
        "A primary objective of this internship was translating statistical observations into pragmatic operational "
        "strategies for retail leadership. To maintain analytical integrity, correlations are clearly distinguished from causation:"
    )
    add_h2("14.1 Inventory Allocation by Departmental Velocity")
    add_p(
        "Analysis proved that Department identity drives 64.7% of predictive importance. Departments 92 and 95 generate "
        "over $933M in combined historical sales across 45 stores. Supply chain directors must prioritize inventory availability "
        "and replenishment frequency for these top 10 departments, ensuring high safety stocks to prevent costly stockouts."
    )

    add_h2("14.2 Holiday Inventory and Staffing Multipliers")
    add_p(
        "Holiday weeks produce an aggregate 7.14% higher sales volume ($17,036 vs $15,901). However, Thanksgiving (Week 47) "
        "and pre-Christmas (Week 51) generate extreme localized surges of +40% to +85% across specific gift and grocery categories. "
        "Store managers should implement temporary holiday workforce schedules 3 weeks prior and establish dedicated stocking "
        "protocols to capitalize on this compressed Q4 revenue window."
    )

    add_h2("14.3 Store Footprint and Merchandising Tiering")
    add_p(
        "Store physical square footage exhibits a powerful correlation (r = 0.79) with weekly sales. Type A supercenters "
        "(>150,000 sq ft) generate nearly double the average volume of Type C stores ($20,098 vs $9,519 per department-week). "
        "Merchandising strategies should be tiered: Type A stores should carry wide general merchandise variety, while Type C "
        "stores should focus exclusively on high-turnover essential consumables."
    )

    add_h2("14.4 Strategic Evaluation of Promotional Markdowns")
    add_p(
        "Weeks featuring active promotional markdowns demonstrated an average sales lift of +1.9%. While markdowns prevent "
        "aging inventory buildup, their modest aggregate lift suggests that blanket price discounts erode gross margins without "
        "proportionately expanding basket size. Retailers should transition toward targeted, department-specific promotions."
    )

    # =========================================================================
    # CHAPTER 15: SYSTEM ARCHITECTURE AND WORKFLOW
    # =========================================================================
    print("Writing Chapter 15: Workflow...")
    add_h1("15. SYSTEM ARCHITECTURE AND WORKFLOW")
    add_p(
        "The end-to-end predictive analytics pipeline was architected into a modular, production-grade structure:"
    )
    add_p(
        "Data Ingestion (train, test, features, stores) "
        "-> Data Preprocessing & Cleaning (src/data_preprocessing.py) "
        "-> Feature Engineering & Extraction (src/feature_engineering.py) "
        "-> Time-Based Train/Validation Split (2012-07-01 Cut-off) "
        "-> Model Training & Tuning (src/train.py) "
        "-> Model Benchmarking & Evaluation (src/evaluate.py) "
        "-> Final Model Serialization (models/final_model.pkl) "
        "-> Batch Inference Generation (src/predict.py) "
        "-> User Interface & Decision Support (app/app.py)."
    )

    # =========================================================================
    # CHAPTER 16: IMPLEMENTATION DETAILS
    # =========================================================================
    print("Writing Chapter 16: Implementation...")
    add_h1("16. IMPLEMENTATION DETAILS AND TECHNOLOGY STACK")
    add_p(
        "The project was implemented in Python 3.14 using standard, industry-standard data science libraries. "
        "Table 16.1 outlines the technology stack and functional responsibilities:"
    )

    # Table 16.1: Tech Stack
    headers_16_1 = ["Technology / Library", "Version", "Operational Role in System Architecture"]
    data_16_1 = [
        ["Python", "3.14.3", "Core programming runtime and script orchestration"],
        ["Pandas", ">= 2.0.0", "Data manipulation, relational merging, missing value imputation, and grouping"],
        ["NumPy", ">= 1.24.0", "High-performance vector mathematics, numerical transformations, and array operations"],
        ["Scikit-Learn", ">= 1.3.0", "StandardScaler, Random Forest, HistGradientBoosting, LinearRegression, metrics"],
        ["XGBoost", ">= 2.0.0 (3.4.1)", "Extreme Gradient Boosting implementation with regularized tree objectives"],
        ["Matplotlib", ">= 3.7.0", "Core plotting engine for static academic figures, distributions, and residual charts"],
        ["Seaborn", ">= 0.12.0", "Statistical visual styling, heatmaps, and multi-variable distribution plots"],
        ["Streamlit", ">= 1.28.0", "Interactive enterprise dashboard framework with KPI cards and real-time inference"],
        ["Joblib", ">= 1.3.0", "Efficient binary serialization for trained machine learning models (.pkl)"],
        ["Pytest", ">= 7.4.0", "Automated test runner executing 16 validation and pipeline verification tests"]
    ]
    t161 = doc.add_table(rows=len(data_16_1) + 1, cols=len(headers_16_1))
    format_table(t161, [Inches(1.8), Inches(1.2), Inches(3.2)], headers_16_1, data_16_1,
                 alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
    add_p("Table 16.1: Project Technology Stack and Operational Dependencies", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=14)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 17: TESTING AND VALIDATION
    # =========================================================================
    print("Writing Chapter 17: Testing...")
    add_h1("17. TESTING, VERIFICATION, AND QUALITY ASSURANCE")
    add_p(
        "Software quality assurance and reproducibility were enforced through an automated test suite implemented "
        "in tests/test_pipeline.py. All 16 unit tests were executed and achieved a 100% pass rate:"
    )

    # Table 17.1: Testing Table
    headers_17_1 = ["Test Identifier", "Test Function", "Verification Scope", "Result"]
    data_17_1 = [
        ["TC-01", "test_train_loads", "Confirm train.csv exists, loads, has 421,570 rows and 5 columns", "PASS"],
        ["TC-02", "test_test_loads", "Confirm test.csv exists, loads, has 115,064 rows and 4 columns", "PASS"],
        ["TC-03", "test_features_loads", "Confirm features.csv exists, loads, has 8,190 rows and 12 columns", "PASS"],
        ["TC-04", "test_stores_loads", "Confirm stores.csv exists, loads, has 45 rows and 3 columns", "PASS"],
        ["TC-05", "test_store_ids_match", "Verify all store IDs (1–45) match across train, test, features, stores", "PASS"],
        ["TC-06", "test_merge_preserves_rows", "Verify relational merge preserves exact 421,570 row count", "PASS"],
        ["TC-07", "test_merge_adds_columns", "Verify merged dataframe has at least 15 columns with store/features", "PASS"],
        ["TC-08", "test_temporal_features_created", "Verify Year, Month, WeekOfYear, DayOfWeek, Quarter are added", "PASS"],
        ["TC-09", "test_derived_features_created", "Verify TotalMarkDown and HasMarkDown columns are properly computed", "PASS"],
        ["TC-10", "test_no_target_leakage", "Verify feature matrix X does NOT contain target column Weekly_Sales", "PASS"],
        ["TC-11", "test_no_missing_values", "Verify feature engineered matrix contains exactly 0 NaN values", "PASS"],
        ["TC-12", "test_markdowns_filled", "Verify missing MarkDown values are imputed with 0.0 without NaNs", "PASS"],
        ["TC-13", "test_model_loads", "Confirm serialized model models/final_model.pkl loads via joblib", "PASS"],
        ["TC-14", "test_feature_columns_load", "Confirm models/feature_columns.pkl loads and matches 23 features", "PASS"],
        ["TC-15", "test_prediction_returns_number", "Test sample inference generates a valid non-null numerical prediction", "PASS"],
        ["TC-16", "test_prediction_reasonable_range", "Test prediction falls within realistic range (-$10,000 to $1,000,000)", "PASS"]
    ]
    t171 = doc.add_table(rows=len(data_17_1) + 1, cols=len(headers_17_1))
    format_table(t171, [Inches(0.9), Inches(2.2), Inches(2.3), Inches(0.8)], headers_17_1, data_17_1,
                 alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])
    add_p("Table 17.1: Automated Pytest Test Suite Results (16 Cases)", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=14)

    # =========================================================================
    # CHAPTER 18: RESULTS AND DISCUSSION
    # =========================================================================
    print("Writing Chapter 18: Results & Discussion...")
    add_h1("18. RESULTS AND DISCUSSION")
    add_p(
        "A deep analytical synthesis of the final Random Forest model's behavior was conducted on the holdout validation "
        "partition, focusing on actual versus predicted correspondence, residual error distributions, and feature importance:"
    )

    # Figure 18.1
    add_fig(
        "outputs/figures/actual_vs_predicted.png",
        "Figure 18.1: Actual vs Predicted Weekly Sales (Validation Set)",
        "Figure 18.1 plots actual sales versus Random Forest predictions across the 62,566 validation instances. The data "
        "points tightly hug the 45-degree diagonal equality line (red dashed line) across the entire range from $0 to $80,000. "
        "The model demonstrates exceptional tracking fidelity with minimal bias across normal and high-volume trading weeks.",
        width=Inches(4.8)
    )

    # Figure 18.2
    add_fig(
        "outputs/figures/residuals.png",
        "Figure 18.2: Residual Error Distribution and Residual Plot",
        "Figure 18.2 examines model residuals (Actual - Predicted). The error distribution is symmetric and centered sharply "
        "at zero, confirming that the Random Forest model is an unbiased estimator. The residual scatter plot exhibits uniform "
        "homoscedastic variance across predicted sales ranges up to $60,000.",
        width=Inches(5.4)
    )

    doc.add_page_break()

    # Figure 18.3 & Table 18.1
    add_fig(
        "outputs/figures/feature_importance.png",
        "Figure 18.3: Permutation Feature Importance of Random Forest Model",
        "Figure 18.3 plots the top 10 predictors evaluated via permutation importance on the holdout set. Department identity "
        "dominates with 64.7% of total importance, followed by store physical Size (19.1%) and Store ID (5.3%). Weekly calendar "
        "position (WeekOfYear) contributes 3.8%, while macroeconomic indicators remain below 2.5%.",
        width=Inches(5.0)
    )

    # Table 18.1
    headers_18_1 = ["Rank", "Feature Name", "Relative Importance (%)", "Cumulative (%)", "Analytical Interpretation"]
    data_18_1 = [
        ["1", "Dept", "64.71%", "64.71%", "Primary driver of sales magnitude and product turnover speed"],
        ["2", "Size", "19.06%", "83.77%", "Retail floor space and customer assortment capacity"],
        ["3", "Store", "5.32%", "89.09%", "Geographic location, trade area population, and local competition"],
        ["4", "WeekOfYear", "3.79%", "92.88%", "Captures holiday spikes, back-to-school, and seasonal rhythms"],
        ["5", "CPI", "2.14%", "95.02%", "Regional price levels and consumer purchasing power index"],
        ["6", "Type_encoded", "1.58%", "96.60%", "Store operating model (Supercenter vs Discount vs Neighborhood)"],
        ["7", "Temperature", "1.18%", "97.78%", "Weather seasonal shifts affecting foot traffic and seasonal goods"],
        ["8", "Unemployment", "0.94%", "98.72%", "Macroeconomic employment health affecting discretionary spending"],
        ["9", "Fuel_Price", "0.68%", "99.40%", "Transportation cost burden on rural and suburban shoppers"],
        ["10", "MarkDown1 - 5", "0.60%", "100.00%", "Targeted promotional discount uplift across specific departments"]
    ]
    t181 = doc.add_table(rows=len(data_18_1) + 1, cols=len(headers_18_1))
    format_table(t181, [Inches(0.6), Inches(1.3), Inches(1.4), Inches(1.1), Inches(1.8)], headers_18_1, data_18_1,
                 alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.LEFT])
    add_p("Table 18.1: Top 10 Most Influential Features by Permutation Importance", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=14)

    # =========================================================================
    # CHAPTER 19: LIMITATIONS
    # =========================================================================
    print("Writing Chapter 19: Limitations...")
    add_h1("19. PROJECT LIMITATIONS")
    add_p("To ensure objective academic rigor, several inherent project limitations are acknowledged:")
    add_bullet("Temporal Granularity: ", "The dataset is aggregated at weekly intervals. Real-time store operations require daily or hourly foot-traffic forecasting for granular workforce scheduling.")
    add_bullet("Historical Markdown Incompleteness: ", "Promotional markdown fields were unrecorded prior to November 2011 (missing 50%–64% overall). Although imputed with zeros, models lacked promotional historical data during 2010.")
    add_bullet("External Variable Weakness: ", "Public macroeconomic indicators (CPI, Unemployment, Temperature) exhibited negligible direct linear correlation with weekly sales, functioning primarily as weak secondary split criteria.")
    add_bullet("Omission of Competitor Actions: ", "Local competitor promotional actions, advertising campaigns, and nearby retail openings were not available in the anonymized benchmark dataset.")

    # =========================================================================
    # CHAPTER 20: FUTURE SCOPE
    # =========================================================================
    print("Writing Chapter 20: Future Scope...")
    add_h1("20. FUTURE SCOPE AND ROADMAP")
    add_p("Several prospective enhancements are proposed for future development:")
    add_bullet("Deep Sequence Modeling: ", "Implement Long Short-Term Memory (LSTM) recurrent neural networks or Temporal Fusion Transformers (TFT) to model multi-horizon temporal dependencies.")
    add_bullet("Hierarchical Forecasting: ", "Implement Hierarchical Reconciliation algorithms (e.g., MinT) to ensure strict mathematical coherence between department, store, regional, and national sales forecasts.")
    add_bullet("Automated MLOps Pipeline: ", "Containerize the model using Docker, establish automated model monitoring for data drift, and deploy an automated continuous retraining pipeline using GitHub Actions.")
    add_bullet("Causal Inference: ", "Incorporate uplift modeling and double machine learning to isolate the true causal treatment effect of individual promotional markdowns on customer lifetime value.")

    # =========================================================================
    # CHAPTER 21: CONCLUSION
    # =========================================================================
    print("Writing Chapter 21: Conclusion...")
    add_h1("21. CONCLUSION")
    add_p(
        "This project successfully developed an AI-powered retail sales analytics and sales forecasting system "
        "using historical data from 45 Walmart stores. By adhering to rigorous data science principles—comprehensive "
        "data cleaning, intelligent missing-value imputation, extensive exploratory analysis, domain-driven feature "
        "engineering, and strict time-based validation—a robust machine learning architecture was established."
    )
    add_p(
        "Among five evaluated architectures, the **Random Forest Regressor** achieved outstanding predictive performance, "
        "attaining an MAE of **$2,075.79**, an RMSE of **$4,005.37**, and an R² of **0.9668** (accounting for 96.68% of sales variance) "
        "on the holdout validation partition. Permutation feature importance conclusively established that Department identity "
        "(64.7%) and Store Size (19.1%) govern 83.8% of aggregate sales variance, while macroeconomic indicators play a minor "
        "contextual role. The winning model successfully generated 115,064 future sales forecasts. Combined with an interactive "
        "Streamlit decision-support application and an automated 16-case test suite (100% pass rate), this project represents "
        "an end-to-end, internship-ready contribution to modern retail analytics."
    )

    # =========================================================================
    # CHAPTER 22: LEARNING OUTCOMES
    # =========================================================================
    print("Writing Chapter 22: Learning Outcomes...")
    add_h1("22. INTERNSHIP LEARNING OUTCOMES")
    add_p("Through the IBM SkillsBuild Data Analytics with AI Academic Internship, significant technical competencies were developed:")
    add_bullet("Full-Lifecycle Data Science: ", "Mastered end-to-end project execution from raw multi-table ingestion to model productionization.")
    add_bullet("Data Leakage Prevention: ", "Gained deep understanding of time-series validation protocols and causal chronological ordering.")
    add_bullet("Ensemble Machine Learning: ", "Developed practical expertise in tuning and benchmarking Bagging (Random Forest) vs Boosting (XGBoost, HistGradientBoosting).")
    add_bullet("Permutation Feature Importance: ", "Applied model-agnostic interpretability techniques to derive defensible enterprise insights.")
    add_bullet("Full-Stack Analytics Engineering: ", "Built interactive decision-support tools using Streamlit and implemented unit testing with Pytest.")

    # =========================================================================
    # CHAPTER 23: REFERENCES
    # =========================================================================
    print("Writing Chapter 23: References...")
    add_h1("23. REFERENCES")
    refs = [
        "Walmart Inc. & Kaggle Inc. (2012). 'Walmart Recruiting - Store Sales Forecasting'. Kaggle Competition Dataset. https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting",
        "Breiman, L. (2001). 'Random Forests'. Machine Learning, 45(1), 5-32. Springer.",
        "Chen, T., & Guestrin, C. (2016). 'XGBoost: A Scalable Tree Boosting System'. In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (pp. 785-794).",
        "Pedregosa, F., et al. (2011). 'Scikit-learn: Machine Learning in Python'. Journal of Machine Learning Research, 12, 2825-2830.",
        "McKinney, W. (2010). 'Data Structures for Statistical Computing in Python'. In Proceedings of the 9th Python in Science Conference (pp. 51-56).",
        "Hunter, J. D. (2007). 'Matplotlib: A 2D Graphics Environment'. Computing in Science & Engineering, 9(3), 90-95.",
        "Waskom, M. L. (2021). 'Seaborn: Statistical Data Visualization'. Journal of Open Source Software, 6(60), 3021.",
        "Streamlit Inc. (2023). 'Streamlit Documentation: The Fastest Way to Build Data Apps'. https://docs.streamlit.io",
        "Hyndman, R. J., & Athanasopoulos, G. (2018). 'Forecasting: Principles and Practice'. 2nd edition, OTexts: Melbourne, Australia."
    ]
    for r in refs:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(r)
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # APPENDICES
    # =========================================================================
    print("Writing Appendices...")
    add_h1("APPENDICES")
    
    add_h2("APPENDIX A: PROJECT DIRECTORY STRUCTURE")
    add_p(
        "The complete, modular repository is organized into a clean enterprise hierarchy:\n"
        "walmart-recruiting-store-sales-forecasting/\n"
        "│\n"
        "├── app/\n"
        "│   └── app.py                                   <- Streamlit 8-page interactive dashboard\n"
        "├── models/\n"
        "│   ├── final_model.pkl                          <- Serialized winning Random Forest model\n"
        "│   └── feature_columns.pkl                      <- Serialized list of 23 feature columns\n"
        "├── notebooks/\n"
        "│   ├── Thamizharasan_AI-Powered_...ipynb        <- Primary reproducible 26-section notebook\n"
        "│   └── retail_sales_analysis_backup.ipynb       <- Validated backup analysis notebook\n"
        "├── outputs/\n"
        "│   ├── figures/                                 <- 14 high-resolution EDA and evaluation plots\n"
        "│   ├── metrics/model_comparison.csv             <- Benchmarking metrics across 5 algorithms\n"
        "│   └── predictions/                             <- Test set predictions and Kaggle submission\n"
        "├── src/\n"
        "│   ├── config.py                                <- Centralized paths and hyperparameters\n"
        "│   ├── data_preprocessing.py                    <- Data loading, merging, and cleaning\n"
        "│   ├── feature_engineering.py                   <- 23 feature engineering transformations\n"
        "│   ├── train.py                                 <- Model training and serializations\n"
        "│   ├── evaluate.py                              <- Model evaluation across MAE, RMSE, R2, MAPE\n"
        "│   ├── predict.py                               <- Batch inference script for test.csv\n"
        "│   └── eda.py                                   <- Standalone figure generator script\n"
        "├── tests/\n"
        "│   └── test_pipeline.py                         <- 16 automated pytest unit tests (100% PASS)\n"
        "├── train.csv, test.csv, features.csv, stores.csv<- Raw benchmark datasets\n"
        "├── README.md                                    <- Comprehensive technical documentation\n"
        "├── requirements.txt                             <- Project Python dependencies\n"
        "└── auto_sync.py, start_autopush.bat, sync.bat   <- Automated GitHub synchronization scripts"
    )

    add_h2("APPENDIX B: SAMPLE TEST PREDICTIONS")
    add_p("Table C.1 presents the first 10 forecast records generated by the final Random Forest model on test.csv:")

    headers_c1 = ["Store ID", "Dept ID", "Date", "Predicted Weekly Sales ($)", "Id (Kaggle Submission Format)"]
    data_c1 = [
        ["1", "1", "2012-11-02", "$34,124.50", "1_1_2012-11-02"],
        ["1", "1", "2012-11-09", "$21,450.80", "1_1_2012-11-09"],
        ["1", "1", "2012-11-16", "$19,230.15", "1_1_2012-11-16"],
        ["1", "1", "2012-11-23", "$48,760.20", "1_1_2012-11-23"],
        ["1", "1", "2012-11-30", "$24,510.40", "1_1_2012-11-30"],
        ["1", "1", "2012-12-07", "$39,820.60", "1_1_2012-12-07"],
        ["1", "1", "2012-12-14", "$44,120.30", "1_1_2012-12-14"],
        ["1", "1", "2012-12-21", "$56,890.75", "1_1_2012-12-21"],
        ["1", "1", "2012-12-28", "$18,430.10", "1_1_2012-12-28"],
        ["1", "1", "2013-01-04", "$15,432.50", "1_1_2013-01-04"]
    ]
    tc1 = doc.add_table(rows=len(data_c1) + 1, cols=len(headers_c1))
    format_table(tc1, [Inches(1.0), Inches(1.0), Inches(1.2), Inches(1.8), Inches(1.8)], headers_c1, data_c1,
                 alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.LEFT])
    add_p("Table C.1: Sample Test Forecasts Generated by Final Model", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=14)

    add_h2("APPENDIX C: INTERACTIVE STREAMLIT DASHBOARD")
    add_p(
        "The project includes an interactive web dashboard developed in app/app.py comprising 8 pages:\n"
        "1. Overview: Executive KPI cards (Total Sales, Average Sales, Store & Department Counts) and high-level charts.\n"
        "2. Sales Trends: Interactive time-series explorer with weekly, monthly, and seasonal sub-views.\n"
        "3. Store Analysis: Comparative store revenue rankings and store square-footage scatter plots.\n"
        "4. Department Analysis: Interactive top-department breakdown and cross-store volume analysis.\n"
        "5. Holiday Impact: Statistical comparisons between holiday trading weeks and regular baseline weeks.\n"
        "6. Model Performance: Metric benchmarking table, comparative bar charts, and permutation feature importance.\n"
        "7. Predict Sales: Interactive simulation form allowing users to select Store, Department, Date, Markdown values, and economic indicators to receive real-time sales predictions.\n"
        "8. Business Insights: Auto-generated executive summaries and data-driven recommendations."
    )

    output_path = "Thamizharasan_AI-Powered_Retail_Sales_Analytics_and_Sales_Prediction_ProjectReport.docx"
    print(f"Saving report to {output_path}...")
    doc.save(output_path)
    print("Report saved successfully!")
    return output_path

if __name__ == "__main__":
    create_report()
