"""
=============================================================================
CampusFlow – Data Preprocessing Module
Machine learning feature engineering, encoding, scaling, and mathematical transforms
=============================================================================
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler


# Disallowed columns for numerical scaling (identifiers, keys, names)
IDENTIFIER_KEYWORDS = ["id", "student_id", "roll_no", "reg_no", "name", "email", "phone", "ssn"]


def is_identifier_column(col_name):
    """Checks if a column name matches common identifier keywords."""
    c_lower = col_name.lower().strip()
    return any(k in c_lower for k in IDENTIFIER_KEYWORDS)


def apply_label_encoding(df, columns):
    """
    Applies Label Encoding to specified categorical columns.
    Returns (preprocessed_df, summary_str, mapping_dict)
    """
    preprocessed = df.copy()
    mapping_dict = {}

    for col in columns:
        if col not in preprocessed.columns:
            continue
        le = LabelEncoder()
        # Fill nulls temporarily for encoding
        temp_series = preprocessed[col].astype(str)
        encoded_col_name = f"{col}_Encoded"
        preprocessed[encoded_col_name] = le.fit_transform(temp_series)
        mapping_dict[col] = {str(cls): int(idx) for idx, cls in enumerate(le.classes_)}

    summary = f"Generated Label Encoded feature(s) for: {', '.join(columns)}."
    return preprocessed, summary, mapping_dict


def apply_one_hot_encoding(df, columns, drop_first=False):
    """
    Applies One-Hot Encoding to specified categorical columns.
    Returns (preprocessed_df, summary_str, new_columns_list)
    """
    preprocessed = df.copy()
    valid_cols = [c for c in columns if c in preprocessed.columns]

    if not valid_cols:
        return preprocessed, "No valid columns provided for One-Hot Encoding.", []

    initial_col_count = len(preprocessed.columns)
    preprocessed = pd.get_dummies(preprocessed, columns=valid_cols, drop_first=drop_first, dtype=int)
    new_cols = [c for c in preprocessed.columns if any(c.startswith(f"{vc}_") for vc in valid_cols)]
    
    summary = f"One-Hot Encoded {len(valid_cols)} categorical feature(s), creating {len(new_cols)} binary indicator columns."
    return preprocessed, summary, new_cols


def apply_min_max_scaling(df, columns, feature_range=(0, 1)):
    """
    Scales numerical features to specified range (default 0 to 1).
    Guarantees identifiers (like Student_ID) are protected and not scaled.
    Returns (preprocessed_df, summary_str, scaled_columns)
    """
    preprocessed = df.copy()
    scaled_cols = []
    skipped_cols = []

    for col in columns:
        if col not in preprocessed.columns:
            continue
        if is_identifier_column(col):
            skipped_cols.append(col)
            continue
        if not pd.api.types.is_numeric_dtype(preprocessed[col]):
            skipped_cols.append(col)
            continue

        scaler = MinMaxScaler(feature_range=feature_range)
        col_vals = preprocessed[[col]].fillna(preprocessed[col].median())
        scaled_name = f"{col}_MinMax"
        preprocessed[scaled_name] = scaler.fit_transform(col_vals).round(4)
        scaled_cols.append(scaled_name)

    summary_parts = [f"Applied Min-Max Scaling on: {', '.join(scaled_cols)}."]
    if skipped_cols:
        summary_parts.append(f"Protected non-scalable / identifier columns: {', '.join(skipped_cols)}.")

    return preprocessed, " ".join(summary_parts), scaled_cols


def apply_standard_scaling(df, columns):
    """
    Standardizes features by removing mean and scaling to unit variance (Z-score).
    Guarantees identifiers are protected.
    Returns (preprocessed_df, summary_str, scaled_columns)
    """
    preprocessed = df.copy()
    scaled_cols = []
    skipped_cols = []

    for col in columns:
        if col not in preprocessed.columns:
            continue
        if is_identifier_column(col):
            skipped_cols.append(col)
            continue
        if not pd.api.types.is_numeric_dtype(preprocessed[col]):
            skipped_cols.append(col)
            continue

        scaler = StandardScaler()
        col_vals = preprocessed[[col]].fillna(preprocessed[col].median())
        scaled_name = f"{col}_StandardScaled"
        preprocessed[scaled_name] = scaler.fit_transform(col_vals).round(4)
        scaled_cols.append(scaled_name)

    summary_parts = [f"Applied Standard Scaling (Z-score) on: {', '.join(scaled_cols)}."]
    if skipped_cols:
        summary_parts.append(f"Protected non-scalable / identifier columns: {', '.join(skipped_cols)}.")

    return preprocessed, " ".join(summary_parts), scaled_cols


def apply_attendance_feature_engineering(df):
    """
    Generates core academic domain metrics:
    - Attendance_Percentage: (Present / Total_Classes) * 100
    - Attendance_Status: Good (>=75%) vs Low (<75%)
    - Risk_Category: Safe (>=85%), Moderate (75-84%), Critical (<75%)
    - Absent_Ratio: Absent / Total_Classes
    Returns (preprocessed_df, summary_str, created_features)
    """
    preprocessed = df.copy()
    created = []

    if "Total_Classes" in preprocessed.columns and "Present" in preprocessed.columns:
        # Cast to numeric
        tot = pd.to_numeric(preprocessed["Total_Classes"], errors="coerce").fillna(90)
        pres = pd.to_numeric(preprocessed["Present"], errors="coerce").fillna(0)
        
        # Enforce non-zero denominator
        tot = np.where(tot <= 0, 1, tot)

        # 1. Attendance Percentage
        preprocessed["Attendance_Percentage"] = ((pres / tot) * 100).round(2)
        created.append("Attendance_Percentage")

        # 2. Attendance Status (Cutoff 75%)
        preprocessed["Attendance_Status"] = np.where(
            preprocessed["Attendance_Percentage"] >= 75.0,
            "Good (>=75%)",
            "Low (<75%)"
        )
        created.append("Attendance_Status")

        # 3. Academic Risk Category
        conditions = [
            preprocessed["Attendance_Percentage"] >= 85.0,
            (preprocessed["Attendance_Percentage"] >= 75.0) & (preprocessed["Attendance_Percentage"] < 85.0),
            preprocessed["Attendance_Percentage"] < 75.0
        ]
        choices = ["Safe Zone (>=85%)", "Moderate Zone (75-84%)", "Critical Shortage (<75%)"]
        preprocessed["Risk_Category"] = np.select(conditions, choices, default="Moderate Zone")
        created.append("Risk_Category")

        # 4. Absent Ratio
        if "Absent" in preprocessed.columns:
            ab = pd.to_numeric(preprocessed["Absent"], errors="coerce").fillna(0)
            preprocessed["Absent_Ratio"] = (ab / tot).round(4)
            created.append("Absent_Ratio")

        summary = f"Engineered academic features: {', '.join(created)}."
        return preprocessed, summary, created

    return preprocessed, "Required columns ('Total_Classes', 'Present') not present for attendance engineering.", []


def apply_numerical_transform(df, column, transform_type="log"):
    """
    Applies mathematical transformations (log1p, sqrt, square).
    Returns (preprocessed_df, summary_str, new_column_name)
    """
    preprocessed = df.copy()
    if column not in preprocessed.columns or not pd.api.types.is_numeric_dtype(preprocessed[column]):
        return df, f"Column '{column}' is not numeric.", None

    s = pd.to_numeric(preprocessed[column], errors="coerce").fillna(0)

    if transform_type == "log":
        new_col = f"{column}_Log1p"
        # clip minimum to 0 for log1p safety
        preprocessed[new_col] = np.log1p(np.maximum(0, s)).round(4)
        summary = f"Created '{new_col}' using Natural Log (log1p) transform."

    elif transform_type == "sqrt":
        new_col = f"{column}_Sqrt"
        preprocessed[new_col] = np.sqrt(np.maximum(0, s)).round(4)
        summary = f"Created '{new_col}' using Square Root transform."

    elif transform_type == "square":
        new_col = f"{column}_Square"
        preprocessed[new_col] = np.square(s).round(2)
        summary = f"Created '{new_col}' using Square (x^2) transform."

    else:
        return df, f"Unsupported transform '{transform_type}'.", None

    return preprocessed, summary, new_col
