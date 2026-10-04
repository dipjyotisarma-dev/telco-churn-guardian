"""
Module: feature_engineering.py
Purpose: Generates domain-informed interaction terms and behavioral features
         to improve the linear decision boundary of Logistic Regression.
"""

from typing import Tuple, List
import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Builds domain features specifically targeting churn behavior:
    
    1. Charge_Discrepancy:
       Difference between current monthly charge and actual average historical monthly spend.
       Reveals recent price increases or bill shock.
       Formula: MonthlyCharges - (TotalCharges / safe_tenure)
       
    2. Total_Services_Subscribed:
       Count of supplementary add-on services adopted by the customer.
       Higher service counts correlate with higher switching costs (loyalty).
       
    3. Tenure_Cohort:
       Binned categorical representation of tenure into risk bands:
       ['0-12m', '12-24m', '24-48m', '48m+'].

    Parameters:
        df (pd.DataFrame): Sanitized DataFrame.

    Returns:
        Tuple[pd.DataFrame, List[str]]:
            - df_featured: DataFrame with engineered columns added.
            - new_features: List of strings naming the newly created columns.
    """
    df_feat = df.copy()

    # Feature 1: Charge Discrepancy (Rate Shock Indicator)
    # Guard against division by zero for new customers with tenure == 0
    safe_tenure = df_feat['tenure'].replace(0, 1)
    historical_avg_monthly = df_feat['TotalCharges'] / safe_tenure
    df_feat['Charge_Discrepancy'] = df_feat['MonthlyCharges'] - historical_avg_monthly

    # Feature 2: Service Adoption Density (Count of 'Yes' responses)
    service_columns = [
        'PhoneService', 'MultipleLines', 'OnlineSecurity',
        'OnlineBackup', 'DeviceProtection', 'TechSupport',
        'StreamingTV', 'StreamingMovies'
    ]
    # Filter to only columns present in the input dataframe
    available_service_cols = [c for c in service_columns if c in df_feat.columns]
    df_feat['Total_Services_Subscribed'] = (df_feat[available_service_cols] == 'Yes').sum(axis=1)

    # Feature 3: Tenure Cohort
    df_feat['Tenure_Cohort'] = pd.cut(
        df_feat['tenure'],
        bins=[-1, 12, 24, 48, 72],
        labels=['0-12m', '12-24m', '24-48m', '48m+']
    ).astype(str)

    new_features = ['Charge_Discrepancy', 'Total_Services_Subscribed', 'Tenure_Cohort']
    return df_feat, new_features