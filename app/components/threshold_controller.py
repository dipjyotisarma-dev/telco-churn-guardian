"""
Module: threshold_controller.py
Purpose: Renders the sidebar decision cutoff controller with business impact explanation
         and financial tradeoff guidance for non-technical retention managers.
"""

from typing import Tuple
import streamlit as st

DEFAULT_OPTIMAL_THRESHOLD: float = 0.28


def render_threshold_controller() -> float:
    """
    Renders an interactive threshold slider and business context block in the sidebar.

    Returns:
        float: The active decision threshold probability selected by the user.
    """
    st.sidebar.markdown("### ⚙️ Decision Strategy")
    st.sidebar.markdown(
        "<p style='font-size:0.8rem; color:rgba(128,128,128,0.9); margin-bottom:0.75rem;'>"
        "Adjust the probability threshold at which an account is classified as high-risk "
        "and flagged for proactive retention incentives.</p>",
        unsafe_allow_html=True
    )

    def reset_cutoff_callback() -> None:
        st.session_state["threshold_slider_key"] = DEFAULT_OPTIMAL_THRESHOLD
        st.session_state["decision_threshold"] = DEFAULT_OPTIMAL_THRESHOLD

    if "threshold_slider_key" not in st.session_state:
        st.session_state["threshold_slider_key"] = DEFAULT_OPTIMAL_THRESHOLD

    # Quick reset button with on_click callback to reliably update widget state
    st.sidebar.button(
        "Reset to 28% (Default)",
        on_click=reset_cutoff_callback,
        use_container_width=True,
        help="Reset decision cutoff to the cost-optimal 0.28 threshold"
    )

    active_threshold: float = st.sidebar.slider(
        "Risk Flag Cutoff",
        min_value=0.10,
        max_value=0.90,
        step=0.01,
        format="%.2f",
        key="threshold_slider_key",
        help="Accounts with predicted churn probability at or above this value trigger retention interventions."
    )
    st.session_state["decision_threshold"] = active_threshold

    # Plain-English business impact guidance
    threshold_pct = active_threshold * 100
    if abs(active_threshold - DEFAULT_OPTIMAL_THRESHOLD) < 0.015:
        impact_header = "🎯 Cost-Optimal Calibration"
        impact_desc = (
            f"Set at <b>{threshold_pct:.1f}%</b>. This cutoff was statistically calibrated to minimize "
            "net financial loss by balancing the $500 lost customer lifetime value against the $50 "
            "proactive retention incentive."
        )
        badge_class = "tg-badge-info"
    elif active_threshold < DEFAULT_OPTIMAL_THRESHOLD:
        impact_header = "⚡ Aggressive Retention"
        impact_desc = (
            f"Lower cutoff (<b>{threshold_pct:.1f}%</b>). Captures more potential churners before they leave, "
            "but expends more budget on promotional offers for accounts that might have stayed organically."
        )
        badge_class = "tg-badge-moderate"
    else:
        impact_header = "🛡️ Conservative Budget"
        impact_desc = (
            f"Higher cutoff (<b>{threshold_pct:.1f}%</b>). Restricts retention offers strictly to "
            "accounts at critical risk of leaving, preserving promotional budget at the cost of missing subtle churn signals."
        )
        badge_class = "tg-badge-safe"

    st.sidebar.markdown(
        f"""
        <div class="tg-card" style="margin-top:0.75rem; padding:0.8rem;">
          <div style="margin-bottom:0.4rem;">
            <span class="tg-badge {badge_class}">{impact_header}</span>
          </div>
          <div style="font-size:0.78rem; color:rgba(128,128,128,0.9); line-height:1.4;">
            {impact_desc}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    return active_threshold
