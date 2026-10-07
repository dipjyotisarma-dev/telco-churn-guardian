"""
Module: app.py
Purpose: Master entrypoint and orchestrator for TelcoChurn Guardian.
         Configures layout, injects responsive dual-theme CSS, manages global state,
         provides navigation, and routes between Single Customer and Fleet Audit views.
"""

from pathlib import Path
import sys
import streamlit as st

# ==============================================================================
# 1. Path & Environment Bootstrapping
# ==============================================================================
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Local package imports
from components.header import render_header
from components.threshold_controller import render_threshold_controller, DEFAULT_OPTIMAL_THRESHOLD
from views.single_customer_view import render_single_customer_view
from views.batch_audit_view import render_batch_audit_view


# ==============================================================================
# 2. Page Configuration & Layout
# ==============================================================================
st.set_page_config(
    page_title="TelcoChurn Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==============================================================================
# 3. Resource & Pipeline Singleton Caching
# ==============================================================================
@st.cache_resource(show_spinner=False)
def load_cached_pipeline():
    """
    Loads and caches the serialized scikit-learn pipeline singleton.
    Guarantees zero redundant disk I/O across user interactions.
    """
    from src.predict import get_pipeline
    return get_pipeline()


# ==============================================================================
# 4. CSS Injection (Dual-Theme Responsive SaaS Styling)
# ==============================================================================
def inject_custom_styles() -> None:
    """Injects responsive enterprise theme CSS."""
    css_path = APP_DIR / "styles" / "theme.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


# ==============================================================================
# 5. Master Orchestrator Application
# ==============================================================================
def main() -> None:
    """Master application workflow entrypoint."""
    inject_custom_styles()

    # Pre-flight pipeline check
    try:
        _ = load_cached_pipeline()
    except Exception as e:
        st.error(
            f"❌ Unable to load production model pipeline from models/telco_churn_pipeline.joblib. "
            f"Ensure the artifact exists and scikit-learn is installed. Details: {str(e)}"
        )
        return

    # Sidebar Navigation & Operational Metadata
    st.sidebar.markdown(
        "<div style='display:flex; align-items:center; gap:0.5rem; margin-bottom:0.75rem;'>"
        "<span style='font-size:1.4rem;'>🛡️</span>"
        "<span style='font-size:1.1rem; font-weight:700; letter-spacing:-0.02em;'>TelcoChurn Guardian</span>"
        "</div>",
        unsafe_allow_html=True
    )

    nav_choice = st.sidebar.radio(
        "Workspace View",
        options=[
            "👤 Single Account Assessment",
            "📊 Fleet Portfolio Audit (Batch)"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr style='margin: 0.75rem 0; border: none; border-top: 1px solid var(--tg-card-border);'>", unsafe_allow_html=True)

    # Sidebar Decision Threshold Controller
    active_threshold = render_threshold_controller()

    # Sidebar System & Model Telemetry
    st.sidebar.markdown("<hr style='margin: 0.75rem 0; border: none; border-top: 1px solid var(--tg-card-border);'>", unsafe_allow_html=True)
    st.sidebar.markdown(
        """
        <div style="font-size:0.72rem; color:rgba(128,128,128,0.9); line-height:1.4;">
          <b>Model Engine:</b> L1-Logistic Regression (C=0.1)<br>
          <b>Evaluation AUC:</b> 0.846<br>
          <b>Calibrated Cutoff:</b> 28.0%<br>
          <b>Serving Status:</b> <span style="color:#10b981;">● Online / Active</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render Main Dashboard Header
    render_header(
        title="TelcoChurn Guardian",
        subtitle="Operational Subscriber Retention & Churn Risk Intelligence",
        badge_text="Production Pipeline • L1 Logistic Regression",
        active_threshold=active_threshold
    )

    # Route View
    if "Single Account Assessment" in nav_choice:
        render_single_customer_view(active_threshold=active_threshold)
    else:
        render_batch_audit_view(active_threshold=active_threshold)


if __name__ == "__main__":
    main()
