"""
Module: predict.py
Purpose: Production inference service layer. Loads the serialized pipeline,
         applies feature engineering to raw customer payloads, and evaluates
         risk against the cost-optimized decision threshold.
"""

from typing import Dict, Any, Union
from pathlib import Path
import joblib
import pandas as pd

try:
    from src.feature_engineering import engineer_features
except ImportError:  # Fallback for direct `python src/predict.py` execution
    from feature_engineering import engineer_features


# Resolve path relative to repository root
ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "models" / "telco_churn_pipeline.joblib"

# Default cost-optimized threshold discovered during tuning
DEFAULT_OPTIMAL_THRESHOLD = 0.28

# Cached pipeline instance
_CACHED_PIPELINE = None


def get_pipeline():
    """Loads and caches the serialized scikit-learn pipeline."""
    global _CACHED_PIPELINE
    if _CACHED_PIPELINE is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {MODEL_PATH}. "
                "Ensure you have trained and saved the pipeline first."
            )
        _CACHED_PIPELINE = joblib.load(MODEL_PATH)
    return _CACHED_PIPELINE


def predict_single_customer(
    customer_payload: Dict[str, Any],
    threshold: float = DEFAULT_OPTIMAL_THRESHOLD
) -> Dict[str, Any]:
    """
    Scores a single raw customer input dictionary.

    Parameters:
        customer_payload: Dictionary of customer attributes matching raw Telco schema.
        threshold: Probability cutoff for flagging churn risk (default: 0.28).

    Returns:
        Structured prediction result dictionary.
    """
    pipeline = get_pipeline()

    # Convert single dictionary to DataFrame and apply feature transformations
    input_df = pd.DataFrame([customer_payload])
    input_featured, _ = engineer_features(input_df)

    # Compute posterior probability for positive class (Churn: 1)
    churn_probability = float(pipeline.predict_proba(input_featured)[0, 1])
    is_churn_risk = bool(churn_probability >= threshold)

    # Determine qualitative risk tier
    if churn_probability >= 0.60:
        risk_tier = "Critical Risk"
        action = "Dispatch High-Priority Retention Offer ($50 Incentive)"
    elif churn_probability >= threshold:
        risk_tier = "Moderate Risk"
        action = "Dispatch Digital Engagement / Service Check-In"
    else:
        risk_tier = "Low Risk"
        action = "Standard Service (No Retention Intervention Needed)"

    return {
        "churn_probability": round(churn_probability, 4),
        "is_churn_risk": is_churn_risk,
        "risk_tier": risk_tier,
        "action_recommendation": action,
        "threshold_applied": round(threshold, 4)
    }


def predict_batch(
    df_raw: pd.DataFrame,
    threshold: float = DEFAULT_OPTIMAL_THRESHOLD
) -> pd.DataFrame:
    """
    Scores a batch DataFrame of customer records.

    Parameters:
        df_raw: Raw DataFrame containing customer attributes.
        threshold: Probability cutoff for churn classification.

    Returns:
        DataFrame with 'Churn_Probability' and 'Churn_Risk_Flag' appended.
    """
    pipeline = get_pipeline()
    df_featured, _ = engineer_features(df_raw)
    
    probabilities = pipeline.predict_proba(df_featured)[:, 1]
    
    df_result = df_raw.copy()
    df_result["Churn_Probability"] = probabilities.round(4)
    df_result["Churn_Risk_Flag"] = (probabilities >= threshold).astype(int)
    
    return df_result


if __name__ == "__main__":
    # Smoke test on a sample payload
    sample_payload = {
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
        "TotalCharges": 139.05
    }

    result = predict_single_customer(sample_payload)
    print("=== Inference Smoke Test ===")
    for k, v in result.items():
        print(f"  • {k:22s}: {v}")