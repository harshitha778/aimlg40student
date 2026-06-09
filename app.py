import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd

# ── App init ──────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    use_pages=False,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Student Enrollment Analytics"
server = app.server

# ── Load data once ────────────────────────────────────────────────────────────
df = pd.read_csv("data/enrollment_data.csv", parse_dates=["enrollment_date"])
# Expose df for page imports
import pages.overview         as pg_overview
import pages.student_analysis  as pg_student
import pages.enrollment_analysis as pg_enroll
import pages.course_analysis   as pg_course
import pages.trend_analysis    as pg_trend

for mod in [pg_overview, pg_student, pg_enroll, pg_course, pg_trend]:
    mod.df = df

# ── Sidebar nav ───────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("overview",    "📊", "Overview"),
    ("student",     "🎓", "Student Analysis"),
    ("enrollment",  "📋", "Enrollment Analysis"),
    ("course",      "📚", "Course Analysis"),
    ("trend",       "📈", "Trend Analysis"),
]

def sidebar():
    links = []
    for page_id, icon, label in NAV_ITEMS:
        links.append(
            html.A(
                [html.Span(icon, className="nav-icon"), label],
                id=f"nav-{page_id}",
                href=f"#{page_id}",
                className="nav-link",
                n_clicks=0,
            )
        )
    return html.Div(
        [
            html.Div(
                [
                    html.Div("SEA", className="brand-abbr"),
                    html.Div(
                        [
                            html.Span("Student", className="brand-word"),
                            html.Span("Enrollment Analytics", className="brand-sub"),
                        ],
                        className="brand-text",
                    ),
                ],
                className="sidebar-brand",
            ),
            html.Nav(links, className="sidebar-nav"),
        ],
        className="sidebar",
        id="sidebar",
    )


# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dcc.Store(id="active-page", data="overview"),
        sidebar(),
        html.Div(id="page-content", className="main-content"),
    ],
    className="app-shell",
)


# ── Page routing ──────────────────────────────────────────────────────────────
@app.callback(
    Output("page-content", "children"),
    Output("active-page", "data"),
    [Input(f"nav-{pid}", "n_clicks") for pid, *_ in NAV_ITEMS],
    Input("url", "pathname"),
    prevent_initial_call=False,
)
def route(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return pg_overview.layout(), "overview"

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    page_map = {f"nav-{pid}": pid for pid, *_ in NAV_ITEMS}

    page = page_map.get(trigger, "overview")

    layouts = {
        "overview":   pg_overview.layout,
        "student":    pg_student.layout,
        "enrollment": pg_enroll.layout,
        "course":     pg_course.layout,
        "trend":      pg_trend.layout,
    }
    return layouts[page](), page


# ── Highlight active nav link ─────────────────────────────────────────────────
@app.callback(
    [Output(f"nav-{pid}", "className") for pid, *_ in NAV_ITEMS],
    Input("active-page", "data"),
)
def highlight_nav(active):
    return ["nav-link active" if pid == active else "nav-link" for pid, *_ in NAV_ITEMS]


# Register page-level callbacks
pg_student.register_callbacks(app)
pg_enroll.register_callbacks(app)
pg_course.register_callbacks(app)
pg_trend.register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8050)
