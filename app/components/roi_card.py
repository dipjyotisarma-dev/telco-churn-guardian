"""
Module: roi_card.py
Purpose: Plain-English financial card detailing the economic tradeoff of proactive retention:
         $500 lost Customer Lifetime Value (LTV) vs. $50 promotional incentive.
         Universal Light & Dark theme support with crisp typography.
"""

from typing import Dict, Any
import streamlit as st

# Financial parameters derived from Telco retention economics
BENCHMARK_LTV: float = 500.00          # Average lost lifetime value when a customer churns
RETENTION_OFFER_COST: float = 50.00    # Cost of proactive promotional incentive
ESTIMATED_SAVE_RATE: float = 0.65      # Benchmark retention success rate when incentive is accepted


def render_roi_card(
    churn_prob: float,
    threshold: float,
    monthly_charges: float = 70.00
) -> None:
    """
    Renders a high-density financial card explaining the retention ROI tradeoff
    in plain business language for retention managers and marketers.

    Parameters:
        churn_prob (float): Model predicted churn probability.
        threshold (float): Active decision boundary.
        monthly_charges (float): Customer's current monthly billing amount.
    """
    is_at_risk = churn_prob >= threshold

    # Financial calculations
    expected_unmitigated_loss = round(churn_prob * BENCHMARK_LTV, 2)
    expected_protected_ltv = round(ESTIMATED_SAVE_RATE * BENCHMARK_LTV, 2)
    net_economic_benefit = round(expected_protected_ltv - RETENTION_OFFER_COST, 2)
    roi_multiple = round((net_economic_benefit / RETENTION_OFFER_COST), 1)

    st.markdown(
        "<div class='tg-card-title' style='margin-top:0.25rem;'>"
        "Financial Impact & Retention Economics"
        "</div>",
        unsafe_allow_html=True
    )

    cell_style = "background:rgba(128,128,128,0.06); padding:0.5rem; border-radius:6px; border:1px solid rgba(128,128,128,0.18);"
    label_style = "font-size:0.7rem; color:rgba(128,128,128,0.9); text-transform:uppercase; font-weight:600;"
    sub_style = "font-size:0.68rem; color:rgba(128,128,128,0.85);"

    if is_at_risk:
        st.markdown(
            f"""
            <div class="tg-card" style="border-left: 4px solid var(--tg-primary);">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                <span class="tg-card-title" style="margin:0; font-size:0.85rem;">
                  💼 Proactive Intervention Analysis
                </span>
                <span class="tg-badge tg-badge-safe">
                  Action Warranted
                </span>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.6rem; margin-bottom: 0.65rem;">
                <div style="{cell_style}">
                  <div style="{label_style}">At-Risk Value</div>
                  <div style="font-size:1.1rem; font-weight:700; color:#ef4444;">${expected_unmitigated_loss:,.0f}</div>
                  <div style="{sub_style}">From $500 baseline LTV</div>
                </div>
                <div style="{cell_style}">
                  <div style="{label_style}">Incentive Cost</div>
                  <div style="font-size:1.1rem; font-weight:700; color:inherit;">${RETENTION_OFFER_COST:.0f}</div>
                  <div style="{sub_style}">Contract discount credit</div>
                </div>
                <div style="{cell_style}">
                  <div style="{label_style}">Net Protected</div>
                  <div style="font-size:1.1rem; font-weight:700; color:#10b981;">+${net_economic_benefit:,.0f}</div>
                  <div style="{sub_style}">{roi_multiple}x Estimated ROI</div>
                </div>
              </div>
              <p style="font-size:0.78rem; color:rgba(128,128,128,0.9); margin:0; line-height:1.4;">
                <b>Recommendation:</b> Deploying a $50 retention offer preserves an estimated 
                <b style="color:inherit;">${net_economic_benefit:,.0f}</b> in net customer lifetime value (assuming an industry-standard 65% save rate), 
                preventing a total loss of ${BENCHMARK_LTV:,.0f}.
              </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        saved_incentive = RETENTION_OFFER_COST
        organic_stay_prob = round((1.0 - churn_prob) * 100, 1)
        st.markdown(
            f"""
            <div class="tg-card" style="border-left: 4px solid #10b981;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                <span class="tg-card-title" style="margin:0; font-size:0.85rem;">
                  🛡️ Organic Retention Status
                </span>
                <span class="tg-badge tg-badge-safe">
                  Budget Preserved
                </span>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.6rem; margin-bottom: 0.65rem;">
                <div style="{cell_style}">
                  <div style="{label_style}">Organic Stay Likelihood</div>
                  <div style="font-size:1.1rem; font-weight:700; color:#10b981;">{organic_stay_prob}%</div>
                  <div style="{sub_style}">Naturally stable account</div>
                </div>
                <div style="{cell_style}">
                  <div style="{label_style}">Unneeded Discount</div>
                  <div style="font-size:1.1rem; font-weight:700; color:inherit;">$0.00</div>
                  <div style="{sub_style}">No offer required</div>
                </div>
                <div style="{cell_style}">
                  <div style="{label_style}">Budget Saved</div>
                  <div style="font-size:1.1rem; font-weight:700; color:#10b981;">+${saved_incentive:.0f}</div>
                  <div style="{sub_style}">Saved promotion capital</div>
                </div>
              </div>
              <p style="font-size:0.78rem; color:rgba(128,128,128,0.9); margin:0; line-height:1.4;">
                <b>Recommendation:</b> Customer risk is comfortably below the {threshold*100:.1f}% threshold. 
                Do <b>not</b> dispatch a discount offer. Unnecessary promotional credits dilute account margin 
                without altering retention behavior.
              </p>
            </div>
            """,
            unsafe_allow_html=True
        )
