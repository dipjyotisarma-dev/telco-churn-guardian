"""
Module: eda.py
Purpose: Generates a complete Exploratory Data Analysis profile,
         including target class imbalance, missing value checks,
         cardinality audits, and feature-target correlation.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np

def generate_eda_report(df: pd.DataFrame, target_col: str = "Churn") -> Dict[str, Any]:
    # 1. Ensure target is cleanly numeric (1 / 0)
    target_series = df[target_col].copy()
    if not pd.api.types.is_numeric_dtype(target_series):
        target_series = target_series.astype(str).str.strip().map({'Yes': 1, 'No': 0})
    target_series = pd.to_numeric(target_series, errors='coerce').fillna(0).astype(int)

    target_counts = target_series.value_counts().to_dict()
    target_pct = target_series.value_counts(normalize=True).to_dict()
    
    retained_count = target_counts.get(0, 0)
    churn_count = target_counts.get(1, 0)
    imbalance_ratio = retained_count / max(churn_count, 1)

    # 2. Separate numeric from categorical features safely
    numeric_cols = [
        c for c in df.select_dtypes(include=[np.number]).columns 
        if c != target_col
    ]
    categorical_cols = [c for c in df.columns if c not in numeric_cols and c != target_col]

    missing_counts = df.isnull().sum()
    missing_dict = missing_counts[missing_counts > 0].to_dict()
    cardinality_dict = {col: int(df[col].nunique()) for col in categorical_cols}

    # 3. Compute point-biserial correlations safely via NumPy (immune to PyArrow type errors)
    correlations = {}
    for col in numeric_cols:
        try:
            col_series = pd.to_numeric(df[col], errors='coerce')
            valid_mask = col_series.notna() & target_series.notna()
            if valid_mask.sum() > 1:
                r = float(np.corrcoef(col_series[valid_mask], target_series[valid_mask])[0, 1])
                if not np.isnan(r):
                    correlations[col] = r
        except Exception:
            pass

    correlations = dict(sorted(correlations.items(), key=lambda x: x[1], reverse=True))

    return {
        "total_rows": int(df.shape[0]),
        "total_features": int(df.shape[1] - 1),
        "target_col": target_col,
        "class_0_retained": retained_count,
        "class_0_pct": target_pct.get(0, 0.0),
        "class_1_churn": churn_count,
        "class_1_pct": target_pct.get(1, 0.0),
        "imbalance_ratio": imbalance_ratio,
        "missing_values": missing_dict,
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
        "cardinality": cardinality_dict,
        "numeric_correlations": correlations
    }


def print_eda_report(report: Dict[str, Any]) -> None:
    print("=" * 65)
    print("                 AUTOMATED DATA PROFILE REPORT                   ")
    print("=" * 65)
    print(f"Dataset Dimensions: {report['total_rows']} rows × {report['total_features']} input features")
    print("-" * 65)
    print(f"TARGET CLASS DISTRIBUTION ('{report['target_col']}'):")
    print(f"  • Retained (0) : {report['class_0_retained']:,} ({report['class_0_pct']:.2%})")
    print(f"  • Churned  (1) : {report['class_1_churn']:,} ({report['class_1_pct']:.2%})")
    print(f"  • Imbalance Ratio: 1 positive : {report['imbalance_ratio']:.2f} negatives")
    print("-" * 65)
    print(f"DATA INTEGRITY & CARDINALITY:")
    print(f"  • Missing Values Detected : {report['missing_values'] if report['missing_values'] else 'Zero missing'}")
    print(f"  • Numerical Features ({len(report['numeric_features'])}) : {report['numeric_features']}")
    print(f"  • Categorical Features ({len(report['categorical_features'])}): {list(report['cardinality'].keys())}")
    print("-" * 65)
    print("LINEAR CORRELATION WITH CHURN (Numeric Features):")
    for feat, corr_val in report['numeric_correlations'].items():
        direction = "▲ Risk factor" if corr_val > 0 else "▼ Protective"
        print(f"  • {feat:22s}: {corr_val:+.4f} ({direction})")
    print("=" * 65)