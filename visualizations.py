"""
=============================================================================
CampusFlow – Interactive Visualizations Module
Plotly chart generators matching the premium dark theme (#0B1020, #17233B, #6366F1)
=============================================================================
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


# Palette constants
BG_COLOR = "#0B1020"
CARD_BG = "#17233B"
ACCENT_COLOR = "#6366F1"
TEXT_COLOR = "#FFFFFF"
MUTED_TEXT = "#94A3B8"
GRID_COLOR = "#2A3B5C"
SUCCESS_COLOR = "#10B981"
DANGER_COLOR = "#F43F5E"
WARNING_COLOR = "#F59E0B"
CYAN_COLOR = "#38BDF8"


def apply_theme(fig, height=380, title=None):
    """Applies CampusFlow dark styling to a Plotly figure."""
    fig.update_layout(
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT_COLOR, family="Segoe UI, sans-serif"),
        height=height,
        margin=dict(l=40, r=40, t=50 if title else 30, b=40),
        title=dict(text=title, font=dict(size=14, color=CYAN_COLOR)) if title else None,
        legend=dict(
            bgcolor="rgba(11, 16, 32, 0.7)",
            bordercolor=GRID_COLOR,
            borderwidth=1,
            font=dict(color=TEXT_COLOR)
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=MUTED_TEXT)
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(color=MUTED_TEXT)
        )
    )
    return fig


def plot_quality_gauge(score):
    """Generates an executive speed-gauge for the Data Quality Health Score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        delta={'reference': 85.0, 'increasing': {'color': SUCCESS_COLOR}, 'decreasing': {'color': DANGER_COLOR}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': MUTED_TEXT},
            'bar': {'color': ACCENT_COLOR, 'thickness': 0.28},
            'bgcolor': "#111A2E",
            'borderwidth': 1,
            'bordercolor': GRID_COLOR,
            'steps': [
                {'range': [0, 60], 'color': 'rgba(244, 63, 94, 0.35)'},
                {'range': [60, 80], 'color': 'rgba(245, 158, 11, 0.35)'},
                {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.35)'}
            ],
            'threshold': {
                'line': {'color': "#FFFFFF", 'width': 3},
                'thickness': 0.75,
                'value': 90.0
            }
        },
        number={'suffix': "%", 'font': {'color': TEXT_COLOR, 'size': 32}}
    ))
    return apply_theme(fig, height=260)


def plot_missing_values(cols_with_nulls, total_rows):
    """Plots a horizontal bar chart of columns containing missing values."""
    if not cols_with_nulls:
        fig = go.Figure()
        fig.add_annotation(
            text="✅ 100% Complete – Zero Missing Values Found!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=15, color=SUCCESS_COLOR)
        )
        return apply_theme(fig, height=220)

    df_missing = pd.DataFrame([
        {"Column": k, "Missing Count": v, "Percentage": round((v / total_rows) * 100, 2)}
        for k, v in cols_with_nulls.items()
    ]).sort_values(by="Missing Count", ascending=True)

    fig = px.bar(
        df_missing,
        x="Missing Count",
        y="Column",
        orientation="h",
        text="Missing Count",
        color="Percentage",
        color_continuous_scale=[(0.0, WARNING_COLOR), (1.0, DANGER_COLOR)],
        labels={"Missing Count": "Total Missing Cells", "Column": "Feature"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(coloraxis_showscale=False)
    return apply_theme(fig, height=max(220, len(cols_with_nulls) * 35))


def plot_attendance_distribution(df):
    """Plots attendance percentage histogram with 75% cutoff indicator."""
    if "Attendance_Percentage" not in df.columns:
        return None

    color_col = "Attendance_Status" if "Attendance_Status" in df.columns else None
    color_map = {"Good (>=75%)": CYAN_COLOR, "Low (<75%)": DANGER_COLOR}

    fig = px.histogram(
        df,
        x="Attendance_Percentage",
        nbins=25,
        color=color_col,
        color_discrete_map=color_map,
        opacity=0.85,
        labels={"Attendance_Percentage": "Attendance Percentage (%)", "count": "Student Count"}
    )
    fig.add_vline(
        x=75.0,
        line_dash="dash",
        line_color=DANGER_COLOR,
        line_width=2.5,
        annotation_text="75% Mandatory Cutoff",
        annotation_position="top left",
        annotation_font=dict(color=DANGER_COLOR, size=11)
    )
    fig.update_layout(bargap=0.08)
    return apply_theme(fig, height=380, title="Attendance Distribution & Eligibility Threshold")


def plot_department_attendance(df):
    """Plots department-wise average attendance bar chart."""
    if "Department" not in df.columns or "Attendance_Percentage" not in df.columns:
        return None

    dept_stats = df.groupby("Department")["Attendance_Percentage"].agg(
        Average_Attendance="mean",
        Student_Count="count"
    ).reset_index().round(2).sort_values(by="Average_Attendance", ascending=False)

    fig = px.bar(
        dept_stats,
        x="Department",
        y="Average_Attendance",
        text="Average_Attendance",
        color="Average_Attendance",
        color_continuous_scale=[(0.0, DANGER_COLOR), (0.5, WARNING_COLOR), (1.0, CYAN_COLOR)],
        labels={"Average_Attendance": "Average Attendance (%)", "Department": "Academic Department"}
    )
    fig.add_hline(
        y=75.0,
        line_dash="dot",
        line_color=DANGER_COLOR,
        annotation_text="75% Eligibility Cutoff",
        annotation_position="bottom right"
    )
    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        marker_line_color=GRID_COLOR,
        marker_line_width=1.5
    )
    fig.update_layout(yaxis_range=[0, 105], coloraxis_showscale=False)
    return apply_theme(fig, height=380, title="Department-wise Attendance Performance")


def plot_attendance_donut(df):
    """Plots good vs low attendance donut chart."""
    if "Attendance_Status" not in df.columns:
        return None

    status_counts = df["Attendance_Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    fig = px.pie(
        status_counts,
        values="Count",
        names="Status",
        hole=0.55,
        color="Status",
        color_discrete_map={"Good (>=75%)": CYAN_COLOR, "Low (<75%)": DANGER_COLOR}
    )
    fig.update_traces(
        textinfo="percent+label",
        textfont=dict(size=12, color=TEXT_COLOR),
        marker=dict(line=dict(color=CARD_BG, width=2))
    )
    return apply_theme(fig, height=360, title="Institutional Eligibility Ratio (Good vs Low)")


def plot_present_vs_absent_scatter(df):
    """Plots classes present vs absent scatter plot."""
    if "Present" not in df.columns or "Absent" not in df.columns:
        return None

    color_col = "Attendance_Status" if "Attendance_Status" in df.columns else ("Department" if "Department" in df.columns else None)
    hover_cols = [c for c in ["Student_ID", "Student_Name", "Department", "Year", "Attendance_Percentage"] if c in df.columns]

    fig = px.scatter(
        df,
        x="Present",
        y="Absent",
        color=color_col,
        hover_name="Student_Name" if "Student_Name" in df.columns else None,
        hover_data=hover_cols,
        labels={"Present": "Classes Present", "Absent": "Classes Absent"},
        color_discrete_sequence=[CYAN_COLOR, DANGER_COLOR, WARNING_COLOR, SUCCESS_COLOR, ACCENT_COLOR]
    )
    return apply_theme(fig, height=400, title="Correlation: Classes Present vs. Classes Absent")


def plot_year_comparison(df):
    """Plots year-wise attendance comparison."""
    if "Year" not in df.columns or "Attendance_Percentage" not in df.columns:
        return None

    fig = px.box(
        df,
        x="Year",
        y="Attendance_Percentage",
        color="Year",
        color_discrete_sequence=[CYAN_COLOR, ACCENT_COLOR, SUCCESS_COLOR, WARNING_COLOR],
        labels={"Year": "Academic Year", "Attendance_Percentage": "Attendance (%)"}
    )
    fig.add_hline(y=75.0, line_dash="dash", line_color=DANGER_COLOR)
    fig.update_layout(showlegend=False)
    return apply_theme(fig, height=380, title="Year-wise Attendance Variance & Spread")
