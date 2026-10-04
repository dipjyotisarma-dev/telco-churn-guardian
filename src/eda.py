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
    """
    Computes key statistical properties and distribution metrics across the dataset.

    Parameters:
        df (pd.DataFrame): Cleaned DataFrame.
        target_col (str): Name of the binary classification target.

    Returns:
        Dict[str, Any]: Structured summary dictionary.
    """
    target_counts = df[target_col].value_counts().to_dict()
    target_pct = df[target_col].value_counts(normalize=True).to_dict()
    
    retained_count = target_counts.get(0, 0)
    churn_count = target_counts.get(1, 1)
    imbalance_ratio = retained_count / max(churn_count, 1)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.drop(target_col, errors='ignore').tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    missing_counts = df.isnull().sum()
    missing_dict = missing_counts[missing_counts > 0].to_dict()

    cardinality_dict = {col: int(df[col].nunique()) for col in categorical_cols}

    # Point-biserial correlation for numeric features with binary target
    corr_series = df[numeric_cols + [target_col]].corr()[target_col].drop(target_col, errors='ignore')
    correlations = corr_series.sort_values(ascending=False).to_dict()

    report = {
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
    return report


def print_eda_report(report: Dict[str, Any]) -> None:
    """Renders the EDA report into a structured console output."""
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