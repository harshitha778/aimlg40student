import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, Input, Output

df: pd.DataFrame = pd.DataFrame()

ACCENT  = "#4F6EF7"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER  = "#EF4444"


def layout():
    dept_options = [{"label": "All Departments", "value": "All"}] + [
        {"label": d, "value": d} for d in sorted(df.department.unique())
    ]

    return html.Div(
        [
            html.Div([
                html.H1("Trend Analysis", className="page-title"),
                html.P("How enrollment numbers, GPA, and demographics have shifted over time.", className="page-sub"),
            ], className="page-header"),

            html.Div([
                html.Div([
                    html.Label("Department", className="filter-label"),
                    dcc.Dropdown(dept_options, value="All", id="ta-dept", clearable=False, className="filter-drop"),
                ], className="filter-item"),
            ], className="filter-bar"),

            html.Div([
                html.Div([
                    html.H3("Monthly Enrollment Trend", className="chart-title"),
                    dcc.Graph(id="ta-monthly", config={"displayModeBar": False}, style={"height": "280px"}),
                ], className="chart-card", style={"flex": "1 1 100%"}),
            ], className="chart-row"),

            html.Div([
                html.Div([
                    html.H3("Avg GPA per Semester", className="chart-title"),
                    dcc.Graph(id="ta-gpa-sem", config={"displayModeBar": False}, style={"height": "280px"}),
                ], className="chart-card wide"),
                html.Div([
                    html.H3("Drop Rate per Semester", className="chart-title"),
                    dcc.Graph(id="ta-drop-sem", config={"displayModeBar": False}, style={"height": "280px"}),
                ], className="chart-card"),
            ], className="chart-row"),

            html.Div([
                html.Div([
                    html.H3("Enrollment by Department per Semester", className="chart-title"),
                    dcc.Graph(id="ta-dept-line", config={"displayModeBar": False}, style={"height": "340px"}),
                ], className="chart-card", style={"flex": "1 1 100%"}),
            ], className="chart-row"),
        ],
        className="page-body",
    )


def register_callbacks(app):
    @app.callback(
        Output("ta-monthly",  "figure"),
        Output("ta-gpa-sem",  "figure"),
        Output("ta-drop-sem", "figure"),
        Output("ta-dept-line","figure"),
        Input("ta-dept", "value"),
    )
    def update(dept):
        filtered = df.copy()
        if dept != "All":
            filtered = filtered[filtered.department == dept]

        # Monthly trend
        tl = filtered.copy()
        tl["month"] = tl.enrollment_date.dt.to_period("M").astype(str)
        tl_g = tl.groupby("month").size().reset_index(name="count").sort_values("month")
        fig1 = px.line(tl_g, x="month", y="count", markers=True,
                       color_discrete_sequence=[ACCENT], template="plotly_white")
        fig1.update_traces(line_width=2.5)
        fig1.update_layout(**_bl(), xaxis_title="", yaxis_title="New Enrollments", xaxis_tickangle=-45)

        # GPA per semester
        sem_order = ["Spring 2023", "Fall 2023", "Spring 2024", "Fall 2024", "Spring 2025"]
        gpa_s = (
            filtered.groupby("semester")["gpa"]
            .mean()
            .reindex(sem_order)
            .reset_index()
        )
        gpa_s.columns = ["semester", "avg_gpa"]
        fig2 = px.line(gpa_s, x="semester", y="avg_gpa", markers=True,
                       color_discrete_sequence=[SUCCESS], template="plotly_white")
        fig2.update_traces(line_width=2.5)
        fig2.update_layout(**_bl(), xaxis_title="", yaxis_title="Avg GPA",
                           yaxis=dict(range=[2.8, 3.5]))

        # Drop rate per semester
        drop = (
            filtered.groupby("semester")
            .apply(lambda x: (x.enrollment_status == "Dropped").mean() * 100)
            .reindex(sem_order)
            .reset_index()
        )
        drop.columns = ["semester", "drop_rate"]
        fig3 = px.bar(drop, x="semester", y="drop_rate",
                      color="drop_rate", color_continuous_scale=["#FEF3C7", DANGER],
                      template="plotly_white")
        fig3.update_layout(**_bl(), xaxis_title="", yaxis_title="Drop Rate (%)",
                           coloraxis_showscale=False)

        # Dept line over semesters
        dept_trend = (
            df.groupby(["semester", "department"])
            .size()
            .reset_index(name="count")
        )
        dept_trend["semester"] = pd.Categorical(dept_trend["semester"], categories=sem_order, ordered=True)
        dept_trend = dept_trend.sort_values("semester")
        fig4 = px.line(dept_trend, x="semester", y="count", color="department",
                       markers=True, template="plotly_white",
                       color_discrete_sequence=px.colors.qualitative.Safe)
        fig4.update_traces(line_width=2)
        fig4.update_layout(**_bl(), xaxis_title="", yaxis_title="Students",
                           legend=dict(orientation="h", y=-0.22))

        return fig1, fig2, fig3, fig4


def _bl():
    return dict(
        margin=dict(l=10, r=10, t=10, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1E293B"),
    )