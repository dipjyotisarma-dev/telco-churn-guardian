"""
Module: customer_form.py
Purpose: Professional, high-density SaaS configuration panel for all 19 Telco attributes.
         Structured into 3 intuitive tabs (Demographics, Services, Contract & Billing)
         with native segmented controls, crisp vertical rhythm, and zero label wrapping.
"""

from typing import Dict, Any, Optional, Tuple
import streamlit as st

# Reference personas for rapid non-technical operator testing
SAMPLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "Custom Profile": {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 2,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 70.35,
        "TotalCharges": 139.05,
    },
    "High Risk: Month-to-Month Fiber Streamer": {
        "gender": "Male",
        "SeniorCitizen": 1,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 3,
        "PhoneService": "Yes",
        "MultipleLines": "Yes",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 98.50,
        "TotalCharges": 295.50,
    },
    "Low Risk: Long-Tenure Two-Year Contract": {
        "gender": "Female",
        "SeniorCitizen": 0,
        "Partner": "Yes",
        "Dependents": "Yes",
        "tenure": 64,
        "PhoneService": "Yes",
        "MultipleLines": "Yes",
        "InternetService": "DSL",
        "OnlineSecurity": "Yes",
        "OnlineBackup": "Yes",
        "DeviceProtection": "Yes",
        "TechSupport": "Yes",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Two year",
        "PaperlessBilling": "No",
        "PaymentMethod": "Credit card (automatic)",
        "MonthlyCharges": 65.20,
        "TotalCharges": 4180.00,
    },
    "Moderate Risk: 1-Year Contract with Bill Shock": {
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 12,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "Yes",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "One year",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Bank transfer (automatic)",
        "MonthlyCharges": 82.00,
        "TotalCharges": 984.00,
    },
}


def render_customer_form(
    preset_override: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[Dict[str, Any]], bool]:
    """
    Renders an enterprise-grade, clean SaaS configuration form capturing all 19 raw Telco attributes.
    Organized into 3 logical tabs with segmented controls and full-width alignment.

    Parameters:
        preset_override (Optional[Dict[str, Any]]): Pre-loaded values to prefill form inputs.

    Returns:
        Tuple[Optional[Dict[str, Any]], bool]:
            - customer_payload: Dictionary of all 19 features if submitted, else current defaults.
            - submitted: Boolean flag indicating if the form submit button was pressed.
    """
    # 1. Preset Selector Toolbar
    col_pre_title, col_pre_sel = st.columns([1, 2.2])
    with col_pre_title:
        st.markdown(
            "<div style='font-size:0.82rem; font-weight:700; color:inherit; padding-top:0.35rem;'>"
            "📋 Persona Template:"
            "</div>",
            unsafe_allow_html=True
        )
    with col_pre_sel:
        preset_keys = list(SAMPLE_PRESETS.keys())
        selected_preset_name = st.selectbox(
            "Select Persona Template",
            options=preset_keys,
            index=0,
            label_visibility="collapsed",
            key="preset_selector_key"
        )

    # Determine baseline default values with reactive preset tracking
    last_preset = st.session_state.get("last_selected_preset")
    if last_preset != selected_preset_name:
        st.session_state["last_selected_preset"] = selected_preset_name
        defaults = SAMPLE_PRESETS[selected_preset_name].copy()
    elif preset_override is not None:
        defaults = preset_override.copy()
    else:
        defaults = SAMPLE_PRESETS[selected_preset_name].copy()

    # Prefix widget keys with preset name to cleanly isolate and update state
    kp = f"p_{selected_preset_name[:6]}"

    # 2. Strict Batched Form with Clean Structured Tabs
    with st.form("customer_profile_form", clear_on_submit=False):
        st.markdown(
            "<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;'>"
            "<span style='font-size:0.9rem; font-weight:700; letter-spacing:-0.01em; color:inherit;'>"
            "Subscriber Account Profile</span>"
            "<span class='tg-badge tg-badge-info' style='font-size:0.7rem;'>19 Model Features</span>"
            "</div>",
            unsafe_allow_html=True
        )

        tab_profile, tab_services, tab_billing = st.tabs([
            "👤 Demographics & Tenure",
            "🌐 Connectivity & Services",
            "💳 Contract & Financials"
        ])

        # ----------------------------------------------------------------------
        # TAB 1: Demographics & Account Tenure
        # ----------------------------------------------------------------------
        with tab_profile:
            tenure_val = int(defaults.get("tenure", 2))
            c_t1, c_t2 = st.columns([1.5, 1])
            with c_t1:
                tenure = st.slider(
                    "Account Tenure (Months)",
                    min_value=0,
                    max_value=72,
                    value=tenure_val,
                    step=1,
                    format="%d mos",
                    key=f"{kp}_tenure",
                    help="Length of customer relationship with Telco in months (0-72)"
                )
            with c_t2:
                cohort_label = "Early (0-12m)" if tenure <= 12 else ("Mature (>48m)" if tenure > 48 else "Mid (12-48m)")
                cohort_badge = "tg-badge-critical" if tenure <= 12 else ("tg-badge-safe" if tenure > 48 else "tg-badge-moderate")
                st.markdown(
                    f"""
                    <div style="padding-top:1.4rem;">
                      <span class="tg-badge {cohort_badge}" style="width:100%; justify-content:center; padding:0.35rem 0.5rem;">
                        Cohort: {cohort_label}
                      </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<hr style='margin:0.5rem 0 0.65rem 0; border:none; border-top:1px solid rgba(128,128,128,0.15);'>", unsafe_allow_html=True)

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                gender_raw = st.segmented_control(
                    "Gender",
                    options=["Female", "Male"],
                    default=defaults.get("gender", "Female"),
                    key=f"{kp}_gender"
                )
                gender = gender_raw or defaults.get("gender", "Female")

                partner_raw = st.segmented_control(
                    "Has Partner",
                    options=["No", "Yes"],
                    default=defaults.get("Partner", "No"),
                    key=f"{kp}_partner"
                )
                partner = partner_raw or defaults.get("Partner", "No")

            with d_col2:
                senior_raw = st.segmented_control(
                    "Senior Citizen (65+)",
                    options=["No", "Yes"],
                    default="Yes" if defaults.get("SeniorCitizen", 0) == 1 else "No",
                    key=f"{kp}_senior"
                )
                senior_val = 1 if (senior_raw or ("Yes" if defaults.get("SeniorCitizen", 0) == 1 else "No")) == "Yes" else 0

                dependents_raw = st.segmented_control(
                    "Has Dependents",
                    options=["No", "Yes"],
                    default=defaults.get("Dependents", "No"),
                    key=f"{kp}_dependents"
                )
                dependents = dependents_raw or defaults.get("Dependents", "No")

        # ----------------------------------------------------------------------
        # TAB 2: Connectivity & Services
        # ----------------------------------------------------------------------
        with tab_services:
            st.markdown(
                "<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:rgba(128,128,128,0.9); margin-bottom:0.4rem;'>"
                "Core Connectivity</div>",
                unsafe_allow_html=True
            )
            s_c1, s_c2 = st.columns(2)
            with s_c1:
                internet_raw = st.segmented_control(
                    "Internet Service",
                    options=["Fiber optic", "DSL", "No"],
                    default=defaults.get("InternetService", "Fiber optic"),
                    key=f"{kp}_internet"
                )
                internet_service = internet_raw or defaults.get("InternetService", "Fiber optic")
            with s_c2:
                phone_raw = st.segmented_control(
                    "Phone Service",
                    options=["Yes", "No"],
                    default=defaults.get("PhoneService", "Yes"),
                    key=f"{kp}_phone"
                )
                phone_service = phone_raw or defaults.get("PhoneService", "Yes")

            mult_opts = ["No", "Yes", "No phone service"]
            mult_def = defaults.get("MultipleLines", "No")
            mult_idx = mult_opts.index(mult_def) if mult_def in mult_opts else 0
            multiple_lines = st.selectbox(
                "Multiple Phone Lines",
                options=mult_opts,
                index=mult_idx,
                key=f"{kp}_mult"
            )

            st.markdown(
                "<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:rgba(128,128,128,0.9); margin:0.6rem 0 0.4rem 0;'>"
                "Security, Support & Media Add-Ons</div>",
                unsafe_allow_html=True
            )
            addon_opts = ["No", "Yes", "No internet service"]

            def get_addon_idx(val: str) -> int:
                return addon_opts.index(val) if val in addon_opts else 0

            sec_c1, sec_c2 = st.columns(2)
            with sec_c1:
                online_security = st.selectbox(
                    "Online Security",
                    options=addon_opts,
                    index=get_addon_idx(defaults.get("OnlineSecurity", "No")),
                    key=f"{kp}_sec"
                )
                online_backup = st.selectbox(
                    "Online Backup",
                    options=addon_opts,
                    index=get_addon_idx(defaults.get("OnlineBackup", "No")),
                    key=f"{kp}_back"
                )
                streaming_tv = st.selectbox(
                    "Streaming TV",
                    options=addon_opts,
                    index=get_addon_idx(defaults.get("StreamingTV", "No")),
                    key=f"{kp}_tv"
                )
            with sec_c2:
                tech_support = st.selectbox(
                    "Tech Support",
                    options=addon_opts,
                    index=get_addon_idx(defaults.get("TechSupport", "No")),
                    key=f"{kp}_tech"
                )
                device_protection = st.selectbox(
                    "Device Protection",
                    options=addon_opts,
                    index=get_addon_idx(defaults.get("DeviceProtection", "No")),
                    key=f"{kp}_dev"
                )
                streaming_movies = st.selectbox(
                    "Streaming Movies",
                    options=addon_opts,
                    index=get_addon_idx(defaults.get("StreamingMovies", "No")),
                    key=f"{kp}_mov"
                )

        # ----------------------------------------------------------------------
        # TAB 3: Contract & Financial Billing
        # ----------------------------------------------------------------------
        with tab_billing:
            b_c1, b_c2 = st.columns([1.6, 1.2])
            with b_c1:
                contract_raw = st.segmented_control(
                    "Contract Commitment",
                    options=["Month-to-month", "One year", "Two year"],
                    default=defaults.get("Contract", "Month-to-month"),
                    key=f"{kp}_contract"
                )
                contract = contract_raw or defaults.get("Contract", "Month-to-month")
            with b_c2:
                paperless_raw = st.segmented_control(
                    "Paperless Billing",
                    options=["Yes", "No"],
                    default=defaults.get("PaperlessBilling", "Yes"),
                    key=f"{kp}_paperless"
                )
                paperless_billing = paperless_raw or defaults.get("PaperlessBilling", "Yes")

            pay_opts = [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)"
            ]
            pay_def = defaults.get("PaymentMethod", "Electronic check")
            pay_idx = pay_opts.index(pay_def) if pay_def in pay_opts else 0
            payment_method = st.selectbox(
                "Payment Method",
                options=pay_opts,
                index=pay_idx,
                key=f"{kp}_pay"
            )

            ch_c1, ch_c2 = st.columns(2)
            with ch_c1:
                monthly_charges = st.number_input(
                    "Monthly Charges ($)",
                    min_value=15.0,
                    max_value=150.0,
                    value=float(defaults.get("MonthlyCharges", 70.35)),
                    step=0.50,
                    format="%.2f",
                    key=f"{kp}_monthly"
                )
            with ch_c2:
                est_total = float(defaults.get("TotalCharges", 0.0))
                if est_total <= 0:
                    est_total = round(monthly_charges * max(1, tenure), 2)
                total_charges = st.number_input(
                    "Total Charges ($)",
                    min_value=0.0,
                    max_value=10000.0,
                    value=float(est_total),
                    step=10.00,
                    format="%.2f",
                    key=f"{kp}_total"
                )

        # ----------------------------------------------------------------------
        # SUBMIT BUTTON
        # ----------------------------------------------------------------------
        st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "🛡️ Assess Subscriber Retention Risk",
            type="primary",
            use_container_width=True
        )

    # Construct clean structured customer payload
    payload: Dict[str, Any] = {
        "gender": str(gender),
        "SeniorCitizen": int(senior_val),
        "Partner": str(partner),
        "Dependents": str(dependents),
        "tenure": int(tenure),
        "PhoneService": str(phone_service),
        "MultipleLines": str(multiple_lines),
        "InternetService": str(internet_service),
        "OnlineSecurity": str(online_security),
        "OnlineBackup": str(online_backup),
        "DeviceProtection": str(device_protection),
        "TechSupport": str(tech_support),
        "StreamingTV": str(streaming_tv),
        "StreamingMovies": str(streaming_movies),
        "Contract": str(contract),
        "PaperlessBilling": str(paperless_billing),
        "PaymentMethod": str(payment_method),
        "MonthlyCharges": float(monthly_charges),
        "TotalCharges": float(total_charges),
    }

    if submitted:
        return payload, True

    return payload, False
