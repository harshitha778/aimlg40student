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
                html.H1("Course Analysis", className="page-title"),
                html.P("Popularity, GPA performance, and credit load across all courses.", className="page-sub"),
            ], className="page-header"),

            html.Div([
                html.Div([
                    html.Label("Department", className="filter-label"),
                    dcc.Dropdown(dept_options, value="All", id="ca-dept", clearable=False, className="filter-drop"),
                ], className="filter-item"),
            ], className="filter-bar"),

            html.Div([
                html.Div([
                    html.H3("Top 15 Most Popular Courses", className="chart-title"),
                    dcc.Graph(id="ca-top-courses", config={"displayModeBar": False}, style={"height": "380px"}),
                ], className="chart-card wide"),
                html.Div([
                    html.H3("Credits Distribution", className="chart-title"),
                    dcc.Graph(id="ca-credits", config={"displayModeBar": False}, style={"height": "380px"}),
                ], className="chart-card"),
            ], className="chart-row"),

            html.Div([
                html.Div([
                    html.H3("Avg GPA per Course (Top 15)", className="chart-title"),
                    dcc.Graph(id="ca-gpa-course", config={"displayModeBar": False}, style={"height": "340px"}),
                ], className="chart-card"),
                html.Div([
                    html.H3("Enrollment Status by Department", className="chart-title"),
                    dcc.Graph(id="ca-status-dept", config={"displayModeBar": False}, style={"height": "340px"}),
                ], className="chart-card wide"),
            ], className="chart-row"),
        ],
        className="page-body",
    )


def register_callbacks(app):
    @app.callback(
        Output("ca-top-courses",  "figure"),
        Output("ca-credits",      "figure"),
        Output("ca-gpa-course",   "figure"),
        Output("ca-status-dept",  "figure"),
        Input("ca-dept", "value"),
    )
    def update(dept):
        filtered = df.copy()
        if dept != "All":
            filtered = filtered[filtered.department == dept]

        # Top 15 courses
        top = filtered.course.value_counts().head(15).reset_index()
        top.columns = ["course", "count"]
        top = top.sort_values("count")
        fig1 = px.bar(top, x="count", y="course", orientation="h",
                      color="count", color_continuous_scale=["#C7D2FE", ACCENT],
                      template="plotly_white")
        fig1.update_layout(**_bl(), xaxis_title="Enrollments", yaxis_title="", coloraxis_showscale=False)

        # Credits pie
        cc = filtered.credits.value_counts().reset_index()
        cc.columns = ["credits", "count"]
        fig2 = px.pie(cc, names="credits", values="count", hole=0.5,
                      color_discrete_sequence=[ACCENT, SUCCESS, WARNING, DANGER, "#A78BFA"],
                      template="plotly_white")
        fig2.update_traces(textposition="outside", textinfo="percent+label")
        fig2.update_layout(**_bl(), showlegend=False)
        fig2.update_layout(annotations=[dict(text="Credits", x=0.5, y=0.5, font_size=14, showarrow=False)])

        # GPA per course (top 15 by count)
        top_names = filtered.course.value_counts().head(15).index
        gpa_c = (
            filtered[filtered.course.isin(top_names)]
            .groupby("course")["gpa"]
            .mean()
            .reset_index()
            .sort_values("gpa", ascending=True)
        )
        fig3 = px.bar(gpa_c, x="gpa", y="course", orientation="h",
                      color="gpa", color_continuous_scale=["#FEF3C7", WARNING, SUCCESS],
                      range_color=[2.5, 4.0], template="plotly_white")
        fig3.update_layout(**_bl(), xaxis_title="Avg GPA", yaxis_title="", coloraxis_showscale=False)

        # Status stacked bar by department
        sd = (
            filtered.groupby(["department", "enrollment_status"])
            .size()
            .reset_index(name="count")
        )
        cmap = {"Enrolled": ACCENT, "Completed": SUCCESS, "Waitlisted": WARNING, "Dropped": DANGER}
        fig4 = px.bar(sd, x="department", y="count", color="enrollment_status",
                      color_discrete_map=cmap, barmode="stack", template="plotly_white")
        fig4.update_layout(**_bl(), xaxis_title="", yaxis_title="Students",
                           xaxis_tickangle=-30, legend=dict(orientation="h", y=1.06))

        return fig1, fig2, fig3, fig4


def _bl():
    return dict(
        margin=dict(l=10, r=10, t=10, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1E293B"),
    )