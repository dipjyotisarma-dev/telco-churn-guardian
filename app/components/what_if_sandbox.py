"""
Module: what_if_sandbox.py
Purpose: Interactive retention offer simulator. Allows customer service reps and
         retention managers to test counterfactual interventions (e.g. Contract upgrade,
         Tech Support bundle, Rate reduction) and immediately visualize risk reduction.
"""

from typing import Dict, Any
import plotly.graph_objects as go
import streamlit as st
from src.predict import predict_single_customer


def render_what_if_sandbox(
    current_payload: Dict[str, Any],
    current_prob: float,
    threshold: float
) -> None:
    """
    Renders an interactive counterfactual retention sandbox with live model scoring
    and a side-by-side Plotly delta comparison chart.

    Parameters:
        current_payload (Dict[str, Any]): Raw feature attributes of the currently evaluated subscriber.
        current_prob (float): Baseline predicted churn probability.
        threshold (float): Active decision cutoff.
    """
    st.markdown(
        "<div class='tg-card-title' style='margin-top:0.5rem;'>"
        "🧪 Counterfactual Retention Sandbox (What-If Simulator)"
        "</div>",
        unsafe_allow_html=True
    )
    st.caption(
        "Simulate proactive retention counter-offers (e.g. annual commitment, add-on security, or rate discounts) "
        "to test how interventions alter the subscriber's predicted retention likelihood."
    )

    # Simulation control widgets in compact layout
    col_w1, col_w2, col_w3, col_w4 = st.columns(4)

    with col_w1:
        current_contract = current_payload.get("Contract", "Month-to-month")
        target_contract = st.selectbox(
            "Contract Offer",
            options=["Keep Current", "One year", "Two year"],
            index=1 if current_contract == "Month-to-month" else 0,
            help="Upgrading to an annual contract creates formal commitment."
        )

    with col_w2:
        current_tech = current_payload.get("TechSupport", "No")
        add_tech_support = st.checkbox(
            "Bundle Tech Support",
            value=(current_tech != "Yes"),
            help="Free 6-month Tech Support add-on reduces frustration."
        )

    with col_w3:
        current_sec = current_payload.get("OnlineSecurity", "No")
        add_online_sec = st.checkbox(
            "Bundle Online Security",
            value=(current_sec != "Yes"),
            help="Complimentary identity protection increases switching cost."
        )

    with col_w4:
        rate_discount_pct = st.selectbox(
            "Monthly Rate Discount",
            options=[0, 10, 15, 20],
            format_func=lambda x: f"{x}% Discount" if x > 0 else "No Discount",
            index=1,
            help="Promotional discount applied to Monthly Charges."
        )

    # Build counterfactual simulated payload
    simulated_payload = current_payload.copy()

    if target_contract != "Keep Current":
        simulated_payload["Contract"] = target_contract

    if add_tech_support:
        simulated_payload["TechSupport"] = "Yes"

    if add_online_sec:
        simulated_payload["OnlineSecurity"] = "Yes"

    if rate_discount_pct > 0:
        discount_factor = 1.0 - (rate_discount_pct / 100.0)
        orig_monthly = float(current_payload.get("MonthlyCharges", 70.0))
        simulated_payload["MonthlyCharges"] = round(orig_monthly * discount_factor, 2)

    # Run inference for the simulated counterfactual scenario
    sim_result = predict_single_customer(simulated_payload, threshold=threshold)
    sim_prob = sim_result["churn_probability"]

    # Compute deltas
    abs_delta_pct = (sim_prob - current_prob) * 100
    if current_prob > 0:
        rel_reduction_pct = ((current_prob - sim_prob) / current_prob) * 100
    else:
        rel_reduction_pct = 0.0

    # Visualization: Side-by-Side Plotly comparison
    col_chart, col_metrics = st.columns([1.2, 0.8])

    with col_chart:
        cur_pct = round(current_prob * 100, 1)
        new_pct = round(sim_prob * 100, 1)
        thresh_pct = round(threshold * 100, 1)

        # Bar colors
        cur_color = "#ef4444" if cur_pct >= 60 else ("#f59e0b" if cur_pct >= thresh_pct else "#10b981")
        new_color = "#ef4444" if new_pct >= 60 else ("#f59e0b" if new_pct >= thresh_pct else "#10b981")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=["Current Profile", "Simulated Offer"],
            y=[cur_pct, new_pct],
            marker_color=[cur_color, new_color],
            text=[f"{cur_pct}%", f"{new_pct}%"],
            textposition="auto",
            textfont=dict(size=14, weight=700),
            width=[0.45, 0.45]
        ))

        # Decision threshold line
        fig.add_shape(
            type="line",
            x0=-0.5,
            x1=1.5,
            y0=thresh_pct,
            y1=thresh_pct,
            line=dict(color="#dc2626", width=2, dash="dash"),
        )

        fig.add_annotation(
            x=0.5,
            y=thresh_pct + 4,
            text=f"Decision Cutoff ({thresh_pct}%)",
            showarrow=False,
            font=dict(size=11, color="#dc2626")
        )

        fig.update_layout(
            title=dict(text="<b>Risk Reduction Comparison</b>", font=dict(size=13, color="gray")),
            yaxis=dict(
                title=dict(text="Churn Likelihood (%)", font=dict(color="gray", size=11)),
                tickfont=dict(color="gray", size=10),
                range=[0, max(100, max(cur_pct, new_pct) + 15)],
                showgrid=True,
                gridcolor="rgba(128,128,128,0.18)"
            ),
            xaxis=dict(
                tickfont=dict(color="gray", size=11),
                showgrid=False
            ),
            height=230,
            margin=dict(l=30, r=20, t=35, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif")
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col_metrics:
        st.markdown(
            f"""
            <div class="tg-card" style="height: 230px; display: flex; flex-direction: column; justify-content: space-between;">
              <div>
                <div class="tg-card-title">Simulated Impact</div>
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.4rem;">
                  <span style="font-size:0.85rem; color:rgba(128,128,128,0.9);">Risk Delta:</span>
                  <span style="font-size:1.15rem; font-weight:700; color:{'#10b981' if abs_delta_pct <= 0 else '#ef4444'};">
                    {abs_delta_pct:+.1f}%
                  </span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.4rem;">
                  <span style="font-size:0.85rem; color:rgba(128,128,128,0.9);">Relative Drop:</span>
                  <span style="font-size:1.15rem; font-weight:700; color:#10b981;">
                    -{rel_reduction_pct:.1f}%
                  </span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                  <span style="font-size:0.85rem; color:rgba(128,128,128,0.9);">Projected Tier:</span>
                  <span class="tg-badge {'tg-badge-safe' if not sim_result['is_churn_risk'] else 'tg-badge-moderate'}">
                    {sim_result['risk_tier']}
                  </span>
                </div>
              </div>
              <div style="font-size:0.75rem; color:rgba(128,128,128,0.85); line-height:1.3; border-top:1px solid rgba(128,128,128,0.18); padding-top:0.4rem;">
                <b>Takeaway:</b> {'This proposed bundle successfully moves the customer below the risk threshold.' if not sim_result['is_churn_risk'] else 'Further incentives or contract modifications are required to achieve full retention stability.'}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
