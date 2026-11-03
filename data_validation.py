"""
=============================================================================
CampusFlow – Data Quality & Validation Engine
Comprehensive automated auditing of missing data, duplicates, domain anomalies,
text inconsistencies, and statistical outliers
=============================================================================
"""

import re
import pandas as pd
import numpy as np


def detect_outliers_iqr(series, factor=1.5):
    """Calculates outlier count and indices using Interquartile Range (IQR)."""
    if not pd.api.types.is_numeric_dtype(series):
        return 0, []
    s = series.dropna()
    if len(s) < 4:
        return 0, []
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    outlier_mask = (series < lower_bound) | (series > upper_bound)
    return int(outlier_mask.sum()), series[outlier_mask].index.tolist()


def detect_inconsistent_text(series):
    """Detects text values with leading/trailing spaces or mixed casing."""
    if not pd.api.types.is_string_dtype(series) and series.dtype != object:
        return 0, []
    
    inconsistencies = []
    str_series = series.dropna().astype(str)
    
    for idx, val in str_series.items():
        # Check trailing/leading spaces
        if val != val.strip():
            inconsistencies.append((idx, val, "Unstripped whitespace"))
        # Check consecutive multiple spaces
        elif re.search(r"\s{2,}", val):
            inconsistencies.append((idx, val, "Multiple internal spaces"))

    return len(inconsistencies), inconsistencies


def audit_dataset_quality(df, id_column="Student_ID"):
    """
    Performs full automated audit across 11 key data quality dimensions.
    Returns audit_results dict.
    """
    if df is None or df.empty:
        return {
            "is_empty": True,
            "total_rows": 0,
            "total_columns": 0,
            "quality_score": 0.0
        }

    total_rows = len(df)
    total_cols = len(df.columns)
    total_cells = total_rows * total_cols

    # 1. Missing Values
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    null_percentage = round((total_nulls / total_cells) * 100, 2) if total_cells > 0 else 0.0
    cols_with_nulls = {col: int(count) for col, count in null_counts.items() if count > 0}

    # 2. Duplicate Rows
    dup_rows_count = int(df.duplicated().sum())

    # 3. Duplicate IDs
    dup_ids_count = 0
    if id_column and id_column in df.columns:
        dup_ids_count = int(df[id_column].duplicated().sum())
    else:
        # Check for any column ending with 'id'
        id_candidates = [c for c in df.columns if "id" in c.lower()]
        if id_candidates:
            dup_ids_count = int(df[id_candidates[0]].duplicated().sum())
            id_column = id_candidates[0]

    # 4. Duplicate Columns
    duplicate_cols = []
    col_names = df.columns.tolist()
    for i in range(len(col_names)):
        for j in range(i + 1, len(col_names)):
            col1 = col_names[i]
            col2 = col_names[j]
            try:
                if df[col1].equals(df[col2]):
                    duplicate_cols.append((col1, col2))
            except Exception:
                pass

    # 5. Empty Columns (100% null)
    empty_columns = [col for col in df.columns if df[col].isnull().all()]

    # 6. Negative Numerical Values
    negative_counts = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            neg_count = int((df[col] < 0).sum())
            if neg_count > 0:
                negative_counts[col] = neg_count
    total_negatives = sum(negative_counts.values())

    # 7. Attendance Domain Inconsistencies (Present > Total_Classes or Sum mismatch)
    attendance_anomalies = 0
    if "Total_Classes" in df.columns and "Present" in df.columns:
        tot = pd.to_numeric(df["Total_Classes"], errors="coerce")
        pres = pd.to_numeric(df["Present"], errors="coerce")
        overflows = (pres > tot).sum()
        attendance_anomalies += int(overflows)
        if "Absent" in df.columns:
            ab = pd.to_numeric(df["Absent"], errors="coerce")
            mismatches = (tot != (pres + ab)).sum()
            attendance_anomalies += int(mismatches)

    # 8. Inconsistent Text & Whitespace
    text_inconsistencies = {}
    for col in df.columns:
        cnt, _ = detect_inconsistent_text(df[col])
        if cnt > 0:
            text_inconsistencies[col] = cnt
    total_text_issues = sum(text_inconsistencies.values())

    # 9. Statistical Outliers
    outliers_summary = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            cnt, _ = detect_outliers_iqr(df[col])
            if cnt > 0:
                outliers_summary[col] = cnt
    total_outliers = sum(outliers_summary.values())

    # 10. Data Types Summary
    dtypes_map = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # 11. Systematic Quality Score Calculation (0 to 100%)
    # Penalties scaled relative to dataset size
    score = 100.0
    # Penalty for missing cells
    score -= min(30.0, null_percentage * 3.0)
    # Penalty for duplicate rows
    dup_pct = (dup_rows_count / total_rows) * 100 if total_rows > 0 else 0
    score -= min(25.0, dup_pct * 3.5)
    # Penalty for duplicate IDs
    dup_id_pct = (dup_ids_count / total_rows) * 100 if total_rows > 0 else 0
    score -= min(15.0, dup_id_pct * 2.5)
    # Penalty for negative values
    score -= min(15.0, total_negatives * 2.0)
    # Penalty for domain anomalies
    score -= min(10.0, attendance_anomalies * 2.0)
    # Penalty for text inconsistencies
    score -= min(5.0, total_text_issues * 0.2)

    quality_score = max(5.0, min(100.0, round(score, 1)))

    return {
        "is_empty": False,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "total_cells": total_cells,
        "total_nulls": total_nulls,
        "null_percentage": null_percentage,
        "cols_with_nulls": cols_with_nulls,
        "dup_rows_count": dup_rows_count,
        "dup_ids_count": dup_ids_count,
        "id_column_used": id_column,
        "duplicate_columns": duplicate_cols,
        "empty_columns": empty_columns,
        "negative_counts": negative_counts,
        "total_negatives": total_negatives,
        "attendance_anomalies": attendance_anomalies,
        "text_inconsistencies": text_inconsistencies,
        "total_text_issues": total_text_issues,
        "outliers_summary": outliers_summary,
        "total_outliers": total_outliers,
        "dtypes_map": dtypes_map,
        "quality_score": quality_score
    }
