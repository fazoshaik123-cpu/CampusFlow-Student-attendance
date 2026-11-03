"""
=============================================================================
CampusFlow – Cross-Format Data Exporter Module
Converts cleaned DataFrames to CSV, XLSX, JSON, JSONL, and Parquet binary streams
=============================================================================
"""

import io
import pandas as pd


def export_dataframe(df, export_format):
    """
    Exports a DataFrame into the chosen format.
    Supported formats: 'CSV', 'XLSX', 'JSON', 'JSONL', 'PARQUET'.
    Returns (bytes_data: bytes, mime_type: str, file_extension: str)
    """
    fmt = export_format.upper().strip()

    if fmt == "CSV":
        csv_str = df.to_csv(index=False)
        return csv_str.encode("utf-8"), "text/csv", ".csv"

    elif fmt == "XLSX":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Cleaned_Data")
        buffer.seek(0)
        return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"

    elif fmt == "JSON":
        json_str = df.to_json(orient="records", indent=2)
        return json_str.encode("utf-8"), "application/json", ".json"

    elif fmt == "JSONL":
        jsonl_str = df.to_json(orient="records", lines=True)
        return jsonl_str.encode("utf-8"), "application/x-ndjson", ".jsonl"

    elif fmt == "PARQUET":
        buffer = io.BytesIO()
        df.to_parquet(buffer, index=False, engine="pyarrow")
        buffer.seek(0)
        return buffer.getvalue(), "application/octet-stream", ".parquet"

    else:
        # Default fallback to CSV
        csv_str = df.to_csv(index=False)
        return csv_str.encode("utf-8"), "text/csv", ".csv"
