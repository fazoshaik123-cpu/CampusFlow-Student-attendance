"""
=============================================================================
CampusFlow – Data Wrangling & Cleaning Module
Core data cleaning, transformation, imputation, and standardization operations
=============================================================================
"""

import re
import pandas as pd
import numpy as np


def handle_missing_values(df, strategy, columns=None, fill_value=None):
    """
    Handles missing values via drop or imputation (mean, median, mode, constant).
    Returns (cleaned_df, summary_str, affected_rows)
    """
    cleaned = df.copy()
    target_cols = columns if columns else cleaned.columns.tolist()
    initial_nulls = cleaned[target_cols].isnull().sum().sum()

    if initial_nulls == 0:
        return cleaned, "No missing values found in selected columns.", 0

    affected_rows = 0

    if strategy == "Drop Rows with Nulls":
        before_rows = len(cleaned)
        cleaned = cleaned.dropna(subset=target_cols)
        affected_rows = before_rows - len(cleaned)
        summary = f"Dropped {affected_rows} rows containing missing values across {len(target_cols)} column(s)."

    elif strategy == "Drop Entire Column":
        before_cols = len(cleaned.columns)
        cleaned = cleaned.drop(columns=[c for c in target_cols if cleaned[c].isnull().any()])
        affected_rows = before_cols - len(cleaned.columns)
        summary = f"Dropped {affected_rows} column(s) containing missing values."

    elif strategy == "Impute with Mean (Numeric)":
        imputed_count = 0
        for col in target_cols:
            if pd.api.types.is_numeric_dtype(cleaned[col]):
                mean_val = cleaned[col].mean()
                null_mask = cleaned[col].isnull()
                imputed_count += null_mask.sum()
                cleaned[col] = cleaned[col].fillna(round(mean_val, 2))
        affected_rows = int(imputed_count)
        summary = f"Imputed {imputed_count} missing numeric cells with column Mean."

    elif strategy == "Impute with Median (Numeric)":
        imputed_count = 0
        for col in target_cols:
            if pd.api.types.is_numeric_dtype(cleaned[col]):
                med_val = cleaned[col].median()
                null_mask = cleaned[col].isnull()
                imputed_count += null_mask.sum()
                cleaned[col] = cleaned[col].fillna(med_val)
        affected_rows = int(imputed_count)
        summary = f"Imputed {imputed_count} missing numeric cells with column Median."

    elif strategy == "Impute with Mode (Most Frequent)":
        imputed_count = 0
        for col in target_cols:
            mode_series = cleaned[col].mode()
            if not mode_series.empty:
                mode_val = mode_series.iloc[0]
                null_mask = cleaned[col].isnull()
                imputed_count += null_mask.sum()
                cleaned[col] = cleaned[col].fillna(mode_val)
        affected_rows = int(imputed_count)
        summary = f"Imputed {imputed_count} missing cells with column Mode."

    elif strategy == "Custom Fill Value":
        imputed_count = 0
        for col in target_cols:
            null_mask = cleaned[col].isnull()
            imputed_count += null_mask.sum()
            cleaned[col] = cleaned[col].fillna(fill_value if fill_value is not None else "Unknown")
        affected_rows = int(imputed_count)
        summary = f"Replaced {imputed_count} missing cells with custom constant '{fill_value}'."

    else:
        summary = "No operation applied."

    return cleaned, summary, affected_rows


def remove_duplicates(df, subset_cols=None, keep="first"):
    """
    Removes duplicate records based on all columns or specified key columns.
    Returns (cleaned_df, summary_str, dropped_rows_count)
    """
    cleaned = df.copy()
    before_count = len(cleaned)
    target_subset = subset_cols if subset_cols and len(subset_cols) > 0 else None
    
    cleaned = cleaned.drop_duplicates(subset=target_subset, keep=keep)
    dropped = before_count - len(cleaned)
    
    subset_desc = f"subset {target_subset}" if target_subset else "all columns"
    summary = f"Removed {dropped} duplicate rows based on {subset_desc} (Kept {keep})."
    return cleaned, summary, dropped


def convert_data_types(df, type_map):
    """
    Converts columns to specified data types: 'int', 'float', 'str', 'datetime', 'category'.
    type_map: dict of {column_name: target_type_str}
    Returns (cleaned_df, summary_str, converted_cols_count)
    """
    cleaned = df.copy()
    conversions_applied = []

    for col, target_type in type_map.items():
        if col not in cleaned.columns:
            continue
        try:
            if target_type == "int":
                cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0).astype(int)
            elif target_type == "float":
                cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").astype(float)
            elif target_type == "str":
                cleaned[col] = cleaned[col].astype(str)
            elif target_type == "category":
                cleaned[col] = cleaned[col].astype("category")
            elif target_type == "datetime":
                cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce")
            conversions_applied.append(f"{col} -> {target_type}")
        except Exception as e:
            conversions_applied.append(f"{col} (failed: {str(e)})")

    summary = f"Converted {len(conversions_applied)} column(s): {', '.join(conversions_applied)}"
    return cleaned, summary, len(conversions_applied)


def standardize_text_columns(df, columns, operations):
    """
    Standardizes text columns:
    operations list can include: 'strip', 'lowercase', 'uppercase', 'titlecase', 'normalize_spaces', 'department_fix'
    Returns (cleaned_df, summary_str, modified_cells_count)
    """
    cleaned = df.copy()
    modified_cells = 0

    dept_canonical_map = {
        "aiml": "AIML", "a.i.m.l.": "AIML", "ai ml": "AIML", "ai&ml": "AIML",
        "cse": "CSE", "c.s.e.": "CSE", "cs": "CSE", "computer science": "CSE",
        "ece": "ECE", "e.c.e.": "ECE", "electronics": "ECE",
        "eee": "EEE", "e.e.e.": "EEE", "electrical": "EEE",
        "it": "IT", "i.t.": "IT", "information technology": "IT"
    }

    for col in columns:
        if col not in cleaned.columns:
            continue
        cleaned[col] = cleaned[col].astype(str)

        if "strip" in operations:
            cleaned[col] = cleaned[col].str.strip()
        if "normalize_spaces" in operations:
            cleaned[col] = cleaned[col].apply(lambda x: re.sub(r"\s+", " ", str(x)).strip())
        if "lowercase" in operations:
            cleaned[col] = cleaned[col].str.lower()
        if "uppercase" in operations:
            cleaned[col] = cleaned[col].str.upper()
        if "titlecase" in operations:
            cleaned[col] = cleaned[col].str.title()
        if "department_fix" in operations:
            def fix_dept(val):
                key = re.sub(r"[^a-zA-Z]", "", str(val)).lower()
                return dept_canonical_map.get(key, str(val).strip().upper())
            cleaned[col] = cleaned[col].apply(fix_dept)

        modified_cells += len(cleaned)

    summary = f"Applied text standardization ({', '.join(operations)}) on {len(columns)} column(s)."
    return cleaned, summary, modified_cells


def filter_dataset(df, column, operator, value):
    """
    Applies conditional filtering to dataset.
    Returns (filtered_df, summary_str, matching_rows)
    """
    if column not in df.columns:
        return df, "Column not found.", len(df)

    cleaned = df.copy()
    try:
        if operator == "==":
            res = cleaned[cleaned[column].astype(str) == str(value)]
        elif operator == "!=":
            res = cleaned[cleaned[column].astype(str) != str(value)]
        elif operator == "contains":
            res = cleaned[cleaned[column].astype(str).str.contains(str(value), case=False, na=False)]
        elif operator == ">":
            res = cleaned[pd.to_numeric(cleaned[column], errors="coerce") > float(value)]
        elif operator == "<":
            res = cleaned[pd.to_numeric(cleaned[column], errors="coerce") < float(value)]
        elif operator == ">=":
            res = cleaned[pd.to_numeric(cleaned[column], errors="coerce") >= float(value)]
        elif operator == "<=":
            res = cleaned[pd.to_numeric(cleaned[column], errors="coerce") <= float(value)]
        elif operator == "is_null":
            res = cleaned[cleaned[column].isnull()]
        elif operator == "not_null":
            res = cleaned[cleaned[column].notnull()]
        else:
            res = cleaned
        
        summary = f"Filtered {column} {operator} '{value}': {len(res)} of {len(df)} rows matched."
        return res, summary, len(res)
    except Exception as e:
        return df, f"Filter Error: {str(e)}", len(df)


def handle_numerical_outliers(df, column, method="clip", factor=1.5):
    """
    Detects and handles outliers in numeric columns using IQR.
    method: 'clip' (caps bounds) or 'drop' (removes rows).
    Returns (cleaned_df, summary_str, affected_count)
    """
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return df, f"Column '{column}' is not numeric.", 0

    cleaned = df.copy()
    q1 = cleaned[column].quantile(0.25)
    q3 = cleaned[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr

    outlier_mask = (cleaned[column] < lower_bound) | (cleaned[column] > upper_bound)
    outlier_count = int(outlier_mask.sum())

    if outlier_count == 0:
        return cleaned, f"No outliers found in '{column}' with IQR factor {factor}.", 0

    if method == "clip":
        cleaned[column] = cleaned[column].clip(lower=lower_bound, upper=upper_bound)
        summary = f"Clipped {outlier_count} outlier(s) in '{column}' to range [{lower_bound:.2f}, {upper_bound:.2f}]."
    elif method == "drop":
        cleaned = cleaned[~outlier_mask]
        summary = f"Dropped {outlier_count} row(s) containing outliers in '{column}' outside [{lower_bound:.2f}, {upper_bound:.2f}]."
    else:
        summary = f"Detected {outlier_count} outliers in '{column}'."

    return cleaned, summary, outlier_count


def fix_attendance_logical_inconsistencies(df):
    """
    Automated college domain repair:
    - Sets negative values to absolute/0
    - Enforces Present <= Total_Classes
    - Recalculates Absent = Total_Classes - Present
    Returns (cleaned_df, summary_str, fixed_count)
    """
    cleaned = df.copy()
    fixed_count = 0

    if "Total_Classes" in cleaned.columns and "Present" in cleaned.columns:
        # Convert to numeric
        cleaned["Total_Classes"] = pd.to_numeric(cleaned["Total_Classes"], errors="coerce").fillna(90).astype(int)
        cleaned["Present"] = pd.to_numeric(cleaned["Present"], errors="coerce").fillna(0).astype(int)

        # Fix negative values
        neg_mask = (cleaned["Total_Classes"] < 0) | (cleaned["Present"] < 0)
        fixed_count += int(neg_mask.sum())
        cleaned["Total_Classes"] = cleaned["Total_Classes"].abs()
        cleaned["Present"] = cleaned["Present"].abs()

        # Fix overflow Present > Total
        overflow_mask = cleaned["Present"] > cleaned["Total_Classes"]
        fixed_count += int(overflow_mask.sum())
        cleaned.loc[overflow_mask, "Present"] = cleaned.loc[overflow_mask, "Total_Classes"]

        # Re-derive Absent
        cleaned["Absent"] = cleaned["Total_Classes"] - cleaned["Present"]
        fixed_count += len(cleaned)

        summary = f"Enforced attendance logic: Non-negative constraint, capped Present <= Total, recalculated Absent = Total - Present."
        return cleaned, summary, fixed_count

    return cleaned, "Required attendance columns (Total_Classes, Present) not present.", 0
