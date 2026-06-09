import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, dash_table

df: pd.DataFrame = pd.DataFrame()

ACCENT  = "#4F6EF7"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER  = "#EF4444"


def layout():
    semester_options = [{"label": "All Semesters", "value": "All"}] + [
        {"label": s, "value": s} for s in sorted(df.semester.unique())
    ]
    status_options = [{"label": "All Statuses", "value": "All"}] + [
        {"label": s, "value": s} for s in df.enrollment_status.unique()
    ]

    return html.Div(
        [
            html.Div([
                html.H1("Enrollment Analysis", className="page-title"),
                html.P("Semester-by-semester enrollment trends, status breakdown, and fee summary.", className="page-sub"),
            ], className="page-header"),

            html.Div([
                html.Div([
                    html.Label("Semester", className="filter-label"),
                    dcc.Dropdown(semester_options, value="All", id="ea-sem", clearable=False, className="filter-drop"),
                ], className="filter-item"),
                html.Div([
                    html.Label("Status", className="filter-label"),
                    dcc.Dropdown(status_options, value="All", id="ea-status", clearable=False, className="filter-drop"),
                ], className="filter-item"),
            ], className="filter-bar"),

            html.Div([
                html.Div([
                    html.H3("Enrollments per Semester", className="chart-title"),
                    dcc.Graph(id="ea-sem-bar", config={"displayModeBar": False}, style={"height": "300px"}),
                ], className="chart-card wide"),
                html.Div([
                    html.H3("Status Breakdown", className="chart-title"),
                    dcc.Graph(id="ea-status-pie", config={"displayModeBar": False}, style={"height": "300px"}),
                ], className="chart-card"),
            ], className="chart-row"),

            html.Div([
                html.Div([
                    html.H3("Tuition vs Scholarship by Department", className="chart-title"),
                    dcc.Graph(id="ea-fee-bar", config={"displayModeBar": False}, style={"height": "300px"}),
                ], className="chart-card"),
                html.Div([
                    html.H3("Enrollment Timeline", className="chart-title"),
                    dcc.Graph(id="ea-timeline", config={"displayModeBar": False}, style={"height": "300px"}),
                ], className="chart-card wide"),
            ], className="chart-row"),

            html.Div([
                html.H3("Department Summary Table", className="chart-title"),
                html.Div(id="ea-table"),
            ], className="chart-card", style={"marginTop": "16px"}),
        ],
        className="page-body",
    )


def register_callbacks(app):
    @app.callback(
        Output("ea-sem-bar",   "figure"),
        Output("ea-status-pie","figure"),
        Output("ea-fee-bar",   "figure"),
        Output("ea-timeline",  "figure"),
        Output("ea-table",     "children"),
        Input("ea-sem",    "value"),
        Input("ea-status", "value"),
    )
    def update(sem, status):
        filtered = df.copy()
        if sem    != "All": filtered = filtered[filtered.semester == sem]
        if status != "All": filtered = filtered[filtered.enrollment_status == status]

        # Semester bar
        sem_order = ["Spring 2023", "Fall 2023", "Spring 2024", "Fall 2024", "Spring 2025"]
        sc = df.semester.value_counts().reindex(sem_order, fill_value=0).reset_index()
        sc.columns = ["semester", "count"]
        fig1 = px.bar(sc, x="semester", y="count", color="count",
                      color_continuous_scale=["#C7D2FE", ACCENT], template="plotly_white")
        fig1.update_layout(**_bl(), xaxis_title="", yaxis_title="Students", coloraxis_showscale=False)

        # Status pie
        sc2 = filtered.enrollment_status.value_counts().reset_index()
        sc2.columns = ["status", "count"]
        cmap = {"Enrolled": ACCENT, "Completed": SUCCESS, "Waitlisted": WARNING, "Dropped": DANGER}
        fig2 = px.pie(sc2, names="status", values="count", hole=0.55,
                      color="status", color_discrete_map=cmap, template="plotly_white")
        fig2.update_traces(textposition="outside", textinfo="percent+label")
        fig2.update_layout(**_bl(), showlegend=False)

        # Fee grouped bar
        fee = (
            filtered.groupby("department")
            .agg(tuition=("tuition_fee", "mean"), scholarship=("scholarship_amount", "mean"))
            .reset_index()
            .sort_values("tuition", ascending=False)
        )
        fig3 = go.Figure([
            go.Bar(name="Avg Tuition",     x=fee.department, y=fee.tuition,     marker_color=ACCENT,   opacity=0.85),
            go.Bar(name="Avg Scholarship", x=fee.department, y=fee.scholarship, marker_color=SUCCESS, opacity=0.85),
        ])
        fig3.update_layout(**_bl(), barmode="group", xaxis_tickangle=-30, yaxis_title="USD ($)",
                           legend=dict(orientation="h", y=1.08))

        # Timeline
        tl = filtered.copy()
        tl["month"] = tl.enrollment_date.dt.to_period("M").astype(str)
        tl_g = tl.groupby("month").size().reset_index(name="count")
        tl_g = tl_g.sort_values("month")
        fig4 = px.area(tl_g, x="month", y="count", color_discrete_sequence=[ACCENT], template="plotly_white")
        fig4.update_traces(fill="tozeroy", fillcolor="rgba(79,110,247,0.15)")
        fig4.update_layout(**_bl(), xaxis_title="", yaxis_title="Enrollments", xaxis_tickangle=-30)

        # Summary table
        summary = (
            filtered.groupby("department")
            .agg(
                Students=("student_id", "count"),
                Avg_GPA=("gpa", lambda x: round(x.mean(), 2)),
                Avg_Tuition=("tuition_fee", lambda x: f"${x.mean():,.0f}"),
                Avg_Scholarship=("scholarship_amount", lambda x: f"${x.mean():,.0f}"),
            )
            .reset_index()
            .rename(columns={"department": "Department"})
        )
        table = dash_table.DataTable(
            data=summary.to_dict("records"),
            columns=[{"name": c, "id": c} for c in summary.columns],
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#F1F5F9", "fontWeight": "600", "color": "#1E293B", "border": "none"},
            style_cell={"fontFamily": "Inter, sans-serif", "fontSize": "13px",
                        "padding": "10px 14px", "border": "1px solid #E2E8F0", "color": "#334155"},
            style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#F8FAFC"}],
            page_size=8,
        )
        return fig1, fig2, fig3, fig4, table


def _bl():
    return dict(
        margin=dict(l=10, r=10, t=10, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1E293B"),
    )
