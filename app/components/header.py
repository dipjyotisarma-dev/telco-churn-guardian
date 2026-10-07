"""
Module: header.py
Purpose: Clean, high-density dashboard header with brand title, operational subtitle,
         and model confidence / deployment status indicator pill.
"""

from typing import Optional
import streamlit as st


def render_header(
    title: str = "TelcoChurn Guardian",
    subtitle: str = "Operational Subscriber Retention & Churn Risk Intelligence",
    badge_text: str = "Production Model • L1-Regularized Logistic Regression",
    active_threshold: Optional[float] = None
) -> None:
    """
    Renders an enterprise SaaS header with semantic badge and subtitle.

    Parameters:
        title (str): Main application title.
        subtitle (str): Descriptive operational context for non-technical users.
        badge_text (str): Status label shown in the model badge pill.
        active_threshold (Optional[float]): Current decision threshold to display if provided.
    """
    threshold_str = f" • Active Cutoff: {active_threshold * 100:.1f}%" if active_threshold is not None else ""
    full_badge = f"{badge_text}{threshold_str}"

    html_code = f"""
    <div class="tg-header-container">
      <div class="tg-header-title-group">
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div>
        <span class="tg-badge tg-badge-info">
          <svg width="8" height="8" viewBox="0 0 8 8" fill="currentColor" style="display:inline-block;">
            <circle cx="4" cy="4" r="3"/>
          </svg>
          {full_badge}
        </span>
      </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)
