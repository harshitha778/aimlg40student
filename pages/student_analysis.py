import pandas as pd
import plotly.express as px
from dash import html, dcc, Input, Output, callback

df: pd.DataFrame = pd.DataFrame()

ACCENT  = "#4F6EF7"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER  = "#EF4444"


def layout():
    dept_options = [{"label": "All Departments", "value": "All"}] + [
        {"label": d, "value": d} for d in sorted(df.department.unique())
    ]
    year_options = [{"label": "All Years", "value": "All"}] + [
        {"label": y, "value": y} for y in ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
    ]

    return html.Div(
        [
            html.Div([
                html.H1("Student Analysis", className="page-title"),
                html.P("Explore demographic and academic performance patterns across the student body.", className="page-sub"),
            ], className="page-header"),

            # Filters
            html.Div([
                html.Div([
                    html.Label("Department", className="filter-label"),
                    dcc.Dropdown(dept_options, value="All", id="sa-dept", clearable=False, className="filter-drop"),
                ], className="filter-item"),
                html.Div([
                    html.Label("Year", className="filter-label"),
                    dcc.Dropdown(year_options, value="All", id="sa-year", clearable=False, className="filter-drop"),
                ], className="filter-item"),
            ], className="filter-bar"),

            # Charts
            html.Div([
                html.Div([
                    html.H3("GPA by Department", className="chart-title"),
                    dcc.Graph(id="sa-gpa-dept", config={"displayModeBar": False}, style={"height": "320px"}),
                ], className="chart-card wide"),
                html.Div([
                    html.H3("Age Distribution", className="chart-title"),
                    dcc.Graph(id="sa-age-hist", config={"displayModeBar": False}, style={"height": "320px"}),
                ], className="chart-card"),
            ], className="chart-row"),

            html.Div([
                html.Div([
                    html.H3("GPA vs Age (by Gender)", className="chart-title"),
                    dcc.Graph(id="sa-scatter", config={"displayModeBar": False}, style={"height": "320px"}),
                ], className="chart-card wide"),
                html.Div([
                    html.H3("Students by Year", className="chart-title"),
                    dcc.Graph(id="sa-year-bar", config={"displayModeBar": False}, style={"height": "320px"}),
                ], className="chart-card"),
            ], className="chart-row"),
        ],
        className="page-body",
    )


def register_callbacks(app):
    @app.callback(
        Output("sa-gpa-dept",  "figure"),
        Output("sa-age-hist",  "figure"),
        Output("sa-scatter",   "figure"),
        Output("sa-year-bar",  "figure"),
        Input("sa-dept", "value"),
        Input("sa-year", "value"),
    )
    def update(dept, year):
        filtered = df.copy()
        if dept != "All":
            filtered = filtered[filtered.department == dept]
        if year != "All":
            filtered = filtered[filtered.year == year]

        # GPA box by department
        fig1 = px.box(
            filtered, x="department", y="gpa", color="department",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_white",
        )
        fig1.update_layout(**_base_layout(), xaxis_tickangle=-30, xaxis_title="", yaxis_title="GPA", showlegend=False)

        # Age histogram
        fig2 = px.histogram(filtered, x="age", nbins=20, color_discrete_sequence=[ACCENT], template="plotly_white")
        fig2.update_layout(**_base_layout(), xaxis_title="Age", yaxis_title="Students", bargap=0.05)

        # Scatter GPA vs Age
        fig3 = px.scatter(
            filtered.sample(min(len(filtered), 500), random_state=1),
            x="age", y="gpa", color="gender",
            color_discrete_sequence=[ACCENT, "#A78BFA", WARNING, "#94A3B8"],
            opacity=0.65, template="plotly_white",
        )
        fig3.update_layout(**_base_layout(), xaxis_title="Age", yaxis_title="GPA")

        # Year bar
        year_order = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
        yc = filtered.year.value_counts().reindex(year_order, fill_value=0).reset_index()
        yc.columns = ["year", "count"]
        fig4 = px.bar(yc, x="year", y="count", color="count", color_continuous_scale=["#C7D2FE", ACCENT], template="plotly_white")
        fig4.update_layout(**_base_layout(), xaxis_title="", yaxis_title="Students", coloraxis_showscale=False)

        return fig1, fig2, fig3, fig4


def _base_layout():
    return dict(
        margin=dict(l=10, r=10, t=10, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1E293B"),
    )