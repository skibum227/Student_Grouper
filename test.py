import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html


# 2. Create a Dash app instance
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": '8rem 2rem',
   # "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 0rem",
}

##### this is me trying to recreate it
teacher_name = 'Mrs. Herr'
period_name = 'Period 2'

# https://dash.plotly.com/dash-core-components/location
# This is only for the side bar
sidebar = html.Div([#dcc.Location(id="url"),
    dbc.Row(
            dbc.Col(
                    html.H2(teacher_name, className="display-4"),
                    width={'size': 6, 'offset': 0}
                )
        ),
    dbc.Row(
            dbc.Col(
                    html.Hr(),
                    width={'size': 12, 'offset': 0}
                )
        ),
    dbc.Row(
            dbc.Col(
                    html.P(period_name, className="lead"),
                    width={'size': 6, 'offset': 0}
                ),
        ),
    dbc.Row(
            dbc.Col(
                    html.Hr(),
                    width={'size': 12, 'offset': 0}
                ),
        ),
    dbc.Nav(
            [
                dbc.NavLink("Grouping Parameters", href="/", active="exact"),
                dbc.NavLink("Update Roster", href="/page-1", active="exact"),
                dbc.NavLink("Student Groups", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE
)

# This is only for the non-sidebar stuff
content = html.Div(id="page-content", style=CONTENT_STYLE)

# This puts the whole damn thing together
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/page-1":
        return html.P("This is the content of page 1. Yay!")
    elif pathname == "/page-2":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True)
