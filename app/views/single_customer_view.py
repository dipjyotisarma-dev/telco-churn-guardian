"""
Module: single_customer_view.py
Purpose: Single-account retention profile assessment view. Provides a high-density,
         side-by-side layout with form inputs, live Plotly risk gauge, ROI card,
         and interactive What-If counterfactual retention simulation.
"""

from typing import Dict, Any, Optional
import streamlit as st

from components.customer_form import render_customer_form, SAMPLE_PRESETS
from components.visual_gauge import render_visual_gauge
from components.roi_card import render_roi_card
from components.what_if_sandbox import render_what_if_sandbox
from src.predict import predict_single_customer


def render_single_customer_view(active_threshold: float) -> None:
    """
    Renders the Single Customer Retention Risk Assessment workspace.

    Parameters:
        active_threshold (float): Active decision boundary probability from sidebar.
    """
    # 1. Ensure session state initialization
    if "current_customer_payload" not in st.session_state:
        # Preload the high-risk persona as an illustrative default
        st.session_state["current_customer_payload"] = SAMPLE_PRESETS["Custom Profile"].copy()

    if "current_prediction_result" not in st.session_state or st.session_state.get("last_scored_threshold") != active_threshold:
        try:
            st.session_state["current_prediction_result"] = predict_single_customer(
                st.session_state["current_customer_payload"],
                threshold=active_threshold
            )
            st.session_state["last_scored_threshold"] = active_threshold
        except Exception as e:
            st.error(f"Inference error during initialization: {str(e)}")
            st.session_state["current_prediction_result"] = None

    # 2. Side-by-Side Split Layout (High Density, Minimal Scrolling)
    col_left, col_right = st.columns([1.25, 0.85])

    # LEFT COLUMN: 19-Parameter Customer Profile Form
    with col_left:
        submitted_payload, is_submitted = render_customer_form(
            preset_override=st.session_state.get("current_customer_payload")
        )
        if is_submitted and submitted_payload is not None:
            st.session_state["current_customer_payload"] = submitted_payload
            try:
                st.session_state["current_prediction_result"] = predict_single_customer(
                    submitted_payload,
                    threshold=active_threshold
                )
                st.session_state["last_scored_threshold"] = active_threshold
                st.toast("Subscriber profile successfully scored!", icon="✅")
            except Exception as e:
                st.error(f"Prediction failed: {str(e)}")

    # RIGHT COLUMN: Live Risk Gauge & ROI Impact Analysis
    with col_right:
        pred_res = st.session_state.get("current_prediction_result")
        if pred_res is not None:
            render_visual_gauge(
                churn_prob=pred_res["churn_probability"],
                threshold=active_threshold,
                risk_tier=pred_res["risk_tier"],
                action_recommendation=pred_res["action_recommendation"]
            )

            current_payload = st.session_state.get("current_customer_payload", {})
            monthly_charges = float(current_payload.get("MonthlyCharges", 70.0))
            render_roi_card(
                churn_prob=pred_res["churn_probability"],
                threshold=active_threshold,
                monthly_charges=monthly_charges
            )
        else:
            st.info("Submit the profile form on the left to evaluate retention risk.")

    # 3. INTERACTIVE RETENTION LAB (Tabs below for high density)
    st.markdown("<hr style='margin: 1rem 0 0.75rem 0; border: none; border-top: 1px solid var(--tg-card-border);'>", unsafe_allow_html=True)
    tab_sandbox, tab_drivers = st.tabs([
        "🧪 Counterfactual Offer Sandbox",
        "🔍 Account Behavioral Risk Indicators"
    ])

    with tab_sandbox:
        current_payload = st.session_state.get("current_customer_payload")
        pred_res = st.session_state.get("current_prediction_result")
        if current_payload is not None and pred_res is not None:
            render_what_if_sandbox(
                current_payload=current_payload,
                current_prob=pred_res["churn_probability"],
                threshold=active_threshold
            )
        else:
            st.info("Evaluate a profile to test counterfactual retention offers.")

    with tab_drivers:
        current_payload = st.session_state.get("current_customer_payload")
        if current_payload is not None:
            _render_behavioral_indicators(current_payload)


def _render_behavioral_indicators(payload: Dict[str, Any]) -> None:
    """
    Renders high-signal behavioral and financial risk indicators for non-technical users.
    """
    tenure = int(payload.get("tenure", 0))
    contract = str(payload.get("Contract", "Month-to-month"))
    monthly = float(payload.get("MonthlyCharges", 0.0))
    total = float(payload.get("TotalCharges", 0.0))
    internet = str(payload.get("InternetService", "No"))
    tech_supp = str(payload.get("TechSupport", "No"))
    payment = str(payload.get("PaymentMethod", ""))

    # Compute rate shock indicator
    safe_t = max(1, tenure)
    avg_hist = total / safe_t
    discrepancy = monthly - avg_hist

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="tg-card">
              <div class="tg-card-title">Tenure Risk Band</div>
              <div class="tg-card-value">{'0-12 Months' if tenure <= 12 else ('> 48 Months' if tenure > 48 else '12-48 Months')}</div>
              <div class="tg-card-desc">
                {'⚠️ Early-stage account (highest churn hazard).' if tenure <= 12 else '🛡️ Established subscriber cohort.'}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="tg-card">
              <div class="tg-card-title">Commitment Lock-In</div>
              <div class="tg-card-value">{contract}</div>
              <div class="tg-card-desc">
                {'⚠️ Zero switching penalty. Easy departure.' if contract == 'Month-to-month' else '🔒 Strong contractual friction.'}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="tg-card">
              <div class="tg-card-title">Rate Shock Flag</div>
              <div class="tg-card-value">{discrepancy:+.2f} $/mo</div>
              <div class="tg-card-desc">
                {'⚠️ Recent bill increase vs historical average.' if discrepancy > 5 else '✅ Predictable billing stability.'}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        has_support = tech_supp == "Yes"
        st.markdown(
            f"""
            <div class="tg-card">
              <div class="tg-card-title">Support Touchpoint</div>
              <div class="tg-card-value">{'Protected' if has_support else 'Vulnerable'}</div>
              <div class="tg-card-desc">
                {'🛡️ Tech Support active.' if has_support else '⚠️ Lacks dedicated technical support.'}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
