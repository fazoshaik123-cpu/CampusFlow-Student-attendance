# 🎓 CampusFlow – Multi-Format Data Wrangling & Preprocessing System

**CampusFlow** is a comprehensive, production-ready college academic project for the subject **Data Wrangling and Preprocessing (DWP)**. Built using **Python, Streamlit, Pandas, NumPy, Plotly, Scikit-learn, and Supabase Authentication**, it provides an end-to-end web workbench to ingest, inspect, clean, wrangle, preprocess, visualize, and cross-export datasets across 13 distinct structured and compressed formats.

---

## 🌟 Executive Project Overview

- **Academic Subject**: Data Wrangling and Preprocessing
- **Core System Architecture**: Multi-Format Ingestion $\rightarrow$ Automated Data Quality Audit $\rightarrow$ Interactive Wrangling $\rightarrow$ Machine Learning Preprocessing $\rightarrow$ Verified Clean Export $\rightarrow$ Visual Analytics.
- **UI Design Palette**:
  - Background: `#0B1020`
  - Sidebar: `#111A2E`
  - Cards: `#17233B`
  - Accent: `#6366F1`
  - Text: `#FFFFFF`
- **Authentication**: Dual-mode engine supporting **Supabase Cloud Authentication** (via OAuth/REST) with seamless offline fallback to **Local Academic Sandbox Mode** for offline grading and demonstration.

---

## 📁 Project Directory Structure

```text
campusflow/
│
├── app.py                                   # Master Streamlit Application & Dashboard
├── requirements.txt                         # Complete Python dependencies
├── README.md                                # Comprehensive documentation & guide
├── .env.example                             # Environment configuration template
│
├── data/
│   └── student_attendance_raw_500.csv       # Synthetic raw dataset (500 records with controlled quality anomalies)
│
└── utils/
    ├── __init__.py                          # Package initialization
    ├── authentication.py                    # Supabase Authentication & Local Academic Auth
    ├── file_loader.py                       # Ingestion engine for 13 file formats
    ├── data_cleaning.py                     # Missing values, duplicates, text fixes, domain repair
    ├── preprocessing.py                     # Encoding, Min-Max & Standard scaling, feature engineering
    ├── data_validation.py                   # 11-dimension automated data quality audit
    ├── visualizations.py                    # Plotly dark theme chart generators
    └── export_data.py                       # Cross-format export engine (CSV, XLSX, JSON, JSONL, Parquet)
```

---

## 🛠️ Complete Technology Stack

| Technology | Role |
|---|---|
| **Python 3.10+** | Core programming language |
| **Streamlit** | Modern, interactive web UI & state management |
| **Pandas & NumPy** | High-performance data manipulation, slicing, and vectorized transformations |
| **Plotly Express & Graph Objects** | Interactive charting with custom dark theme integration |
| **Scikit-learn** | Machine learning preprocessing: `LabelEncoder`, `MinMaxScaler`, `StandardScaler` |
| **Supabase** | Cloud authentication, user registration, and password recovery |
| **OpenPyXL & PyArrow** | Native Excel (`.xlsx`) and Apache Parquet columnar storage engines |
| **Python-Dotenv** | Secure credential and environment variable management |

---

## 📂 13 Verified Supported File Formats

CampusFlow implements actual parsers for both structured and compressed formats:

### Structured Formats:
1. **CSV** (`.csv`): Comma-Separated Values with automatic delimiter sniffing (`,` `\t` `;` `|`).
2. **TSV** (`.tsv`): Tab-Separated Values.
3. **XLSX** (`.xlsx`): Microsoft Excel OpenXML with multi-worksheet selection.
4. **XLS** (`.xls`): Legacy Microsoft Excel spreadsheets.
5. **JSON** (`.json`): Structured JavaScript Object Notation with automatic nested dictionary flattening (`pd.json_normalize`).
6. **JSONL** (`.jsonl`): JSON Lines format.
7. **NDJSON** (`.ndjson`): Newline Delimited JSON.
8. **XML** (`.xml`): Hierarchical Extensible Markup Language parsed into tabular DataFrames.
9. **TXT** (`.txt`): Text files with custom delimiter selection.
10. **DAT** (`.dat`): Generic data files with delimiter detection.
11. **Parquet** (`.parquet`): Fast, columnar Apache Parquet storage.

### Compressed Formats:
12. **CSV.GZ** (`.csv.gz`): Gzip-compressed CSV archives parsed directly in-memory.
13. **JSON.GZ** (`.json.gz`): Gzip-compressed JSON files parsed in-memory.

---

## 🖥️ System Modules & Features

### 1. 🔑 Login & Authentication
- Secure email/password authentication.
- User registration with role classification (*Student Analyst, Faculty Researcher, Department Head, External Auditor*).
- Password recovery and reset mechanisms.
- Show/hide password toggles.
- Protected dashboard routing (non-authenticated requests are halted).
- **Dual Mode**: Connects to live Supabase Cloud when `SUPABASE_URL` and `SUPABASE_KEY` are provided in `.env`; otherwise automatically operates in Local Academic Sandbox Mode with built-in credentials:
  - **Admin**: `admin@campusflow.edu` / `admin123`
  - **Evaluator**: `evaluator@college.edu` / `college2026`
  - **Student**: `student@campusflow.edu` / `student123`

### 2. 🏠 Executive Dashboard
- 8 Live Metric Cards: Uploaded Datasets, Total Records, Features, Missing Values, Duplicate Rows, Invalid Domain Values, Cleaned Records, and Data Quality Health Score.
- Interactive Plotly speed-gauge for overall dataset quality health index.
- Chronological audit history log tracking every applied transformation.

### 3. 🛡️ Data Quality Analysis Engine
Automatically identifies issues across 11 dimensions:
- Missing cells and null percentage per column.
- Duplicate rows and duplicate primary keys (`Student_ID`).
- Duplicate column pairs and empty columns (100% null).
- Negative numerical values in non-negative features.
- Domain mismatches ($\text{Present} > \text{Total\_Classes}$ or $\text{Total} \ne \text{Present} + \text{Absent}$).
- Text irregularities (leading/trailing whitespace, inconsistent department naming).
- Statistical outliers via Interquartile Range (IQR).

### 4. ⚙️ Interactive Data Wrangling
- **Preview before commit**: Users inspect the outcome before saving changes.
- **Missing Value Handling**: Mean imputation, Median imputation, Mode imputation, row dropping, column dropping, or custom constants.
- **Deduplication**: Removes duplicates across all columns or specific primary key subsets.
- **Text Standardization**: Trimming, casing conversion, and academic department normalizer (`AIML`, `CSE`, `ECE`, `EEE`, `IT`).
- **Data Type Casting**: Conversion to `int`, `float`, `str`, `category`, and `datetime`.
- **Filtering & Sorting**: Multi-condition filtering (`==`, `!=`, `contains`, `>`, `<`, `is_null`, etc.).
- **Outlier Treatment**: IQR clipping or row removal.
- **One-Click Academic Attendance Repair**: Automated non-negative enforcement, bounds checking, and recalculation of $\text{Absent} = \text{Total} - \text{Present}$.

### 5. 🔬 Machine Learning Preprocessing
- **Label Encoding**: Ordinal mapping via Scikit-learn `LabelEncoder`.
- **One-Hot Encoding**: Dummy variable generation with optional first-column drop.
- **Min-Max Scaling**: Normalizes numeric features to range $[0, 1]$ (automatically protects identifier columns like `Student_ID`).
- **Standard Scaling**: Z-score standardization ($\mu=0, \sigma=1$) with identifier protection.
- **Academic Feature Engineering**: Calculates $\text{Attendance\_Percentage}$, $\text{Attendance\_Status}$ (Cutoff 75%), $\text{Risk\_Category}$ (*Safe Zone, Moderate, Critical*), and $\text{Absent\_Ratio}$.
- **Mathematical Transforms**: Natural log ($\ln(1+x)$), square root ($\sqrt{x}$), and square ($x^2$).

### 6. ✨ Clean Dataset & Export Center (Main Showcase)
- Displays side-by-side **Before vs After Transformation Comparisons**.
- Displays full chronological transformation audit trail.
- Verified final clean dataset viewer.
- **Cross-Format Data Exporter**: Export the cleaned data into **CSV, XLSX, JSON, JSONL, or Parquet** at any time.

### 7. 📊 Exploratory Data Analysis
- Interactive filters by Department, Academic Year, and Eligibility Status.
- Statistical summary bar (Mean, Median, Defaulters count, Compliant count).
- Attendance Distribution Histogram with 75% cutoff indicator.
- Good vs Low attendance ratio donut chart.
- Department-wise performance comparison bar chart.
- Classes Present vs Absent correlation scatter plot.
- Academic Year-wise performance variance box plot.

---

## 📊 Sample Attendance Dataset Specification

- **File**: `data/student_attendance_raw_500.csv`
- **Records**: Exactly 500 fictional student records.
- **Columns**: `Student_ID, Student_Name, Department, Year, Total_Classes, Present, Absent`
- **Controlled Quality Anomalies Included for Demonstration**:
  - Missing values in `Student_Name`, `Present`, `Absent`, and `Total_Classes`.
  - Duplicate rows and duplicate student IDs.
  - Inconsistent department strings (`"aiml"`, `"AIML "`, `"C.S.E."`, `"cse"`, `"  ECE"`, `"eee "`, `"I.T."`).
  - Negative values (e.g. `Absent = -5`, `Present = -2`).
  - Attendance overflow (`Present = 95` with `Total_Classes = 80`).
  - Extra whitespace in student names (`"  Arjun Reddy   "`).

---

## 🚀 Visual Studio Code (VS Code) Setup Guide on Windows

Follow these steps to run CampusFlow in **Visual Studio Code** on Windows:

### Step 1: Open the Project in VS Code
1. Launch **Visual Studio Code**.
2. Click **File** $\rightarrow$ **Open Folder...** and select:
   ```text
   C:\Users\Student\farzana_dwp\campusflow
   ```

### Step 2: Open the Integrated Terminal
Press <kbd>Ctrl</kbd> + <kbd>`</kbd> (backtick) or navigate to **Terminal** $\rightarrow$ **New Terminal**.

### Step 3: Install Required Dependencies
Run:
```powershell
pip install -r requirements.txt
```

### Step 4: (Optional) Configure Supabase Credentials
To enable live Supabase Cloud authentication, you can configure `.streamlit/secrets.toml` or `.env`:

#### Option A: Using `.streamlit/secrets.toml` (Recommended)
Copy the provided template `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`:
```powershell
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Open `.streamlit/secrets.toml` and fill in your Supabase credentials:
```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your-actual-anon-public-key"
```

#### Option B: Using `.env`
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Open `.env` and fill in your keys:
```ini
# .env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-actual-anon-public-key
```

*(If neither file is provided, CampusFlow handles missing credentials gracefully with zero crashes and provides an explicit **Local Academic Demo Mode** for offline review).*

### Step 5: Launch the Application
Run the Streamlit server:
```powershell
streamlit run app.py
```

### Step 6: View in Browser
The dashboard will open automatically at:
```text
http://localhost:8501
```
To evaluate without registering, click the **"Fill Admin"** or **"Fill Evaluator"** quick button on the login screen.

---

## 💡 Troubleshooting & FAQ

- **PowerShell Execution Policy Error**:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Port Conflict**: If port 8501 is busy, run:
  ```powershell
  streamlit run app.py --server.port 8505
  ```
- **ModuleNotFoundError**: Ensure your terminal working directory is inside `campusflow`:
  ```powershell
  cd campusflow
  streamlit run app.py
  ```

---

## 🎓 Academic Submission Details
- **Project Title**: CampusFlow – Multi-Format Data Wrangling and Preprocessing System
- **Subject**: Data Wrangling and Preprocessing (DWP)
- **Primary Technologies**: Python, Streamlit, Pandas, NumPy, Plotly, Scikit-learn, Supabase
- **Target OS**: Windows 10/11 & Visual Studio Code
