"""
========================================================================================
CampusFlow – Multi-Format Data Wrangling and Preprocessing System
College Academic Project: Data Wrangling and Preprocessing
========================================================================================
"""

import sys
import os
import io
import time
import datetime
import pandas as pd
import numpy as np
import streamlit as st

# Ensure utils directory is on Python path regardless of execution directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import CampusFlow Utility Modules
from utils.authentication import (
    render_auth_interface,
    logout_user,
    get_supabase_client
)
from utils.file_loader import (
    load_file_content,
    detect_file_format,
    format_file_size,
    get_excel_sheet_names
)
from utils.data_cleaning import (
    handle_missing_values,
    remove_duplicates,
    convert_data_types,
    standardize_text_columns,
    filter_dataset,
    handle_numerical_outliers,
    fix_attendance_logical_inconsistencies
)
from utils.preprocessing import (
    apply_label_encoding,
    apply_one_hot_encoding,
    apply_min_max_scaling,
    apply_standard_scaling,
    apply_attendance_feature_engineering,
    apply_numerical_transform
)
from utils.data_validation import (
    audit_dataset_quality
)
from utils.visualizations import (
    plot_quality_gauge,
    plot_missing_values,
    plot_attendance_distribution,
    plot_department_attendance,
    plot_attendance_donut,
    plot_present_vs_absent_scatter,
    plot_year_comparison
)
from utils.export_data import (
    export_dataframe
)

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & THEME INJECTION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CampusFlow – Multi-Format Data Wrangling",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Theme CSS
CAMPUSFLOW_THEME_CSS = """
<style>
    /* Theme Palettes: Background: #0B1020, Sidebar: #111A2E, Cards: #17233B, Accent: #6366F1, Text: #FFFFFF */
    .stApp {
        background-color: #0B1020;
        color: #FFFFFF;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111A2E;
        border-right: 1px solid #1E293B;
    }
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #6366F1;
    }

    /* Block Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.8rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    /* Executive Header */
    .campus-banner {
        background: linear-gradient(135deg, #17233B 0%, #111A2E 100%);
        border: 1px solid #2A3B5C;
        border-left: 5px solid #6366F1;
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4);
    }
    .campus-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .campus-subtitle {
        color: #94A3B8;
        font-size: 1.0rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .campus-badge {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 700;
        border-radius: 9999px;
        background-color: rgba(99, 102, 241, 0.2);
        color: #818CF8;
        border: 1px solid #6366F1;
        margin-left: 10px;
    }

    /* Metric Cards */
    .kpi-card {
        background-color: #17233B;
        border: 1px solid #2A3B5C;
        border-radius: 12px;
        padding: 18px 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #6366F1;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.2);
    }
    .kpi-title {
        color: #94A3B8;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 2.0rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 0.82rem;
        font-weight: 500;
    }
    .text-accent { color: #6366F1; }
    .text-success { color: #10B981; }
    .text-danger { color: #F43F5E; }
    .text-warning { color: #F59E0B; }
    .text-cyan { color: #38BDF8; }

    /* Section Subheadings */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 18px;
        margin-bottom: 14px;
        border-bottom: 1px solid #2A3B5C;
        padding-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Operation Audit Log */
    .audit-item {
        background-color: #111A2E;
        border-left: 3px solid #6366F1;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin-bottom: 8px;
        font-size: 0.86rem;
    }

    /* Dataframe wrapper */
    [data-testid="stDataFrame"] {
        border: 1px solid #2A3B5C;
        border-radius: 8px;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #818CF8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton>button {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #34D399 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
</style>
"""
st.markdown(CAMPUSFLOW_THEME_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
def init_system_session():
    """Initializes all data wrangling state variables."""
    if "raw_df" not in st.session_state:
        st.session_state.raw_df = None
    if "current_df" not in st.session_state:
        st.session_state.current_df = None
    if "dataset_name" not in st.session_state:
        st.session_state.dataset_name = "No dataset loaded"
    if "dataset_format" not in st.session_state:
        st.session_state.dataset_format = "None"
    if "operation_history" not in st.session_state:
        st.session_state.operation_history = []
    if "total_datasets_uploaded" not in st.session_state:
        st.session_state.total_datasets_uploaded = 0


init_system_session()


# -----------------------------------------------------------------------------
# 3. AUTHENTICATION GATEWAY
# -----------------------------------------------------------------------------
is_auth = render_auth_interface()
if not is_auth:
    st.stop()


# -----------------------------------------------------------------------------
# 4. DEFAULT SAMPLE DATASET LOADER HELPER
# -----------------------------------------------------------------------------
def load_default_attendance_sample():
    """Loads the synthetic 500-student raw dataset with controlled anomalies."""
    candidate_paths = [
        os.path.join(CURRENT_DIR, "data", "student_attendance_raw_500.csv"),
        os.path.join(os.path.dirname(CURRENT_DIR), "data", "student_attendance_raw_500.csv"),
        os.path.join(CURRENT_DIR, "data", "student_attendance_synthetic_500.csv")
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            st.session_state.raw_df = df.copy()
            st.session_state.current_df = df.copy()
            st.session_state.dataset_name = os.path.basename(path)
            st.session_state.dataset_format = "CSV (Sample Student Attendance)"
            st.session_state.total_datasets_uploaded += 1
            st.session_state.operation_history = [
                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Loaded synthetic student attendance dataset (500 records with controlled data quality issues)."
            ]
            return True, f"Loaded {os.path.basename(path)} ({len(df)} records)"
    return False, "Sample dataset file not found."


# -----------------------------------------------------------------------------
# 5. SIDEBAR NAVIGATION & SYSTEM CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 6px 0 16px 0;">
            <div style="font-size: 2.6rem; margin-bottom: 2px;">🎓</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">CampusFlow</div>
            <div style="font-size: 0.80rem; color: #6366F1; font-weight: 700;">Multi-Format Data Wrangling & Preprocessing</div>
        </div>
    """, unsafe_allow_html=True)

    # Current Authenticated User Badge
    current_user = st.session_state.get("user", {})
    is_demo_user = current_user.get("is_demo", False)
    auth_tag = '<span style="color:#F59E0B; font-weight:700;">[SIMULATED DEMO]</span>' if is_demo_user else '<span style="color:#10B981; font-weight:700;">[SUPABASE CLOUD]</span>'

    st.markdown(f"""
        <div style="background-color: #17233B; border: 1px solid {'#F59E0B' if is_demo_user else '#2A3B5C'}; border-radius: 8px; padding: 10px 12px; margin-bottom: 14px; font-size: 0.80rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="color: #6366F1; font-weight: 700;">👤 Active User</span>
                {auth_tag}
            </div>
            <div style="color: #FFFFFF; font-weight: 600; font-size: 0.90rem;">{current_user.get('name', 'Analyst')}</div>
            <div style="color: #94A3B8; font-size: 0.74rem;">{current_user.get('email', '')}</div>
            <div style="color: #CBD5E1; font-size: 0.72rem; margin-top: 3px;">Role: {current_user.get('role', 'Researcher')}</div>
        </div>
    """, unsafe_allow_html=True)

    nav_selection = st.radio(
        label="System Navigation",
        options=[
            "🏠 Dashboard",
            "📁 Multi-Format File Upload",
            "🛡️ Data Quality Analysis",
            "⚙️ Data Wrangling",
            "🔬 Data Preprocessing",
            "✨ Clean Dataset",
            "📊 Data Analysis"
        ],
        index=0
    )

    st.markdown("---")

    # Dataset Status
    active_rows = len(st.session_state.current_df) if st.session_state.current_df is not None else 0
    active_cols = len(st.session_state.current_df.columns) if st.session_state.current_df is not None else 0
    st.markdown(f"""
        <div style="font-size: 0.80rem; color: #94A3B8; line-height: 1.5;">
            <div><b>Active Dataset:</b> <span style="color:#FFFFFF;">{st.session_state.dataset_name}</span></div>
            <div><b>Format:</b> <span style="color:#6366F1;">{st.session_state.dataset_format}</span></div>
            <div><b>Dimensions:</b> <span style="color:#10B981;">{active_rows} rows × {active_cols} cols</span></div>
            <div><b>Operations Logged:</b> <span style="color:#38BDF8;">{len(st.session_state.operation_history)}</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        logout_user()
        st.rerun()


# Top Authentication Notice Banner
active_usr = st.session_state.get("user", {})
if active_usr.get("is_demo", False):
    st.markdown("""
        <div style="background-color: rgba(245, 158, 11, 0.12); border: 1px solid #F59E0B; border-left: 4px solid #F59E0B; border-radius: 8px; padding: 10px 16px; margin-bottom: 20px; font-size: 0.86rem; color: #FCD34D;">
            ⚠️ <b>ACADEMIC DEMO MODE ACTIVE</b>: Authentication is currently simulated locally for development and academic evaluation.
            It does <b>NOT</b> connect to Supabase Cloud and must <b>NOT</b> be treated as real secure authentication.
            To connect real cloud authentication, add your credentials in <code>.streamlit/secrets.toml</code> or <code>.env</code>.
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="background-color: rgba(16, 185, 129, 0.12); border: 1px solid #10B981; border-left: 4px solid #10B981; border-radius: 8px; padding: 8px 16px; margin-bottom: 20px; font-size: 0.84rem; color: #6EE7B7;">
            🟢 <b>Supabase Cloud Authentication Active</b>: Verified secure session authenticated via Supabase.
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. AUTO-LOAD SAMPLE DATASET IF NO DATASET ACTIVE
# -----------------------------------------------------------------------------
if st.session_state.current_df is None:
    load_default_attendance_sample()


# Audit current dataset
audit_res = audit_dataset_quality(st.session_state.current_df)


# =============================================================================
# SECTION 1: DASHBOARD
# =============================================================================
if nav_selection == "🏠 Dashboard":
    st.markdown("""
        <div class="campus-banner">
            <div class="campus-title">
                <span>🎓 CampusFlow Executive Dashboard</span>
                <span class="campus-badge">Data Wrangling and Preprocessing</span>
            </div>
            <p class="campus-subtitle">Multi-Format Data Wrangling & Preprocessing • Real-time Quality Score and Transformation Pipeline.</p>
        </div>
    """, unsafe_allow_html=True)

    # 8 KPI Metric Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📂 Uploaded Datasets</div>
                <div class="kpi-value text-accent">{st.session_state.total_datasets_uploaded}</div>
                <div class="kpi-sub text-cyan">Active: {st.session_state.dataset_name[:18]}...</div>
            </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">👥 Total Records</div>
                <div class="kpi-value">{audit_res['total_rows']}</div>
                <div class="kpi-sub text-success">Rows Currently in Memory</div>
            </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📊 Total Columns</div>
                <div class="kpi-value text-cyan">{audit_res['total_columns']}</div>
                <div class="kpi-sub text-cyan">Dataset Features</div>
            </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">❓ Missing Values</div>
                <div class="kpi-value {'text-danger' if audit_res['total_nulls'] > 0 else 'text-success'}">{audit_res['total_nulls']}</div>
                <div class="kpi-sub">{audit_res['null_percentage']}% of cells</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    m5, m6, m7, m8 = st.columns(4)
    with m5:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📑 Duplicate Records</div>
                <div class="kpi-value {'text-danger' if audit_res['dup_rows_count'] > 0 else 'text-success'}">{audit_res['dup_rows_count']}</div>
                <div class="kpi-sub">Exact duplicate rows</div>
            </div>
        """, unsafe_allow_html=True)
    with m6:
        total_invalids = audit_res['total_negatives'] + audit_res['attendance_anomalies']
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">⚠️ Invalid Values</div>
                <div class="kpi-value {'text-warning' if total_invalids > 0 else 'text-success'}">{total_invalids}</div>
                <div class="kpi-sub">Negative & domain errors</div>
            </div>
        """, unsafe_allow_html=True)
    with m7:
        cleaned_cnt = audit_res['total_rows'] - audit_res['dup_rows_count']
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">✨ Cleaned Records</div>
                <div class="kpi-value text-success">{cleaned_cnt}</div>
                <div class="kpi-sub">Unique verified records</div>
            </div>
        """, unsafe_allow_html=True)
    with m8:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🛡️ Data Quality Score</div>
                <div class="kpi-value {'text-success' if audit_res['quality_score'] >= 85 else ('text-warning' if audit_res['quality_score'] >= 65 else 'text-danger')}">{audit_res['quality_score']}%</div>
                <div class="kpi-sub">Systemic Health Index</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visual Row: Quality Gauge + Dataset Overview Table
    v_col1, v_col2 = st.columns([1.1, 2])
    with v_col1:
        st.markdown('<div class="section-title">🛡️ Data Quality Health Index</div>', unsafe_allow_html=True)
        st.plotly_chart(plot_quality_gauge(audit_res['quality_score']), use_container_width=True)

    with v_col2:
        st.markdown('<div class="section-title">📋 Active Dataset Quick Glance</div>', unsafe_allow_html=True)
        if st.session_state.current_df is not None:
            st.dataframe(st.session_state.current_df.head(6), use_container_width=True, hide_index=True)
            st.caption(f"Showing first 6 of {len(st.session_state.current_df)} rows. Use 'Data Wrangling' or 'Clean Dataset' to explore further.")

    # Processing History Log
    st.markdown('<div class="section-title">📜 Audit Trail & Processing History</div>', unsafe_allow_html=True)
    if st.session_state.operation_history:
        for hist_entry in reversed(st.session_state.operation_history[-6:]):
            st.markdown(f'<div class="audit-item"><b>{hist_entry}</b></div>', unsafe_allow_html=True)
    else:
        st.info("No wrangling operations performed yet. Load a dataset or apply transformations.")


# =============================================================================
# SECTION 2: MULTI-FORMAT FILE UPLOAD
# =============================================================================
elif nav_selection == "📁 Multi-Format File Upload":
    st.markdown("""
        <div class="campus-banner">
            <div class="campus-title">
                <span>📁 Multi-Format Data Ingestion Engine</span>
                <span class="campus-badge">13 Actual Formats Supported</span>
            </div>
            <p class="campus-subtitle">Upload CSV, TSV, XLSX, XLS, JSON, JSONL, NDJSON, XML, TXT, DAT, Parquet, and GZIP compressed archives.</p>
        </div>
    """, unsafe_allow_html=True)

    # Format Support Chips
    st.markdown("""
        <div style="background-color: #17233B; border: 1px solid #2A3B5C; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
            <div style="color: #6366F1; font-weight: 700; margin-bottom: 6px;">Supported File Formats:</div>
            <span style="color:#38BDF8; font-weight:600;">Structured:</span> CSV, TSV, XLSX, XLS, JSON, JSONL, NDJSON, XML, TXT, DAT, Parquet &nbsp;|&nbsp; 
            <span style="color:#10B981; font-weight:600;">Compressed:</span> CSV.GZ, JSON.GZ
        </div>
    """, unsafe_allow_html=True)

    # Option to reload default sample dataset
    samp_col1, samp_col2 = st.columns([3, 1])
    with samp_col1:
        st.markdown("<p style='color:#CBD5E1; font-size:0.9rem; padding-top:6px;'>Need test data? Load our verified 500-student attendance dataset with controlled quality issues:</p>", unsafe_allow_html=True)
    with samp_col2:
        if st.button("📥 Load Sample 500 Dataset", use_container_width=True):
            success, msg = load_default_attendance_sample()
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("<br>", unsafe_allow_html=True)

    # File Upload Component
    uploaded_files = st.file_uploader(
        label="Drag and drop or browse files to ingest into CampusFlow:",
        type=["csv", "tsv", "xlsx", "xls", "json", "jsonl", "ndjson", "xml", "txt", "dat", "parquet", "gz"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.markdown('<div class="section-title">📂 Uploaded File Queue</div>', unsafe_allow_html=True)
        
        for file in uploaded_files:
            ext, fmt_name, is_comp = detect_file_format(file.name)
            size_str = format_file_size(len(file.getvalue()))
            
            with st.expander(f"📄 {file.name} ({fmt_name} - {size_str})", expanded=True):
                col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
                
                # Format specific options
                parse_options = {}
                with col_cfg1:
                    if ext in [".csv", ".txt", ".dat", ".csv.gz"]:
                        parse_options["delimiter"] = st.selectbox(
                            f"Delimiter for {file.name}:",
                            ["Auto-Detect", ",", "\t", ";", "|", " "],
                            key=f"delim_{file.name}"
                        )
                with col_cfg2:
                    if ext in [".xlsx", ".xls"]:
                        sheets = get_excel_sheet_names(file)
                        parse_options["sheet_name"] = st.selectbox(
                            f"Select Worksheet for {file.name}:",
                            sheets,
                            key=f"sheet_{file.name}"
                        )
                    if ext in [".json", ".json.gz"]:
                        parse_options["flatten_json"] = st.checkbox("Flatten Nested JSON structures", value=True, key=f"flatten_{file.name}")
                with col_cfg3:
                    if st.button(f"🚀 Ingest & Set as Active", key=f"btn_ingest_{file.name}", use_container_width=True):
                        try:
                            loaded_df, load_msg = load_file_content(file, parse_options)
                            st.session_state.raw_df = loaded_df.copy()
                            st.session_state.current_df = loaded_df.copy()
                            st.session_state.dataset_name = file.name
                            st.session_state.dataset_format = fmt_name
                            st.session_state.total_datasets_uploaded += 1
                            st.session_state.operation_history.append(
                                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Ingested file '{file.name}' ({len(loaded_df)} records, {len(loaded_df.columns)} columns)."
                            )
                            st.success(load_msg)
                            time.sleep(0.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to parse {file.name}: {str(e)}")

    # Active dataset preview
    if st.session_state.current_df is not None:
        st.markdown('<div class="section-title">👁️ Active Working Dataset Preview</div>', unsafe_allow_html=True)
        st.dataframe(st.session_state.current_df.head(10), use_container_width=True, hide_index=True)


# =============================================================================
# SECTION 3: DATA QUALITY ANALYSIS
# =============================================================================
elif nav_selection == "🛡️ Data Quality Analysis":
    st.markdown(f"""
        <div class="campus-banner">
            <div class="campus-title">
                <span>🛡️ Automated Data Quality Audit</span>
                <span class="campus-badge">Quality Health: {audit_res['quality_score']}%</span>
            </div>
            <p class="campus-subtitle">Systemic diagnostic scanning across missing cells, duplicate IDs, outliers, text inconsistencies, and mathematical bounds.</p>
        </div>
    """, unsafe_allow_html=True)

    # 4 Quick Health Cards
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Missing Values</div>
                <div class="kpi-value {'text-danger' if audit_res['total_nulls'] > 0 else 'text-success'}">{audit_res['total_nulls']}</div>
                <div class="kpi-sub">{len(audit_res['cols_with_nulls'])} column(s) affected</div>
            </div>
        """, unsafe_allow_html=True)
    with q2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Duplicate IDs</div>
                <div class="kpi-value {'text-danger' if audit_res['dup_ids_count'] > 0 else 'text-success'}">{audit_res['dup_ids_count']}</div>
                <div class="kpi-sub">Column: {audit_res['id_column_used']}</div>
            </div>
        """, unsafe_allow_html=True)
    with q3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Negative Numbers</div>
                <div class="kpi-value {'text-danger' if audit_res['total_negatives'] > 0 else 'text-success'}">{audit_res['total_negatives']}</div>
                <div class="kpi-sub">Violating non-negative rule</div>
            </div>
        """, unsafe_allow_html=True)
    with q4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Outliers (IQR)</div>
                <div class="kpi-value {'text-warning' if audit_res['total_outliers'] > 0 else 'text-success'}">{audit_res['total_outliers']}</div>
                <div class="kpi-sub">Statistical anomalies</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Missing Values Breakdown Chart
    st.markdown('<div class="section-title">🔍 Missing Values & Null Audit</div>', unsafe_allow_html=True)
    col_null1, col_null2 = st.columns([1.5, 1])
    with col_null1:
        st.plotly_chart(plot_missing_values(audit_res['cols_with_nulls'], audit_res['total_rows']), use_container_width=True)
    with col_null2:
        if audit_res['cols_with_nulls']:
            st.markdown("<p style='color:#F43F5E; font-weight:600;'>Columns Requiring Imputation or Removal:</p>", unsafe_allow_html=True)
            for c_name, c_cnt in audit_res['cols_with_nulls'].items():
                st.markdown(f"• **`{c_name}`**: {c_cnt} missing cells ({(c_cnt/audit_res['total_rows'])*100:.1f}%)")
        else:
            st.success("✅ Perfect Integrity: Zero missing values across all features!")

    # Duplicate & Consistency Breakdown
    st.markdown('<div class="section-title">📑 Duplicates & Domain Anomaly Audit</div>', unsafe_allow_html=True)
    col_dup1, col_dup2 = st.columns(2)
    with col_dup1:
        st.markdown("""
            <div style="background-color: #17233B; border: 1px solid #2A3B5C; border-radius: 8px; padding: 14px;">
                <div style="color: #6366F1; font-weight: 700; margin-bottom: 8px;">🆔 Identity & Row Duplication:</div>
        """, unsafe_allow_html=True)
        st.write(f"• **Duplicate Rows:** {audit_res['dup_rows_count']} rows")
        st.write(f"• **Duplicate Student IDs:** {audit_res['dup_ids_count']} instances in `{audit_res['id_column_used']}`")
        st.write(f"• **Duplicate Columns:** {len(audit_res['duplicate_columns'])} identical column pairs")
        st.write(f"• **Empty Columns (100% null):** {len(audit_res['empty_columns'])}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_dup2:
        st.markdown("""
            <div style="background-color: #17233B; border: 1px solid #2A3B5C; border-radius: 8px; padding: 14px;">
                <div style="color: #6366F1; font-weight: 700; margin-bottom: 8px;">📐 Mathematical & Text Quality:</div>
        """, unsafe_allow_html=True)
        st.write(f"• **Negative Values:** {audit_res['total_negatives']} cells")
        st.write(f"• **Attendance Balance Mismatches:** {audit_res['attendance_anomalies']} rows (Present > Total or Sum error)")
        st.write(f"• **Inconsistent Text / Extra Spaces:** {audit_res['total_text_issues']} cells")
        st.write(f"• **Statistical Outliers:** {audit_res['total_outliers']} values")
        st.markdown("</div>", unsafe_allow_html=True)

    # Schema Inspector
    st.markdown('<div class="section-title">🧬 Feature Schema & Data Types</div>', unsafe_allow_html=True)
    schema_records = []
    for c, dt in audit_res['dtypes_map'].items():
        sample_val = str(st.session_state.current_df[c].dropna().iloc[0]) if not st.session_state.current_df[c].dropna().empty else "N/A"
        schema_records.append({
            "Column Name": c,
            "Data Type": dt,
            "Non-Null Count": int(st.session_state.current_df[c].notnull().sum()),
            "Sample Value": sample_val
        })
    st.dataframe(pd.DataFrame(schema_records), use_container_width=True, hide_index=True)


# =============================================================================
# SECTION 4: DATA WRANGLING
# =============================================================================
elif nav_selection == "⚙️ Data Wrangling":
    st.markdown("""
        <div class="campus-banner">
            <div class="campus-title">
                <span>⚙️ Interactive Data Wrangling Workbench</span>
                <span class="campus-badge">Preview Before Commit</span>
            </div>
            <p class="campus-subtitle">Clean missing values, deduplicate, convert types, standardize department text, filter, and rectify domain anomalies.</p>
        </div>
    """, unsafe_allow_html=True)

    curr_df = st.session_state.current_df.copy()

    # Academic domain one-click quick fix
    st.markdown("""
        <div style="background-color: #17233B; border: 1px solid #6366F1; border-radius: 8px; padding: 14px 18px; margin-bottom: 22px;">
            <div style="color: #818CF8; font-weight: 700; font-size: 1.05rem; margin-bottom: 4px;">⚡ One-Click Academic Attendance Repair</div>
            <div style="color: #CBD5E1; font-size: 0.88rem; margin-bottom: 10px;">
                Automatically standardizes department naming (casing & spacing), rectifies negative attendance values, caps Present &le; Total Classes, and recalculates Absent = Total - Present.
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Apply Automated College Attendance Logic Repair", use_container_width=True):
        repaired_df, sum_msg, cnt = fix_attendance_logical_inconsistencies(curr_df)
        repaired_df, dept_msg, _ = standardize_text_columns(repaired_df, ["Department"] if "Department" in repaired_df.columns else [], ["department_fix", "strip"])
        st.session_state.current_df = repaired_df
        st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Automated Attendance Repair: {sum_msg} {dept_msg}")
        st.success("Automated repair applied successfully!")
        time.sleep(0.5)
        st.rerun()

    # Operations Tabs
    t_missing, t_dup, t_text, t_types, t_filter, t_outlier = st.tabs([
        "❓ Missing Values", "📑 Duplicates", "🔤 Text Standardize", "🧬 Types & Rename", "🔍 Filter & Sort", "📉 Outliers"
    ])

    # Tab 1: Missing Values
    with t_missing:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Handle Missing Data via Drop or Imputation:</p>", unsafe_allow_html=True)
        m_c1, m_c2, m_c3 = st.columns(3)
        with m_c1:
            strategy = st.selectbox(
                "Imputation Strategy:",
                ["Impute with Mean (Numeric)", "Impute with Median (Numeric)", "Impute with Mode (Most Frequent)", "Drop Rows with Nulls", "Drop Entire Column", "Custom Fill Value"]
            )
        with m_c2:
            target_cols = st.multiselect("Select Target Columns:", options=curr_df.columns.tolist(), default=curr_df.columns[curr_df.isnull().any()].tolist() if curr_df.isnull().any().any() else curr_df.columns.tolist()[:3])
        with m_c3:
            custom_fill = st.text_input("Custom Fill Value (if selected):", value="Unknown")

        if st.button("Preview Missing Value Transformation", key="btn_prev_missing"):
            preview_df, sum_text, aff = handle_missing_values(curr_df, strategy, target_cols, custom_fill)
            st.info(sum_text)
            st.dataframe(preview_df.head(6), use_container_width=True)

        if st.button("✅ Apply Missing Value Operation", key="btn_apply_missing"):
            new_df, sum_text, aff = handle_missing_values(curr_df, strategy, target_cols, custom_fill)
            st.session_state.current_df = new_df
            st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Missing Value Handling: {sum_text}")
            st.success("Operation committed to dataset!")
            time.sleep(0.5)
            st.rerun()

    # Tab 2: Duplicates
    with t_dup:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Deduplicate Rows or Primary Keys:</p>", unsafe_allow_html=True)
        d_c1, d_c2 = st.columns(2)
        with d_c1:
            dup_subset = st.multiselect("Deduplicate based on subset of columns (Leave empty for all columns):", options=curr_df.columns.tolist(), default=["Student_ID"] if "Student_ID" in curr_df.columns else [])
        with d_c2:
            keep_opt = st.selectbox("Keep Which Record?", ["first", "last"])

        if st.button("Preview Deduplication", key="btn_prev_dup"):
            prev_df, d_msg, dropped = remove_duplicates(curr_df, dup_subset, keep_opt)
            st.info(d_msg)
            st.write(f"Row count will reduce from {len(curr_df)} to {len(prev_df)}.")

        if st.button("✅ Remove Duplicate Records", key="btn_apply_dup"):
            new_df, d_msg, dropped = remove_duplicates(curr_df, dup_subset, keep_opt)
            st.session_state.current_df = new_df
            st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Deduplication: {d_msg}")
            st.success(d_msg)
            time.sleep(0.5)
            st.rerun()

    # Tab 3: Text Standardization
    with t_text:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Standardize Text Formats, Strip Whitespace & Canonicalize Departments:</p>", unsafe_allow_html=True)
        text_cols = [c for c in curr_df.columns if curr_df[c].dtype == object or pd.api.types.is_string_dtype(curr_df[c])]
        txt_target = st.multiselect("Select Text Columns:", options=text_cols, default=["Department", "Student_Name"] if "Department" in curr_df.columns and "Student_Name" in curr_df.columns else text_cols[:2])
        txt_ops = st.multiselect("Select Standardization Operations:", ["strip", "normalize_spaces", "uppercase", "lowercase", "titlecase", "department_fix"], default=["strip", "department_fix"])

        if st.button("Preview Text Standardization", key="btn_prev_text"):
            prev_df, t_msg, _ = standardize_text_columns(curr_df, txt_target, txt_ops)
            st.info(t_msg)
            st.dataframe(prev_df[txt_target].head(8) if txt_target else prev_df.head(8), use_container_width=True)

        if st.button("✅ Apply Text Standardization", key="btn_apply_text"):
            new_df, t_msg, _ = standardize_text_columns(curr_df, txt_target, txt_ops)
            st.session_state.current_df = new_df
            st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Text Standardization: {t_msg}")
            st.success(t_msg)
            time.sleep(0.5)
            st.rerun()

    # Tab 4: Types & Rename
    with t_types:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Cast Data Types or Rename Column Headers:</p>", unsafe_allow_html=True)
        r_c1, r_c2 = st.columns(2)
        with r_c1:
            st.markdown("<b>Convert Column Types:</b>", unsafe_allow_html=True)
            col_to_cast = st.selectbox("Choose Column to Convert:", curr_df.columns.tolist())
            target_cast = st.selectbox("Target Data Type:", ["int", "float", "str", "category", "datetime"])
            if st.button(f"Convert '{col_to_cast}' to {target_cast}"):
                new_df, c_msg, _ = convert_data_types(curr_df, {col_to_cast: target_cast})
                st.session_state.current_df = new_df
                st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Type Cast: {c_msg}")
                st.success(c_msg)
                time.sleep(0.5)
                st.rerun()

        with r_c2:
            st.markdown("<b>Rename Feature Column:</b>", unsafe_allow_html=True)
            col_to_rename = st.selectbox("Choose Column to Rename:", curr_df.columns.tolist(), key="sel_rename")
            new_col_name = st.text_input("New Name:", value=col_to_rename)
            if st.button(f"Rename Column"):
                if new_col_name and new_col_name != col_to_rename:
                    st.session_state.current_df = curr_df.rename(columns={col_to_rename: new_col_name})
                    st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Renamed '{col_to_rename}' -> '{new_col_name}'")
                    st.success(f"Renamed '{col_to_rename}' to '{new_col_name}'!")
                    time.sleep(0.5)
                    st.rerun()

    # Tab 5: Filter & Sort
    with t_filter:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Conditional Filtering & Sorting:</p>", unsafe_allow_html=True)
        flt_col1, flt_col2, flt_col3 = st.columns(3)
        with flt_col1:
            f_col = st.selectbox("Filter Column:", curr_df.columns.tolist(), key="flt_c")
        with flt_col2:
            f_op = st.selectbox("Condition Operator:", ["==", "!=", "contains", ">", "<", ">=", "<=", "is_null", "not_null"])
        with flt_col3:
            f_val = st.text_input("Condition Value:", value="AIML" if f_col == "Department" else "75")

        if st.button("Apply Filter Query"):
            f_df, f_msg, m_cnt = filter_dataset(curr_df, f_col, f_op, f_val)
            st.session_state.current_df = f_df
            st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Filter Applied: {f_msg}")
            st.success(f_msg)
            time.sleep(0.5)
            st.rerun()

    # Tab 6: Outliers
    with t_outlier:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Detect & Handle Statistical Outliers via IQR:</p>", unsafe_allow_html=True)
        num_cols = [c for c in curr_df.columns if pd.api.types.is_numeric_dtype(curr_df[c])]
        if num_cols:
            out_col = st.selectbox("Select Numeric Feature for Outlier Treatment:", num_cols)
            out_method = st.selectbox("Treatment Action:", ["clip", "drop"])
            out_factor = st.slider("IQR Threshold Factor:", min_value=1.0, max_value=3.0, value=1.5, step=0.1)

            if st.button("Preview Outlier Treatment"):
                p_out_df, out_msg, aff_cnt = handle_numerical_outliers(curr_df, out_col, out_method, out_factor)
                st.info(out_msg)

            if st.button("✅ Apply Outlier Operation"):
                new_out_df, out_msg, aff_cnt = handle_numerical_outliers(curr_df, out_col, out_method, out_factor)
                st.session_state.current_df = new_out_df
                st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Outlier Treatment: {out_msg}")
                st.success(out_msg)
                time.sleep(0.5)
                st.rerun()
        else:
            st.warning("No numeric columns available for outlier analysis.")


# =============================================================================
# SECTION 5: DATA PREPROCESSING
# =============================================================================
elif nav_selection == "🔬 Data Preprocessing":
    st.markdown("""
        <div class="campus-banner">
            <div class="campus-title">
                <span>🔬 Data Preprocessing & Feature Engineering</span>
                <span class="campus-badge">Machine Learning Ready</span>
            </div>
            <p class="campus-subtitle">Label encoding, one-hot encoding, Min-Max & Standard scaling (with identifier protection), and academic feature engineering.</p>
        </div>
    """, unsafe_allow_html=True)

    curr_df = st.session_state.current_df.copy()

    prep_t1, prep_t2, prep_t3, prep_t4 = st.tabs([
        "🎓 Academic Feature Engineering", "🏷️ Categorical Encoding", "📏 Scaling & Normalization", "📐 Mathematical Transforms"
    ])

    # Tab 1: Academic Feature Engineering
    with prep_t1:
        st.markdown("""
            <div style="background-color: #17233B; border: 1px solid #2A3B5C; border-radius: 8px; padding: 14px; margin-bottom: 16px;">
                <div style="color: #6366F1; font-weight: 700;">Academic Institutional Features:</div>
                <div style="color: #CBD5E1; font-size: 0.88rem; margin-top: 4px;">
                    Generates <b>Attendance_Percentage</b>, <b>Attendance_Status</b> (Good &ge; 75% vs Low &lt; 75%), <b>Risk_Category</b> (Safe Zone, Moderate, Critical), and <b>Absent_Ratio</b>.
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Generate Academic Attendance Features", use_container_width=True):
            eng_df, eng_msg, created = apply_attendance_feature_engineering(curr_df)
            st.session_state.current_df = eng_df
            st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Feature Engineering: {eng_msg}")
            st.success(eng_msg)
            time.sleep(0.5)
            st.rerun()

    # Tab 2: Categorical Encoding
    with prep_t2:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Convert Categorical Variables for Machine Learning:</p>", unsafe_allow_html=True)
        cat_cols = [c for c in curr_df.columns if curr_df[c].dtype == object or pd.api.types.is_string_dtype(curr_df[c])]
        
        enc_col1, enc_col2 = st.columns(2)
        with enc_col1:
            st.markdown("<b>Label Encoding (Ordinal / Integer mapping):</b>", unsafe_allow_html=True)
            lbl_targets = st.multiselect("Select Categorical Columns for Label Encoding:", cat_cols, default=["Department"] if "Department" in cat_cols else cat_cols[:1])
            if st.button("Apply Label Encoding"):
                if lbl_targets:
                    lbl_df, l_msg, mapping = apply_label_encoding(curr_df, lbl_targets)
                    st.session_state.current_df = lbl_df
                    st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Label Encoding: {l_msg}")
                    st.success(l_msg)
                    time.sleep(0.5)
                    st.rerun()

        with enc_col2:
            st.markdown("<b>One-Hot Encoding (Dummy Variables):</b>", unsafe_allow_html=True)
            ohe_targets = st.multiselect("Select Columns for One-Hot Encoding:", cat_cols, default=["Department"] if "Department" in cat_cols else [])
            drop_first_opt = st.checkbox("Drop first dummy column (avoid dummy trap)", value=False)
            if st.button("Apply One-Hot Encoding"):
                if ohe_targets:
                    ohe_df, o_msg, new_cols = apply_one_hot_encoding(curr_df, ohe_targets, drop_first=drop_first_opt)
                    st.session_state.current_df = ohe_df
                    st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] One-Hot Encoding: {o_msg}")
                    st.success(o_msg)
                    time.sleep(0.5)
                    st.rerun()

    # Tab 3: Scaling & Normalization
    with prep_t3:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Scale Numerical Features (Identifiers like Student_ID are automatically protected):</p>", unsafe_allow_html=True)
        num_scale_cols = [c for c in curr_df.columns if pd.api.types.is_numeric_dtype(curr_df[c]) and "id" not in c.lower()]

        scale_targets = st.multiselect("Select Features to Scale:", num_scale_cols, default=[c for c in ["Total_Classes", "Present", "Absent", "Attendance_Percentage"] if c in num_scale_cols])
        scale_type = st.radio("Scaling Algorithm:", ["Min-Max Scaling (Range 0 to 1)", "Standard Scaling (Z-Score Mean 0, Variance 1)"])

        if st.button("Preview Scaled Output"):
            if scale_type == "Min-Max Scaling (Range 0 to 1)":
                prev_s_df, s_msg, sc_cols = apply_min_max_scaling(curr_df, scale_targets)
            else:
                prev_s_df, s_msg, sc_cols = apply_standard_scaling(curr_df, scale_targets)
            st.info(s_msg)
            st.dataframe(prev_s_df[sc_cols].head(6) if sc_cols else prev_s_df.head(6), use_container_width=True)

        if st.button("✅ Apply Scaling to Dataset"):
            if scale_type == "Min-Max Scaling (Range 0 to 1)":
                new_s_df, s_msg, sc_cols = apply_min_max_scaling(curr_df, scale_targets)
            else:
                new_s_df, s_msg, sc_cols = apply_standard_scaling(curr_df, scale_targets)
            st.session_state.current_df = new_s_df
            st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Feature Scaling: {s_msg}")
            st.success(s_msg)
            time.sleep(0.5)
            st.rerun()

    # Tab 4: Mathematical Transforms
    with prep_t4:
        st.markdown("<p style='color:#CBD5E1; font-weight:600;'>Non-Linear Mathematical Transformations:</p>", unsafe_allow_html=True)
        num_trans_cols = [c for c in curr_df.columns if pd.api.types.is_numeric_dtype(curr_df[c])]
        if num_trans_cols:
            trans_col = st.selectbox("Choose Numeric Column:", num_trans_cols)
            trans_func = st.selectbox("Transformation Function:", ["log", "sqrt", "square"])

            if st.button("Apply Mathematical Transform"):
                t_df, t_msg, new_c = apply_numerical_transform(curr_df, trans_col, trans_func)
                st.session_state.current_df = t_df
                st.session_state.operation_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Mathematical Transform: {t_msg}")
                st.success(t_msg)
                time.sleep(0.5)
                st.rerun()


# =============================================================================
# SECTION 6: CLEAN DATASET (MAIN FEATURE)
# =============================================================================
elif nav_selection == "✨ Clean Dataset":
    st.markdown("""
        <div class="campus-banner">
            <div class="campus-title">
                <span>✨ Final Cleaned Dataset & Export Center</span>
                <span class="campus-badge">Main Showcase Feature</span>
            </div>
            <p class="campus-subtitle">Verified clean dataset, before-and-after audit comparisons, operation logs, and cross-format export downloads.</p>
        </div>
    """, unsafe_allow_html=True)

    raw = st.session_state.raw_df
    cleaned = st.session_state.current_df

    raw_audit = audit_dataset_quality(raw)
    clean_audit = audit_dataset_quality(cleaned)

    # Before and After Comparison KPI Cards
    st.markdown('<div class="section-title">📊 Before vs After Transformation Audit</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Records Retained</div>
                <div class="kpi-value text-accent">{len(cleaned)}</div>
                <div class="kpi-sub text-cyan">Initial: {len(raw) if raw is not None else 0} rows</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Missing Values</div>
                <div class="kpi-value text-success">{clean_audit['total_nulls']}</div>
                <div class="kpi-sub text-danger">Initial: {raw_audit['total_nulls']} cells</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Duplicate Records</div>
                <div class="kpi-value text-success">{clean_audit['dup_rows_count']}</div>
                <div class="kpi-sub text-danger">Initial: {raw_audit['dup_rows_count']} rows</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Data Quality Score</div>
                <div class="kpi-value text-success">{clean_audit['quality_score']}%</div>
                <div class="kpi-sub text-cyan">Initial: {raw_audit['quality_score']}%</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Operations Performed Audit History
    st.markdown('<div class="section-title">📜 Chronological Cleaning Pipeline Executed</div>', unsafe_allow_html=True)
    if st.session_state.operation_history:
        for idx, op in enumerate(st.session_state.operation_history, start=1):
            st.markdown(f'<div class="audit-item"><b>Step {idx}:</b> {op}</div>', unsafe_allow_html=True)
    else:
        st.info("No cleaning transformations recorded.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Export Center: Cross-Format Download
    st.markdown('<div class="section-title">📥 Cross-Format Data Export</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#CBD5E1; font-size:0.9rem;'>Export the cleaned dataset to any desired format. You can ingest one format (e.g. Parquet or XML) and export into another (e.g. XLSX or JSONL):</p>", unsafe_allow_html=True)

    exp_col1, exp_col2, exp_col3 = st.columns([1.5, 1.5, 2])
    with exp_col1:
        export_fmt = st.selectbox("Select Target Export Format:", ["CSV", "XLSX", "JSON", "JSONL", "PARQUET"])
    with exp_col2:
        export_base_name = st.text_input("Export Filename:", value=f"CampusFlow_Cleaned_{st.session_state.dataset_name.split('.')[0]}")
    with exp_col3:
        try:
            bytes_data, mime, ext = export_dataframe(cleaned, export_fmt)
            final_filename = f"{export_base_name}{ext}"
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label=f"💾 Download Cleaned Dataset ({export_fmt})",
                data=bytes_data,
                file_name=final_filename,
                mime=mime,
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Export Error: {str(e)}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Display Final Table
    st.markdown('<div class="section-title">📋 Cleaned Dataset Viewer</div>', unsafe_allow_html=True)
    st.dataframe(cleaned, use_container_width=True, height=520, hide_index=True)


# =============================================================================
# SECTION 7: DATA ANALYSIS
# =============================================================================
elif nav_selection == "📊 Data Analysis":
    st.markdown("""
        <div class="campus-banner">
            <div class="campus-title">
                <span>📊 Academic Attendance Data Analysis</span>
                <span class="campus-badge">Statistical Insights</span>
            </div>
            <p class="campus-subtitle">Exploratory visual analytics using the verified, preprocessed dataset with interactive multi-attribute filters.</p>
        </div>
    """, unsafe_allow_html=True)

    ana_df = st.session_state.current_df.copy()

    # Ensure attendance features are available
    if "Attendance_Percentage" not in ana_df.columns:
        ana_df, _, _ = apply_attendance_feature_engineering(ana_df)

    # Interactive Filters
    st.markdown('<div class="section-title">🔍 Interactive Filters</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        dept_options = sorted(ana_df["Department"].dropna().unique().tolist()) if "Department" in ana_df.columns else []
        selected_depts = st.multiselect("Filter Departments:", options=dept_options, default=dept_options)
    with f2:
        year_options = sorted(ana_df["Year"].dropna().unique().tolist()) if "Year" in ana_df.columns else []
        selected_years = st.multiselect("Filter Academic Year:", options=year_options, default=year_options)
    with f3:
        status_options = sorted(ana_df["Attendance_Status"].dropna().unique().tolist()) if "Attendance_Status" in ana_df.columns else []
        selected_statuses = st.multiselect("Filter Attendance Status:", options=status_options, default=status_options)

    # Apply filters
    filtered_ana = ana_df.copy()
    if selected_depts and "Department" in filtered_ana.columns:
        filtered_ana = filtered_ana[filtered_ana["Department"].isin(selected_depts)]
    if selected_years and "Year" in filtered_ana.columns:
        filtered_ana = filtered_ana[filtered_ana["Year"].isin(selected_years)]
    if selected_statuses and "Attendance_Status" in filtered_ana.columns:
        filtered_ana = filtered_ana[filtered_ana["Attendance_Status"].isin(selected_statuses)]

    if filtered_ana.empty:
        st.warning("No records match the selected filter criteria. Please broaden your selection.")
        st.stop()

    # Summary Metrics
    st.markdown('<div class="section-title">📈 Statistical Summary</div>', unsafe_allow_html=True)
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        avg_att = filtered_ana["Attendance_Percentage"].mean()
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Average Attendance</div>
                <div class="kpi-value text-accent">{avg_att:.2f}%</div>
                <div class="kpi-sub text-success">Institutional Mean</div>
            </div>
        """, unsafe_allow_html=True)
    with s_col2:
        med_att = filtered_ana["Attendance_Percentage"].median()
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Median Attendance</div>
                <div class="kpi-value text-cyan">{med_att:.2f}%</div>
                <div class="kpi-sub text-cyan">50th Percentile</div>
            </div>
        """, unsafe_allow_html=True)
    with s_col3:
        defaulters = (filtered_ana["Attendance_Percentage"] < 75.0).sum()
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Defaulters (&lt; 75%)</div>
                <div class="kpi-value text-danger">{defaulters}</div>
                <div class="kpi-sub text-danger">{(defaulters/len(filtered_ana))*100:.1f}% at risk of detention</div>
            </div>
        """, unsafe_allow_html=True)
    with s_col4:
        eligible = (filtered_ana["Attendance_Percentage"] >= 75.0).sum()
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Eligible (&ge; 75%)</div>
                <div class="kpi-value text-success">{eligible}</div>
                <div class="kpi-sub text-success">{(eligible/len(filtered_ana))*100:.1f}% exam compliant</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row 1: Histogram + Donut
    ch_r1_c1, ch_r1_c2 = st.columns([1.2, 1])
    with ch_r1_c1:
        st.plotly_chart(plot_attendance_distribution(filtered_ana), use_container_width=True)
    with ch_r1_c2:
        st.plotly_chart(plot_attendance_donut(filtered_ana), use_container_width=True)

    # Charts Row 2: Department Bar + Scatter Plot
    ch_r2_c1, ch_r2_c2 = st.columns(2)
    with ch_r2_c1:
        st.plotly_chart(plot_department_attendance(filtered_ana), use_container_width=True)
    with ch_r2_c2:
        st.plotly_chart(plot_present_vs_absent_scatter(filtered_ana), use_container_width=True)

    # Charts Row 3: Year-wise Comparison
    if "Year" in filtered_ana.columns:
        st.markdown('<div class="section-title">🏛️ Academic Year-wise Performance Variance</div>', unsafe_allow_html=True)
        st.plotly_chart(plot_year_comparison(filtered_ana), use_container_width=True)


# -----------------------------------------------------------------------------
# 7. FOOTER
# -----------------------------------------------------------------------------
st.markdown("<br><hr style='border-color: #2A3B5C;'><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #94A3B8; font-size: 0.85rem; padding-bottom: 24px;">
        <b>CampusFlow – Multi-Format Data Wrangling and Preprocessing System</b><br>
        Developed for Academic Evaluation in Data Wrangling & Preprocessing • Compatible with VS Code on Windows
    </div>
""", unsafe_allow_html=True)
