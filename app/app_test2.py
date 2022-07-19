from flask import Flask, request, render_template, session
from healthcheck import HealthCheck, EnvironmentDump

import secrets
from grouper import Grouper
from plotter import Plotter
import pandas as pd
# https://pythonbasics.org/flask-tutorial-templates/
# https://stackoverflow.com/questions/53344797/how-create-an-array-with-checkboxes-in-flask
# https://medium.com/geekculture/aws-container-services-part-1-b147e974c745
# https://dev.to/marounmaroun/running-docker-container-with-gunicorn-and-flask-4ihg
# Make it all look nice
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/toast/

app = Flask(__name__)
name = 'Mrs. Herr'

####################
# HEALTH CHECKS!!!!!
####################
health = HealthCheck()
envdump = EnvironmentDump()

def app_availible():
    return True, "App good to go!"

def application_data():
    return {"maintainer": "Skibum Woodworks Web Developement Division",
            "git_repo": "https://github.com/skibum227/Student_Grouper"}

health.add_check(app_availible)
envdump.add_section("application", application_data)

# Add a flask route to expose information
app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())
app.add_url_rule("/environment", "environment", view_func=lambda: envdump.run())


##################################
# Lets try to build the new app...
##################################
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, dcc, html


# 2. Create a Dash app instance
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
server = app.server

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
CONTENT_STYLE_ON = {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 0rem",
    "display": "block"
}

CONTENT_STYLE_OFF= {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 0rem",
    'display': 'none'
}

##### this is me trying to recreate it
teacher_name = 'Mrs. Herr'
period_name = 'Period 2'

# This is only for the side bar
sidebar = html.Div([
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
    dbc.Nav([
            # dbc.NavLink("Grouping Parameters", href="/parameters", active="exact"),
            dbc.NavLink("Grouping Parameters", href="/", active="exact"),
            dbc.NavLink("Update Roster", href="/roster", active="exact"),
            dbc.NavLink("Student Groups", href="/groups", active="exact"),
        ],
        vertical=True,
        pills=True,
    )],
    style=SIDEBAR_STYLE,
    id='sidebar-content'
)   

# This is only for the non-sidebar stuff
content_params = html.Div([
    dbc.Row(
        dbc.Col(
            dbc.RadioItems(
                id="input_period_1",
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",
                labelCheckedClassName="active",
                options=[
                    {"label": "Period 1", "value": 1},
                    {"label": "Period 2", "value": 2},
                    {"label": "Period 3", "value": 3},
                ],
                value=1,
            ),
            width={'size': 4, 'offset': 0}
        ),
    ),
    dbc.Row(
        dbc.Col(
            html.Div(id='output_period_1'),
            width={'size': 4, 'offset': 0}
        )

    ),
    dbc.Row(
        dbc.Col(
            dbc.Input(id="input_cnt_1", placeholder="Number of Students in group", type="number", min=0, max=10, step=1),
            width={'size': 4, 'offset': 0}
        )
    ),
    dbc.Row(
        dbc.Col(
            html.Div(id='output_cnt_1'),
            width={'size': 4, 'offset': 0}
        )

    ),
    dbc.Row(
            dbc.RadioItems(
                id="input_distrib_1",
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",
                labelCheckedClassName="active",
                options=[
                    {"label": "Yes", "value": 1},
                    {"label": "No", "value": 0},
                ],
                value=1,
            ),
    ),
    dbc.Row(
        dbc.Col(
            html.Div(id='output_distrib_1'),
            width={'size': 4, 'offset': 0}
        )
    )], 
    id="page-content_one",
    style=CONTENT_STYLE_ON
)

content_roster = html.Div([
    # https://dash.plotly.com/dash-core-components/checklist
    dbc.Row(
        dbc.Col(
            daq.ToggleSwitch(id='input_two', label='Present example', labelPosition='top', color='#4682b4', value=True),
            # dcc.Input(id='input_two', value='test input two', type='text'),
            width={'size': 4, 'offset': 0}
        ),
    ),
    dbc.Row(
        dbc.Col(
            html.Div(id='output_two')
        )
    )], 
    id="page-content_two",
    style=CONTENT_STYLE_OFF
)

content_groups = html.Div([
    dbc.Row(
        dbc.Col(
            dcc.Input(id='input_three', value='test input three', type='text'),
            width={'size': 4, 'offset': 0}
        ),
    ),
    dbc.Row(
        dbc.Col(
            html.Div(id='output_three')
        )
    )], 
    id="page-content_three",
    style=CONTENT_STYLE_OFF
)
# This puts the whole damn thing together
app.layout = html.Div([dcc.Location(id="ip"), sidebar, content_params, content_roster, content_groups])


@app.callback(
     Output(component_id="output_period_1", component_property="children"),
     Output(component_id="output_cnt_1", component_property="children"),
     Output(component_id="output_distrib_1", component_property="children"),
     Output(component_id="output_two", component_property="children"),
     Output(component_id="output_three", component_property="children"),
     Output(component_id="page-content_one", component_property="style"),
     Output(component_id="page-content_two", component_property="style"),
     Output(component_id="page-content_three", component_property="style"),
     Input(component_id="ip", component_property="pathname"),
     Input(component_id="input_period_1", component_property="value"),
     Input(component_id="input_cnt_1", component_property="value"),
     Input(component_id="input_distrib_1", component_property="value"),
     Input(component_id="input_two", component_property="value"),
     Input(component_id="input_three", component_property="value")
)
def render_page_content(pathname, input_period_1, input_cnt_1, input_distrib_1, input_two, input_three):
    if pathname in ["/parameters", "/"]: # Left the old one on purpose
        return html.P(f'Selected Period {input_period_1}'), \
               html.P(f'Students in group: {input_cnt_1}'), \
               html.P(f'Distribute Leftovers: {input_distrib_1}'), \
               html.P(f'Output two: {input_two}'), \
               html.P(f'Output three: {input_three}'), \
               CONTENT_STYLE_ON, \
               CONTENT_STYLE_OFF, \
               CONTENT_STYLE_OFF
    elif pathname == "/roster":
        return html.P(f'Selected Period {input_period_1}'), \
               html.P(f'Students in group: {input_cnt_1}'), \
               html.P(f'Distribute Leftovers: {input_distrib_1}'), \
               html.P(f'Output two: {input_two}'), \
               html.P(f'Output three: {input_three}'), \
               CONTENT_STYLE_OFF, \
               CONTENT_STYLE_ON, \
               CONTENT_STYLE_OFF
    elif pathname == "/groups":
        return html.P(f'Selected Period {input_period_1}'), \
               html.P(f'Students in group: {input_cnt_1}'), \
               html.P(f'Distribute Leftovers: {input_distrib_1}'), \
               html.P(f'Output two: {input_two}'), \
               html.P(f'Output three: {input_three}'), \
               CONTENT_STYLE_OFF, \
               CONTENT_STYLE_OFF, \
               CONTENT_STYLE_ON

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


secret = secrets.token_urlsafe(32)
app.secret_key = secret

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)











