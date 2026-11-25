"""
Executive Revenue & Performance Intelligence Suite (v2.0)
Board-Level ARR Growth, Rule of 40, Net Dollar Retention (NDR), LTV:CAC & Variance Analytics
"""

import io
from datetime import datetime, timezone
import streamlit as st
import pandas as pd
import plotly.express as px
from revenue_intel_engine import DEFAULT_SEGMENTS, analyze_executive_revenue

st.set_page_config(page_title="Executive Revenue & Performance Intelligence Suite", page_icon="📊", layout="wide")
st.title("📊 Executive Revenue & Performance Intelligence Suite")
st.caption("Board ARR & Budget Variance Analytics • Rule of 40 • Net Dollar Retention (NDR) • LTV:CAC & Payback Period • Excel Board Pack")
st.divider()

uploaded = st.sidebar.file_uploader("Upload Custom Segment / Regional Revenue Sheet (.csv or .xlsx)", type=["csv", "xlsx"])
base_df = (pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)) if uploaded else pd.DataFrame(DEFAULT_SEGMENTS)

st.subheader("Interactive Regional & Business-Unit Revenue Performance Ledger")
st.caption("Edit ARR actuals, expansion/churn, margins, or S&M spend below to recalculate board KPIs instantaneously.")
edited_df = st.data_editor(base_df, width="stretch", num_rows="dynamic")

res = analyze_executive_revenue(edited_df)
out_df = res["df"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Ending ARR", f"${res['total_arr']:,.0f}", delta=f"Budget Var: ${res['total_variance']:+,.0f}")
c2.metric("Portfolio Rule of 40", f"{res['portfolio_rule40']:.1f}%", delta=f"YoY Growth: {res['portfolio_growth_pct']:.1f}%")
c3.metric("Avg Net Dollar Retention", f"{res['avg_ndr_pct']:.1f}%", delta="Benchmark >= 110%")
c4.metric("Avg LTV : CAC Ratio", f"{res['avg_ltv_cac']:.2f}x", delta="Institutional Target >= 3.0x")

tab1, tab2, tab3 = st.tabs(["📋 Executive Segment Scorecard", "📈 ARR, Rule of 40 & LTV:CAC Charts", "📥 3-Sheet Excel Board Pack"])

with tab1:
    st.dataframe(out_df[["Segment", "Actual_ARR_USD", "Budget_Variance_USD", "YoY_Growth_Pct", "NDR_Pct", "Rule_Of_40", "CAC_USD", "LTV_to_CAC", "CAC_Payback_Months", "Board_Status"]], width="stretch")

with tab2:
    col1, col2 = st.columns(2)
    col1.plotly_chart(px.bar(out_df, x="Segment", y=["Prior_ARR_USD", "Actual_ARR_USD", "Budget_ARR_USD"], barmode="group", title="Prior vs. Actual vs. Budget ARR by Segment ($)"), width="stretch")
    col2.plotly_chart(px.bar(out_df, x="Segment", y="Rule_Of_40", color="Board_Status", title="Rule of 40 Score by Business Unit (%)"), width="stretch")

with tab3:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        pd.DataFrame([
            {"Board_Metric": "Report Generated (UTC)", "Value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")},
            {"Board_Metric": "Total Ending ARR ($)", "Value": f"${res['total_arr']:,.2f}"},
            {"Board_Metric": "Net Budget Variance ($)", "Value": f"${res['total_variance']:+,.2f}"},
            {"Board_Metric": "Portfolio YoY ARR Growth (%)", "Value": f"{res['portfolio_growth_pct']:.1f}%"},
            {"Board_Metric": "Portfolio Rule of 40 Score (%)", "Value": f"{res['portfolio_rule40']:.1f}%"},
            {"Board_Metric": "Average Net Dollar Retention (%)", "Value": f"{res['avg_ndr_pct']:.1f}%"},
            {"Board_Metric": "Average LTV : CAC Ratio", "Value": f"{res['avg_ltv_cac']:.2f}x"},
        ]).to_excel(writer, sheet_name="01_Board_Executive_KPIs", index=False)
        out_df.to_excel(writer, sheet_name="02_Segment_Performance", index=False)

    st.download_button("📊 Download Executive Revenue Board Pack (.xlsx)", buf.getvalue(), "Executive_Revenue_Intelligence_Board_Pack.xlsx")
