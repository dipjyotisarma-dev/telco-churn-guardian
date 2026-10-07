"""
Module: visual_gauge.py
Purpose: Renders a Plotly semi-circular risk gauge with semantic status badge,
         colored risk bands, and active decision threshold marker.
"""

from typing import Dict, Any, List
import plotly.graph_objects as go
import streamlit as st


def render_visual_gauge(
    churn_prob: float,
    threshold: float,
    risk_tier: str,
    action_recommendation: str
) -> None:
    """
    Renders an interactive, dual-theme compatible semi-circular speedometer gauge
    representing the predicted churn risk against the active decision boundary.

    Parameters:
        churn_prob (float): Estimated churn probability (0.0 to 1.0).
        threshold (float): Active decision cutoff (0.0 to 1.0).
        risk_tier (str): Categorical risk level ('Low Risk', 'Moderate Risk', 'Critical Risk').
        action_recommendation (str): Recommended operational next step.
    """
    prob_pct = round(churn_prob * 100, 1)
    thresh_pct = round(threshold * 100, 1)

    # Determine semantic color styling based on tier
    if churn_prob >= 0.60 or risk_tier == "Critical Risk":
        bar_color = "#ef4444"  # Crimson
        badge_class = "tg-badge-critical"
        badge_icon = "🔴"
        tier_label = "Critical Risk"
    elif churn_prob >= threshold or risk_tier == "Moderate Risk":
        bar_color = "#f59e0b"  # Amber
        badge_class = "tg-badge-moderate"
        badge_icon = "🟡"
        tier_label = "Moderate Risk"
    else:
        bar_color = "#10b981"  # Emerald
        badge_class = "tg-badge-safe"
        badge_icon = "🟢"
        tier_label = "Low Retention Risk"

    # Build dynamically validated steps for the gauge background
    steps: List[Dict[str, Any]] = []
    if thresh_pct < 60:
        steps.append({"range": [0, thresh_pct], "color": "rgba(34, 197, 94, 0.22)"})
        steps.append({"range": [thresh_pct, 60], "color": "rgba(245, 158, 11, 0.25)"})
        steps.append({"range": [60, 100], "color": "rgba(239, 68, 68, 0.28)"})
    else:
        mid_point = min(40.0, thresh_pct / 2)
        steps.append({"range": [0, mid_point], "color": "rgba(34, 197, 94, 0.22)"})
        steps.append({"range": [mid_point, thresh_pct], "color": "rgba(245, 158, 11, 0.25)"})
        steps.append({"range": [thresh_pct, 100], "color": "rgba(239, 68, 68, 0.28)"})

    # Render Title Above Meter (prevents SVG canvas clipping)
    st.markdown(
        """
        <div style="text-align:center; padding-top:0.2rem; margin-bottom:-0.25rem;">
          <span style="font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:rgba(128,128,128,0.95);">
            Subscriber Retention Risk
          </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=prob_pct,
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": "%",
                "font": {"size": 38, "color": bar_color, "weight": 700},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "rgba(128, 128, 128, 0.4)",
                    "ticks": "outside",
                    "tickvals": [0, 25, 50, 75, 100],
                    "ticktext": ["0%", "25%", "50%", "75%", "100%"],
                    "tickfont": {"size": 11, "color": "rgba(128,128,128,0.85)"},
                },
                "bar": {"color": bar_color, "thickness": 0.26},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 1,
                "bordercolor": "rgba(128,128,128,0.2)",
                "steps": steps,
                "threshold": {
                    "line": {"color": "#dc2626", "width": 3},
                    "thickness": 0.85,
                    "value": thresh_pct,
                },
            },
        )
    )

    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10),
        height=195,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
    )

    # Render Plotly Chart
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Render High-Density Semantic Status Badge and Operational Recommendation
    delta_str = f"{prob_pct - thresh_pct:+.1f}% vs Cutoff"
    st.markdown(
        f"""
        <div class="tg-card" style="margin-top: -0.5rem; padding: 0.85rem 1rem;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
            <span class="tg-badge {badge_class}">
              {badge_icon} {tier_label} ({prob_pct}%)
            </span>
            <span style="font-size:0.75rem; font-weight:600; color:rgba(128,128,128,0.9);">
              Cutoff: {thresh_pct:.1f}% ({delta_str})
            </span>
          </div>
          <div style="font-size:0.825rem; font-weight:600; color:inherit; margin-top:0.35rem;">
            📢 Action: <span style="font-weight:400; opacity:0.9;">{action_recommendation}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
