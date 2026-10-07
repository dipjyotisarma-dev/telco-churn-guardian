"""
Module: batch_audit_view.py
Purpose: Fleet-wide retention portfolio audit view. Handles CSV ingestion,
         high-performance batch scoring, Plotly fleet risk distribution donut & histogram,
         financial portfolio impact KPIs, filterable fleet table, and CSV export.
"""

from typing import Optional
from pathlib import Path
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.predict import predict_batch

# Benchmark financial metrics for portfolio calculations
BENCHMARK_LTV: float = 500.00
RAW_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "Telco-Customer-Churn.csv"


@st.cache_data(show_spinner=False)
def load_uploaded_csv(file_bytes: bytes) -> pd.DataFrame:
    """
    Parses and caches uploaded CSV file bytes.

    Parameters:
        file_bytes (bytes): Binary file content.

    Returns:
        pd.DataFrame: Parsed DataFrame.
    """
    return pd.read_csv(io.BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def load_sample_dataset() -> pd.DataFrame:
    """
    Loads a benchmark sample from the local Telco dataset for instant demonstration.

    Returns:
        pd.DataFrame: Sample DataFrame.
    """
    if RAW_DATA_PATH.exists():
        df = pd.read_csv(RAW_DATA_PATH)
        return df.head(350).copy()
    else:
        # Fallback synthetic demo DataFrame
        return pd.DataFrame([
            {
                "customerID": f"DEMO-{i:04d}",
                "gender": "Female" if i % 2 == 0 else "Male",
                "SeniorCitizen": 1 if i % 4 == 0 else 0,
                "Partner": "Yes" if i % 2 == 0 else "No",
                "Dependents": "Yes" if i % 3 == 0 else "No",
                "tenure": (i * 3) % 72 + 1,
                "PhoneService": "Yes",
                "MultipleLines": "Yes" if i % 2 == 0 else "No",
                "InternetService": "Fiber optic" if i % 2 == 0 else "DSL",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "Yes" if i % 3 == 0 else "No",
                "StreamingMovies": "Yes" if i % 3 == 0 else "No",
                "Contract": "Month-to-month" if i % 3 != 0 else "One year",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 65.0 + (i % 45),
                "TotalCharges": 120.0 + (i * 50),
            }
            for i in range(100)
        ])


def render_batch_audit_view(active_threshold: float) -> None:
    """
    Renders the Fleet Portfolio Audit workspace.

    Parameters:
        active_threshold (float): Active decision boundary probability from sidebar.
    """
    st.markdown(
        "<div class='tg-card-title'>"
        "📁 Fleet Portfolio Audit & Fleet Risk Distribution"
        "</div>",
        unsafe_allow_html=True
    )
    st.caption(
        "Upload a batch CSV file of subscriber accounts to perform portfolio-wide risk scoring, "
        "analyze fleet risk distribution, and export actionable retention intervention rosters."
    )

    # Ingestion Controls
    col_up, col_demo = st.columns([2, 1])

    with col_up:
        uploaded_file = st.file_uploader(
            "Upload Customer Accounts CSV",
            type=["csv"],
            help="Upload raw Telco subscriber file matching the production schema."
        )

    with col_demo:
        st.markdown(
            "<div style='font-size:0.8rem; font-weight:600; color:var(--tg-muted-text); margin-top:0.35rem; margin-bottom:0.4rem;'>"
            "Quick Demo Audit:"
            "</div>",
            unsafe_allow_html=True
        )
        use_sample = st.button(
            "⚡ Load Benchmark Sample (350 Accounts)",
            use_container_width=True,
            help="Instant fleet audit using 350 real subscriber records from data/raw."
        )

    # Ingest data
    df_raw: Optional[pd.DataFrame] = None
    if uploaded_file is not None:
        try:
            df_raw = load_uploaded_csv(uploaded_file.getvalue())
            st.toast(f"Ingested {len(df_raw):,} records from {uploaded_file.name}", icon="📥")
        except Exception as e:
            st.error(f"Error reading uploaded CSV: {str(e)}")
            return
    elif use_sample or st.session_state.get("batch_use_sample", False):
        st.session_state["batch_use_sample"] = True
        df_raw = load_sample_dataset()

    if df_raw is None:
        st.info("👈 Upload a CSV file or click 'Load Benchmark Sample' to inspect fleet retention risk.")
        return

    # Execute Model Inference via src.predict.predict_batch
    with st.spinner("Scoring fleet retention risk through production pipeline..."):
        try:
            df_scored = predict_batch(df_raw, threshold=active_threshold)
        except Exception as e:
            st.error(f"Batch inference failed: {str(e)}")
            return

    # Enrich with Qualitative Risk Tiers & Recommendations
    probs = df_scored["Churn_Probability"]
    conditions = [
        probs >= 0.60,
        (probs >= active_threshold) & (probs < 0.60),
        probs < active_threshold
    ]
    tiers = ["Critical Risk", "Moderate Risk", "Low Risk"]
    actions = [
        "Dispatch High-Priority Retention Offer ($50 Incentive)",
        "Dispatch Digital Engagement / Service Check-In",
        "Standard Service (No Retention Intervention Needed)"
    ]
    df_scored["Risk_Tier"] = np.select(conditions, tiers, default="Low Risk")
    df_scored["Action_Recommendation"] = np.select(conditions, actions, default="Standard Service")

    # Fleet Financial & Risk KPIs
    total_accounts = len(df_scored)
    at_risk_df = df_scored[df_scored["Churn_Risk_Flag"] == 1]
    crit_risk_df = df_scored[df_scored["Risk_Tier"] == "Critical Risk"]
    mod_risk_df = df_scored[df_scored["Risk_Tier"] == "Moderate Risk"]
    low_risk_df = df_scored[df_scored["Risk_Tier"] == "Low Risk"]

    at_risk_count = len(at_risk_df)
    at_risk_pct = (at_risk_count / total_accounts) * 100 if total_accounts > 0 else 0
    fleet_avg_prob = probs.mean() * 100 if total_accounts > 0 else 0
    at_risk_ltv = at_risk_count * BENCHMARK_LTV

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Fleet Accounts", f"{total_accounts:,}")
    with kpi2:
        st.metric(
            "Flagged Retention Risk",
            f"{at_risk_count:,} ({at_risk_pct:.1f}%)",
            delta=f"Cutoff: {active_threshold * 100:.1f}%",
            delta_color="inverse"
        )
    with kpi3:
        st.metric("At-Risk Portfolio Value", f"${at_risk_ltv:,.0f}", help=f"Based on ${BENCHMARK_LTV:.0f} benchmark LTV")
    with kpi4:
        st.metric("Fleet Avg Churn Risk", f"{fleet_avg_prob:.1f}%")

    st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)

    # Visualizations: Donut Chart + Distribution
    col_donut, col_dist = st.columns([1, 1.2])

    with col_donut:
        # Donut Chart of Risk Tiers
        tier_counts = pd.DataFrame({
            "Tier": ["Critical Risk", "Moderate Risk", "Low Risk"],
            "Count": [len(crit_risk_df), len(mod_risk_df), len(low_risk_df)],
            "Color": ["#ef4444", "#f59e0b", "#10b981"]
        })
        tier_counts = tier_counts[tier_counts["Count"] > 0]

        fig_donut = px.pie(
            tier_counts,
            names="Tier",
            values="Count",
            hole=0.55,
            color="Tier",
            color_discrete_map={
                "Critical Risk": "#ef4444",
                "Moderate Risk": "#f59e0b",
                "Low Risk": "#10b981"
            }
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="rgba(255,255,255,0.2)", width=1))
        )
        fig_donut.update_layout(
            title=dict(text="<b>Fleet Risk Distribution</b>", font=dict(size=14, color="gray")),
            height=260,
            margin=dict(l=10, r=10, t=35, b=10),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif")
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    with col_dist:
        # Histogram of churn probabilities
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df_scored["Churn_Probability"] * 100,
            nbinsx=25,
            marker_color="#0284c7",
            opacity=0.75,
            name="Subscribers"
        ))
        # Threshold cutoff line
        fig_hist.add_vline(
            x=active_threshold * 100,
            line_width=2.5,
            line_dash="dash",
            line_color="#dc2626",
            annotation_text=f"Cutoff ({active_threshold * 100:.1f}%)",
            annotation_position="top right",
            annotation_font=dict(color="#dc2626", size=11)
        )
        fig_hist.update_layout(
            title=dict(text="<b>Probability Density vs. Active Cutoff</b>", font=dict(size=14, color="gray")),
            xaxis=dict(
                title=dict(text="Predicted Churn Likelihood (%)", font=dict(color="gray", size=11)),
                tickfont=dict(color="gray", size=10),
                range=[0, 100]
            ),
            yaxis=dict(
                title=dict(text="Account Volume", font=dict(color="gray", size=11)),
                tickfont=dict(color="gray", size=10),
                showgrid=True,
                gridcolor="rgba(128,128,128,0.18)"
            ),
            height=260,
            margin=dict(l=25, r=20, t=35, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif")
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

    # Filterable Scored Fleet Table
    st.markdown("<hr style='margin: 0.75rem 0; border: none; border-top: 1px solid var(--tg-card-border);'>", unsafe_allow_html=True)
    col_t_title, col_filter, col_dl = st.columns([1.5, 1, 1])

    with col_t_title:
        st.markdown(
            "<div class='tg-card-title' style='padding-top:0.4rem;'>"
            "📋 Subscriber Retention Roster"
            "</div>",
            unsafe_allow_html=True
        )

    with col_filter:
        filter_opt = st.selectbox(
            "Filter Tier",
            options=["All Accounts", "Critical Risk (>=60%)", "Moderate Risk (>=Cutoff)", "Low Risk (<Cutoff)"],
            index=0,
            label_visibility="collapsed"
        )

    # Filter dataframe
    if filter_opt == "Critical Risk (>=60%)":
        display_df = df_scored[df_scored["Risk_Tier"] == "Critical Risk"]
    elif filter_opt == "Moderate Risk (>=Cutoff)":
        display_df = df_scored[df_scored["Risk_Tier"] == "Moderate Risk"]
    elif filter_opt == "Low Risk (<Cutoff)":
        display_df = df_scored[df_scored["Risk_Tier"] == "Low Risk"]
    else:
        display_df = df_scored

    # CSV Download Button
    with col_dl:
        csv_buffer = io.StringIO()
        df_scored.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Scored Fleet CSV",
            data=csv_buffer.getvalue(),
            file_name=f"telco_fleet_scored_cutoff_{int(active_threshold * 100)}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )

    # Select display columns for clarity
    pref_cols = [
        "customerID", "Churn_Probability", "Risk_Tier", "Action_Recommendation",
        "Contract", "tenure", "MonthlyCharges", "InternetService", "TechSupport", "PaymentMethod"
    ]
    available_cols = [c for c in pref_cols if c in display_df.columns] + [
        c for c in display_df.columns if c not in pref_cols
    ]

    # Present formatted dataframe
    st.dataframe(
        display_df[available_cols].sort_values("Churn_Probability", ascending=False),
        use_container_width=True,
        height=320,
        column_config={
            "Churn_Probability": st.column_config.ProgressColumn(
                "Risk Likelihood",
                help="Predicted probability of churning",
                format="%.2f",
                min_value=0.0,
                max_value=1.0,
            ),
            "MonthlyCharges": st.column_config.NumberColumn(
                "Monthly Spend",
                format="$%.2f"
            ),
            "tenure": st.column_config.NumberColumn(
                "Tenure (Mo)",
                format="%d mo"
            ),
        }
    )
