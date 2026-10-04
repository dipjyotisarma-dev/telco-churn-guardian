"""
Module: data_loader.py
Purpose: Handles raw data acquisition from the public remote repository,
         local file caching, and initial loading into a pandas DataFrame.
"""

import os
import urllib.request
import pandas as pd
from pathlib import Path

# Verified public mirror of the IBM Telco Customer Churn dataset
RAW_DATA_URL = (
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/"
    "master/data/Telco-Customer-Churn.csv"
)

def load_raw_data(data_dir: str = "data/raw") -> pd.DataFrame:
    """
    Downloads the raw Telco Churn CSV if not already present on disk,
    caches it in the data_dir, and returns the raw pandas DataFrame.

    Parameters:
        data_dir (str): Directory path where the raw CSV is stored.

    Returns:
        pd.DataFrame: Unmodified raw Telco dataset.
    """
    save_path = Path(data_dir) / "Telco-Customer-Churn.csv"
    save_path.parent.mkdir(parents=True, exist_ok=True)

    if not save_path.exists():
        print(f"[DataLoader] File not found locally. Downloading from remote repository...")
        print(f"             Source: {RAW_DATA_URL}")
        urllib.request.urlretrieve(RAW_DATA_URL, save_path)
        print(f"[DataLoader] Successfully downloaded and cached to: {save_path}")
    else:
        print(f"[DataLoader] Using cached raw dataset from: {save_path}")

    df_raw = pd.read_csv(save_path)
    print(f"[DataLoader] Ingested raw shape: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns.")
    return df_raw