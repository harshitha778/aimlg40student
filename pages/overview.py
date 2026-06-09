import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc

df: pd.DataFrame = pd.DataFrame()   # injected by app.py

ACCENT   = "#4F6EF7"
SUCCESS  = "#22C55E"
WARNING  = "#F59E0B"
DANGER   = "#EF4444"
MUTED    = "#64748B"


def kpi_card(label, value, sub="", color=ACCENT):
    return html.Div(
        [
            html.Div(value, className="kpi-value", style={"color": color}),
            html.Div(label, className="kpi-label"),
            html.Div(sub,   className="kpi-sub") if sub else None,
        ],
        className="kpi-card",
    )


def layout():
    total       = len(df)
    enrolled    = len(df[df.enrollment_status == "Enrolled"])
    avg_gpa     = df.gpa.mean()
    departments = df.department.nunique()
    courses     = df.course.nunique()
    dropped_pct = round(len(df[df.enrollment_status == "Dropped"]) / total * 100, 1)

    # Department distribution
    dept_counts = df.groupby("department").size().reset_index(name="count").sort_values("count")
    fig_dept = px.bar(
        dept_counts, x="count", y="department", orientation="h",
        color="count", color_continuous_scale=["#C7D2FE", ACCENT],
        template="plotly_white",
    )
    fig_dept.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
        xaxis_title="Students",
        yaxis_title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1E293B"),
    )

    # Status donut
    status_counts = df.enrollment_status.value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    color_map = {"Enrolled": ACCENT, "Completed": SUCCESS, "Waitlisted": WARNING, "Dropped": DANGER}
    fig_status = px.pie(
        status_counts, names="status", values="count",
        hole=0.6, color="status", color_discrete_map=color_map,
        template="plotly_white",
    )
    fig_status.update_traces(textposition="outside", textinfo="percent+label")
    fig_status.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1E293B"),
    )

    # Gender split
    gender_counts = df.gender.value_counts().reset_index()
    gender_counts.columns = ["gender", "count"]
    fig_gender = px.pie(
        gender_counts, names="gender", values="count", hole=0.5,
        color_discrete_sequence=[ACCENT, "#A78BFA", WARNING, MUTED],
        template="plotly_white",
    )
    fig_gender.update_traces(textposition="outside", textinfo="percent+label")
    fig_gender.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1E293B"),
    )

    # GPA distribution
    fig_gpa = px.histogram(
        df, x="gpa", nbins=30, color_discrete_sequence=[ACCENT],
        template="plotly_white",
    )
    fig_gpa.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="GPA",
        yaxis_title="Students",
        bargap=0.05,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1E293B"),
    )

    return html.Div(
        [
            html.Div([
                html.H1("Dashboard Overview", className="page-title"),
                html.P("Snapshot of all enrollment activity across semesters and departments.", className="page-sub"),
            ], className="page-header"),

            # KPI row
            html.Div([
                kpi_card("Total Students",  f"{total:,}"),
                kpi_card("Currently Enrolled", f"{enrolled:,}", color=SUCCESS),
                kpi_card("Average GPA",     f"{avg_gpa:.2f}", color=WARNING),
                kpi_card("Departments",     str(departments)),
                kpi_card("Unique Courses",  str(courses)),
                kpi_card("Drop Rate",       f"{dropped_pct}%", color=DANGER),
            ], className="kpi-row"),

            # Charts row 1
            html.Div([
                html.Div([
                    html.H3("Students by Department", className="chart-title"),
                    dcc.Graph(figure=fig_dept, config={"displayModeBar": False}, style={"height": "320px"}),
                ], className="chart-card wide"),
                html.Div([
                    html.H3("Enrollment Status", className="chart-title"),
                    dcc.Graph(figure=fig_status, config={"displayModeBar": False}, style={"height": "320px"}),
                ], className="chart-card"),
            ], className="chart-row"),

            # Charts row 2
            html.Div([
                html.Div([
                    html.H3("GPA Distribution", className="chart-title"),
                    dcc.Graph(figure=fig_gpa, config={"displayModeBar": False}, style={"height": "280px"}),
                ], className="chart-card wide"),
                html.Div([
                    html.H3("Gender Split", className="chart-title"),
                    dcc.Graph(figure=fig_gender, config={"displayModeBar": False}, style={"height": "280px"}),
                ], className="chart-card"),
            ], className="chart-row"),
        ],
        className="page-body",
    )
