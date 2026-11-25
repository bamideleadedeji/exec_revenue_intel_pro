"""
Executive Revenue & Performance Intelligence Suite (v2.0)
Computes Rule of 40, Net Dollar Retention (NDR), LTV:CAC Ratio, CAC Payback, and Budget vs. Actual Variances.
"""

import pandas as pd

DEFAULT_SEGMENTS = [
    {"Segment": "North America Enterprise", "Prior_ARR_USD": 1850000.0, "Actual_ARR_USD": 2340000.0, "Budget_ARR_USD": 2250000.0, "Expansion_ARR_USD": 310000.0, "Churned_ARR_USD": 95000.0, "Gross_Margin_Pct": 78.5, "EBITDA_Margin_Pct": 18.2, "New_Customers": 42, "Sales_Marketing_Spend_USD": 410000.0, "Avg_Customer_Lifespan_Yrs": 4.5},
    {"Segment": "EMEA Commercial", "Prior_ARR_USD": 920000.0, "Actual_ARR_USD": 1140000.0, "Budget_ARR_USD": 1180000.0, "Expansion_ARR_USD": 125000.0, "Churned_ARR_USD": 68000.0, "Gross_Margin_Pct": 74.0, "EBITDA_Margin_Pct": 12.5, "New_Customers": 31, "Sales_Marketing_Spend_USD": 265000.0, "Avg_Customer_Lifespan_Yrs": 3.8},
    {"Segment": "APAC Growth", "Prior_ARR_USD": 480000.0, "Actual_ARR_USD": 645000.0, "Budget_ARR_USD": 600000.0, "Expansion_ARR_USD": 74000.0, "Churned_ARR_USD": 29000.0, "Gross_Margin_Pct": 71.5, "EBITDA_Margin_Pct": 9.8, "New_Customers": 26, "Sales_Marketing_Spend_USD": 175000.0, "Avg_Customer_Lifespan_Yrs": 3.5},
    {"Segment": "SMB Self-Serve", "Prior_ARR_USD": 610000.0, "Actual_ARR_USD": 710000.0, "Budget_ARR_USD": 730000.0, "Expansion_ARR_USD": 48000.0, "Churned_ARR_USD": 72000.0, "Gross_Margin_Pct": 81.0, "EBITDA_Margin_Pct": 22.0, "New_Customers": 145, "Sales_Marketing_Spend_USD": 195000.0, "Avg_Customer_Lifespan_Yrs": 2.9},
]


def analyze_executive_revenue(df: pd.DataFrame) -> dict:
    work = df.copy()
    yoy_growth_list, var_usd_list, var_pct_list, ndr_list = [], [], [], []
    rule40_list, cac_list, ltv_cac_list, payback_months_list, status_list = [], [], [], [], []

    for _, row in work.iterrows():
        prior = max(float(row.get("Prior_ARR_USD", 1.0)), 1.0)
        actual = float(row.get("Actual_ARR_USD", 0.0))
        budget = max(float(row.get("Budget_ARR_USD", actual)), 1.0)
        exp_arr = float(row.get("Expansion_ARR_USD", 0.0))
        churn_arr = float(row.get("Churned_ARR_USD", 0.0))
        gm_pct = float(row.get("Gross_Margin_Pct", 75.0))
        ebitda_pct = float(row.get("EBITDA_Margin_Pct", 15.0))
        new_cust = max(float(row.get("New_Customers", 1.0)), 1.0)
        sm_spend = float(row.get("Sales_Marketing_Spend_USD", 0.0))
        life_yrs = float(row.get("Avg_Customer_Lifespan_Yrs", 3.5))

        yoy_g = round((actual - prior) / prior * 100.0, 1)
        var_usd = round(actual - budget, 2)
        var_pct = round(var_usd / budget * 100.0, 1)
        ndr = round((prior + exp_arr - churn_arr) / prior * 100.0, 1)
        rule40 = round(yoy_g + ebitda_pct, 1)

        cac = round(sm_spend / new_cust, 2)
        net_new_arr = max(actual - prior + churn_arr, 1.0)
        arpa = net_new_arr / new_cust
        gross_margin_frac = max(gm_pct / 100.0, 0.05)
        ltv = arpa * gross_margin_frac * life_yrs
        ltv_cac = round(ltv / max(cac, 1.0), 2)
        payback = round(cac / max((arpa * gross_margin_frac) / 12.0, 1.0), 1)

        if rule40 >= 40.0 and var_usd >= 0:
            flag = "OUTPERFORMING (Rule of 40+)"
        elif rule40 >= 32.0:
            flag = "ON TRACK"
        else:
            flag = "WATCH VARIANCE / EFFICIENCY"

        yoy_growth_list.append(yoy_g)
        var_usd_list.append(var_usd)
        var_pct_list.append(var_pct)
        ndr_list.append(ndr)
        rule40_list.append(rule40)
        cac_list.append(cac)
        ltv_cac_list.append(ltv_cac)
        payback_months_list.append(payback)
        status_list.append(flag)

    work["YoY_Growth_Pct"] = yoy_growth_list
    work["Budget_Variance_USD"] = var_usd_list
    work["Budget_Variance_Pct"] = var_pct_list
    work["NDR_Pct"] = ndr_list
    work["Rule_Of_40"] = rule40_list
    work["CAC_USD"] = cac_list
    work["LTV_to_CAC"] = ltv_cac_list
    work["CAC_Payback_Months"] = payback_months_list
    work["Board_Status"] = status_list

    tot_prior = max(float(work["Prior_ARR_USD"].sum()), 1.0)
    tot_actual = float(work["Actual_ARR_USD"].sum())
    tot_budget = float(work["Budget_ARR_USD"].sum())
    port_growth = round((tot_actual - tot_prior) / tot_prior * 100.0, 1)
    avg_ebitda = round(float(work["EBITDA_Margin_Pct"].mean()), 1)

    return {
        "df": work,
        "total_arr": round(tot_actual, 2),
        "total_variance": round(tot_actual - tot_budget, 2),
        "portfolio_growth_pct": port_growth,
        "portfolio_rule40": round(port_growth + avg_ebitda, 1),
        "avg_ndr_pct": round(float(work["NDR_Pct"].mean()), 1),
        "avg_ltv_cac": round(float(work["LTV_to_CAC"].mean()), 2),
    }
