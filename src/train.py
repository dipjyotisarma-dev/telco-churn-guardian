"""
Module: train.py
Purpose: Standalone CLI model training pipeline. Chains data loading,
         sanitization, feature engineering, and the winning L1-regularized
         Logistic Regression estimator into an exported .joblib artifact.
"""

from pathlib import Path
import joblib
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score

from data_loader import load_raw_data
from cleaning import clean_data
from feature_engineering import engineer_features
from preprocessing import split_data, get_feature_types, build_preprocessor

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"
MODEL_PATH = MODELS_DIR / "telco_churn_pipeline.joblib"

# Winning hyperparameter configuration from GridSearchCV
BEST_PARAMS = {
    "C": 0.1445,
    "penalty": "l1",
    "solver": "liblinear",
    "random_state": 42,
    "max_iter": 1000
}


def run_training_pipeline() -> Path:
    """Executes the full training pipeline and persists the model artifact."""
    print("=" * 60)
    print("       STARTING TELCO CHURN TRAINING PIPELINE               ")
    print("=" * 60)

    # 1. Ingestion
    print("[1/5] Loading raw data...")
    df_raw = load_raw_data(data_dir=str(ROOT_DIR / "data" / "raw"))

    # 2. Sanitization
    print("[2/5] Cleaning and sanitizing records...")
    df_clean, _ = clean_data(df_raw)

    # 3. Domain Feature Engineering
    print("[3/5] Engineering behavioral features...")
    df_featured, _ = engineer_features(df_clean)

    # 4. Stratified Splitting & Preprocessor Setup
    print("[4/5] Splitting data and configuring ColumnTransformer...")
    X_train, X_test, y_train, y_test = split_data(
        df_featured, 
        target_col="Churn", 
        test_size=0.20, 
        random_state=42
    )
    num_cols, cat_cols = get_feature_types(X_train)
    preprocessor = build_preprocessor(num_cols, cat_cols)

    # 5. Pipeline Assembly & Fitting
    print(f"[5/5] Training Logistic Regression with winning parameters:")
    print(f"      {BEST_PARAMS}")
    
    classifier = LogisticRegression(**BEST_PARAMS)
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate on Holdout Test Set
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    auc_score = roc_auc_score(y_test, y_proba)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("-" * 60)
    print(f"Holdout Test ROC-AUC  : {auc_score:.4f}")
    print(f"Holdout Test Accuracy : {acc:.4f}")
    print(f"Holdout Test F1-Score : {f1:.4f}")
    print("-" * 60)

    # Persist Artifact
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Pipeline successfully serialized to: {MODEL_PATH}")
    print("=" * 60)
    
    return MODEL_PATH


if __name__ == "__main__":
    run_training_pipeline()