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
    return {"maintainer": "Skibum Woodworks",
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
                dbc.NavLink("Grouping Parameters", href="/activity_parameters", active="exact"),
                dbc.NavLink("Update Roster", href="/data", active="exact"),
                dbc.NavLink("Student Groups", href="/attendance", active="exact"),
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
#app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
app.layout = html.Div([dcc.Location(id="url"), 
    sidebar, 
    content])
   # html.Iframe(src="templates/activity_params.html",
    #            style={"height": "100px", "width": "100%"})])



###########
# Machinery
###########

# This is where the app actually starts...
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
#@server.route('/')
#@server.route('/activity_parameters')
def form(pathname): 
    if pathname == "/" or pathname == "/activity_parameters":
#        return render_template('activity_params.html', title='Student Grouper', username=name)
        return html.Iframe(src="templates/activity_params.html",style={"height": "100px", "width": "100%", 'color':'white'})

@server.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"You are lost, got back to '/activity_parameters'"

    if request.method == 'POST':
        period = request.form.get('period')
        group  = request.form.get('gps')
        dl     = True if request.form.get('dl') else False

        session['params'] = {'period': period, 'gps':int(group), 'distrib_lo': dl, 'filename': 'student_ledger.xlsx'}

        df = pd.read_excel('student_ledger.xlsx', sheet_name=f'period_{period}')
        stu_dict = pd.Series(['y']*df.size,index=df.student_names).to_dict()

        return render_template('check_attendance.html', title='Student Grouper', stu_dict=stu_dict)

@server.route('/attendance', methods=['POST', 'GET'])
def check_attendance():
    if request.method == 'GET':
        return f"You are lost, got back to '/activity_parameters'"

    if request.method == 'POST':
        present_stus=request.form.getlist('pres')
        grouper = Grouper(session['params'], present_stus)

        df = grouper.group_students()

        grouper.print_student_groups(df)

        graphjson = Plotter(session['params'], df).plot_groups()
        return render_template('plot_student_groups.html', graphjson=graphjson)

secret = secrets.token_urlsafe(32)
app.secret_key = secret

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
