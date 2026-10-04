"""
Module: preprocessing.py
Purpose: Handles stratified train-test splitting and builds the scikit-learn
         ColumnTransformer to prevent data leakage during scaling and encoding.
"""

from typing import Tuple, List
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

def split_data(
    df: pd.DataFrame, 
    target_col: str = "Churn", 
    test_size: float = 0.20, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Splits features and target into stratified train and test partitions.

    Parameters:
        df (pd.DataFrame): Featured dataset.
        target_col (str): Target variable name.
        test_size (float): Fraction of data reserved for holdout evaluation.
        random_state (int): Seed for exact reproducibility.

    Returns:
        Tuple: X_train, X_test, y_train, y_test
    """
    X = df.drop(columns=[target_col])
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y  # Essential to preserve the 26.6% churn distribution in both splits
    )
    return X_train, X_test, y_train, y_test


def get_feature_types(X: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Identifies continuous numerical and categorical column names.

    Parameters:
        X (pd.DataFrame): Training feature matrix.

    Returns:
        Tuple[List[str], List[str]]: numeric_features, categorical_features
    """
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()
    return numeric_features, categorical_features


def build_preprocessor(
    numeric_features: List[str],
    categorical_features: List[str]
) -> ColumnTransformer:
    """
    Builds a leakage-free ColumnTransformer pipeline:
    - Numeric: Median Imputation -> StandardScaler (required for L1/L2 penalties)
    - Categorical: Most Frequent Imputation -> OneHotEncoder(drop='first') 
      (drop='first' prevents collinearity in Logistic Regression)

    Parameters:
        numeric_features (List[str]): List of numeric feature names.
        categorical_features (List[str]): List of categorical feature names.

    Returns:
        ColumnTransformer: Configured preprocessor ready for a scikit-learn Pipeline.
    """
    # 1. Pipeline for numeric columns
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # 2. Pipeline for categorical columns
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ])

    # 3. Combine both pipelines
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='drop'
    )
    return preprocessor