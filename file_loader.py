"""
=============================================================================
CampusFlow – Multi-Format File Loader Module
Supports CSV, TSV, XLSX, XLS, JSON, JSONL, NDJSON, XML, TXT, DAT, Parquet,
and compressed CSV.GZ / JSON.GZ
=============================================================================
"""

import io
import os
import gzip
import json
import csv
import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st


# Maximum file size limit: 50MB
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024


def format_file_size(size_in_bytes):
    """Converts bytes to a human-readable string."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} Bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"


def detect_file_format(filename):
    """
    Detects the file format and compression type from the filename.
    Returns (extension: str, format_name: str, is_compressed: bool)
    """
    fname_lower = filename.lower()
    
    if fname_lower.endswith(".csv.gz"):
        return ".csv.gz", "Gzip Compressed CSV", True
    elif fname_lower.endswith(".json.gz"):
        return ".json.gz", "Gzip Compressed JSON", True
    
    ext = os.path.splitext(fname_lower)[1]
    format_map = {
        ".csv": "Comma-Separated Values (CSV)",
        ".tsv": "Tab-Separated Values (TSV)",
        ".xlsx": "Microsoft Excel OpenXML (XLSX)",
        ".xls": "Legacy Microsoft Excel (XLS)",
        ".json": "JavaScript Object Notation (JSON)",
        ".jsonl": "JSON Lines (JSONL)",
        ".ndjson": "Newline Delimited JSON (NDJSON)",
        ".xml": "Extensible Markup Language (XML)",
        ".txt": "Text Delimited Data (TXT)",
        ".dat": "Data File (DAT)",
        ".parquet": "Apache Parquet Columnar (PARQUET)"
    }
    
    return ext, format_map.get(ext, f"Unknown ({ext})"), False


def detect_csv_delimiter(file_bytes):
    """
    Sniffs the delimiter of a text-based delimited file.
    Defaults to comma ',' if sniffing fails.
    """
    try:
        sample = file_bytes[:4096].decode("utf-8", errors="ignore")
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample, delimiters=[',', '\t', ';', '|'])
        return dialect.delimiter
    except Exception:
        return ","


def parse_xml_to_dataframe(xml_content):
    """
    Parses hierarchical XML data into a flat tabular pandas DataFrame.
    """
    try:
        if isinstance(xml_content, bytes):
            root = ET.fromstring(xml_content)
        else:
            root = ET.fromstring(xml_content.encode("utf-8"))

        records = []
        # Iterate over child elements
        for child in root:
            row = {}
            # Capture tag attributes if any
            for attr_k, attr_v in child.attrib.items():
                row[f"@{attr_k}"] = attr_v

            # Capture direct sub-elements
            has_subchildren = False
            for subchild in child:
                has_subchildren = True
                row[subchild.tag] = subchild.text.strip() if subchild.text else ""

            # If child has no subchildren, take child's text
            if not has_subchildren and child.text:
                row[child.tag] = child.text.strip()

            if row:
                records.append(row)

        if not records:
            raise ValueError("No tabular record elements found under XML root.")

        return pd.DataFrame(records)
    except Exception as e:
        raise ValueError(f"XML Parsing Failed: {str(e)}")


def load_file_content(uploaded_file, options=None):
    """
    Loads and parses an uploaded file into a Pandas DataFrame based on format.
    
    options: dict with optional keys:
      - 'delimiter': str (for CSV, TXT, DAT)
      - 'sheet_name': str (for Excel)
      - 'flatten_json': bool (for JSON)
    
    Returns (df: pd.DataFrame, message: str)
    """
    if options is None:
        options = {}

    file_bytes = uploaded_file.getvalue()
    size = len(file_bytes)

    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size ({format_file_size(size)}) exceeds maximum allowed limit of 50 MB.")

    fname = uploaded_file.name
    ext, format_name, is_compressed = detect_file_format(fname)

    # 1. Compressed CSV (.csv.gz)
    if ext == ".csv.gz":
        with gzip.GzipFile(fileobj=io.BytesIO(file_bytes)) as gz:
            df = pd.read_csv(gz)
        return df, f"Successfully parsed {format_name} ({len(df)} records)"

    # 2. Compressed JSON (.json.gz)
    if ext == ".json.gz":
        with gzip.GzipFile(fileobj=io.BytesIO(file_bytes)) as gz:
            decompressed_text = gz.read().decode("utf-8", errors="ignore")
            data = json.loads(decompressed_text)
            if isinstance(data, list):
                df = pd.json_normalize(data) if options.get("flatten_json", True) else pd.DataFrame(data)
            else:
                df = pd.json_normalize(data)
        return df, f"Successfully parsed {format_name} ({len(df)} records)"

    # 3. CSV
    if ext == ".csv":
        delim = options.get("delimiter")
        if not delim or delim == "Auto-Detect":
            delim = detect_csv_delimiter(file_bytes)
        df = pd.read_csv(io.BytesIO(file_bytes), sep=delim)
        return df, f"Parsed CSV with delimiter '{delim}' ({len(df)} records)"

    # 4. TSV
    if ext == ".tsv":
        df = pd.read_csv(io.BytesIO(file_bytes), sep="\t")
        return df, f"Parsed TSV file ({len(df)} records)"

    # 5. Excel (.xlsx, .xls)
    if ext in [".xlsx", ".xls"]:
        sheet = options.get("sheet_name", 0)
        try:
            df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet, engine="openpyxl")
        except Exception:
            df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet)
        return df, f"Parsed Excel sheet '{sheet}' ({len(df)} records)"

    # 6. JSON
    if ext == ".json":
        try:
            data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
            if isinstance(data, list):
                if options.get("flatten_json", True):
                    df = pd.json_normalize(data)
                else:
                    df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Check if it has a records array inside
                array_keys = [k for k, v in data.items() if isinstance(v, list)]
                if array_keys:
                    df = pd.json_normalize(data[array_keys[0]])
                else:
                    df = pd.json_normalize(data)
            else:
                df = pd.read_json(io.BytesIO(file_bytes))
            return df, f"Parsed JSON format ({len(df)} records)"
        except Exception as e:
            df = pd.read_json(io.BytesIO(file_bytes))
            return df, f"Parsed JSON format ({len(df)} records)"

    # 7. JSONL & NDJSON
    if ext in [".jsonl", ".ndjson"]:
        df = pd.read_json(io.BytesIO(file_bytes), lines=True)
        return df, f"Parsed {format_name} ({len(df)} lines)"

    # 8. XML
    if ext == ".xml":
        df = parse_xml_to_dataframe(file_bytes)
        return df, f"Parsed XML elements ({len(df)} records)"

    # 9. TXT & DAT
    if ext in [".txt", ".dat"]:
        delim = options.get("delimiter")
        if not delim or delim == "Auto-Detect":
            delim = detect_csv_delimiter(file_bytes)
        df = pd.read_csv(io.BytesIO(file_bytes), sep=delim)
        return df, f"Parsed {format_name} using delimiter '{delim}' ({len(df)} records)"

    # 10. Parquet
    if ext == ".parquet":
        df = pd.read_parquet(io.BytesIO(file_bytes), engine="pyarrow")
        return df, f"Parsed Apache Parquet format ({len(df)} records)"

    # Fallback to general CSV read
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        return df, f"Parsed generic delimited file ({len(df)} records)"
    except Exception as e:
        raise ValueError(f"Unsupported or unparseable file format: {ext}. Details: {str(e)}")


def get_excel_sheet_names(uploaded_file):
    """Returns list of sheet names from an Excel file without loading all sheets."""
    try:
        xl = pd.ExcelFile(io.BytesIO(uploaded_file.getvalue()))
        return xl.sheet_names
    except Exception:
        return ["Sheet1"]
