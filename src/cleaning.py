"""
Module: cleaning.py
Purpose: Performs data sanitization, explicit type casting, missing value
         fixes, and returns a detailed data hygiene report.
"""

from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Sanitizes raw customer data:
    1. Replaces hidden whitespace strings in 'TotalCharges' with NaN.
    2. Imputes TotalCharges NaN values with 0.0 for new customers (tenure == 0).
    3. Drops the non-predictive administrative identifier 'customerID'.
    4. Converts the target column 'Churn' from string ('Yes'/'No') to binary integer (1/0).

    Parameters:
        df (pd.DataFrame): Raw ingested DataFrame.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]:
            - df_cleaned: Sanitized pandas DataFrame.
            - report: Structured dictionary detailing what changes were made.
    """
    df_clean = df.copy()
    report = {}

    # 1. TotalCharges whitespace sanitation
    raw_tc_missing = (df_clean['TotalCharges'] == " ").sum()
    df_clean['TotalCharges'] = pd.to_numeric(
        df_clean['TotalCharges'].replace(" ", np.nan), 
        errors='coerce'
    )
    # Customers with tenure == 0 have not been billed yet; their baseline total charge is 0.0
    imputed_count = df_clean['TotalCharges'].isna().sum()
    df_clean['TotalCharges'] = df_clean['TotalCharges'].fillna(0.0)

    report['total_charges_whitespace_fixed'] = int(raw_tc_missing)
    report['total_charges_imputed_with_zero'] = int(imputed_count)

    # 2. Drop administrative identifier
    if 'customerID' in df_clean.columns:
        df_clean = df_clean.drop(columns=['customerID'])
        report['dropped_identifier'] = 'customerID'
    else:
        report['dropped_identifier'] = None

    # 3. Target binary encoding
    if 'Churn' in df_clean.columns and df_clean['Churn'].dtype == object:
        df_clean['Churn'] = df_clean['Churn'].map({'Yes': 1, 'No': 0})
        report['target_mapping'] = "{'Yes': 1, 'No': 0}"

    report['cleaned_rows'] = df_clean.shape[0]
    report['cleaned_columns'] = df_clean.shape[1]

    return df_clean, report


def print_cleaning_report(report: Dict[str, Any]) -> None:
    """Prints a formatted report of the data cleaning operations."""
    print("=" * 60)
    print("               DATA SANITIZATION REPORT                     ")
    print("=" * 60)
    print(f"  • Rows Retained                 : {report.get('cleaned_rows')}")
    print(f"  • Columns Retained              : {report.get('cleaned_columns')}")
    print(f"  • TotalCharges Whitespace Fixed : {report.get('total_charges_whitespace_fixed')}")
    print(f"  • TotalCharges Imputed (with 0) : {report.get('total_charges_imputed_with_zero')}")
    print(f"  • Identifier Dropped            : {report.get('dropped_identifier')}")
    print(f"  • Target Variable Encoded       : {report.get('target_mapping')}")
    print("=" * 60)