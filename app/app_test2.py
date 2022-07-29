from flask import Flask, request, render_template, session
from healthcheck import HealthCheck, EnvironmentDump

import secrets
from grouper import Grouper
from plotter import Plotter
import pandas as pd

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, dcc, html

import templates.styles as styles
import templates.components as components
# https://pythonbasics.org/flask-tutorial-templates/
# https://stackoverflow.com/questions/53344797/how-create-an-array-with-checkboxes-in-flask
# https://medium.com/geekculture/aws-container-services-part-1-b147e974c745
# https://dev.to/marounmaroun/running-docker-container-with-gunicorn-and-flask-4ihg
# Make it all look nice
# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/toast/


#app = Flask(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
server = app.server

####################
# APP CONSTANTS
####################
name = 'Mrs. Herr'
subtitle = 'The Student Grouper'

# temp
stu_dict = pd.read_excel('student_ledger.xlsx', sheet_name=None)
periods = list(stu_dict.keys())
period = 'period_2'
df = pd.DataFrame(stu_dict[period])
df.sort_values('student_names', inplace=True)
student_names = df['student_names'].values.tolist()


######################
# HEALTH CHECK ENPONTS
######################
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
server.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())
server.add_url_rule("/environment", "environment", view_func=lambda: envdump.run())


################
# APP COMPONENTS
################

# Build the sidebar 
sidebar = components.sidebar_builder(name, subtitle)

# Build the params content
content_params = components.content_params_builder(periods)

# Build the roster content
content_roster = components.content_roster_builder(student_names)

# Build the table content
from dash import dcc
import plotly.express as px

df = px.data.iris()  # iris is a pandas dataframe
fig = px.scatter(df, x="sepal_width", y="sepal_length")
content_table = components.content_table_builder(fig)


###############
# Construct App
###############

# This puts the whole damn thing together
app.layout = html.Div([dcc.Location(id="ip"), sidebar, content_params, content_roster, content_table])


@app.callback(
     Output(component_id="output_period_1", component_property="children"),
     Output(component_id="output_cnt_1", component_property="children"),
     Output(component_id="output_distrib_1", component_property="children"),
     Output(component_id="page_content_two", component_property="children"),
     Output(component_id="page-content_three", component_property="children"),
     Output(component_id="page-content_one", component_property="style"),
     Output(component_id="page_content_two", component_property="style"),
     Output(component_id="page-content_three", component_property="style"),

     Input(component_id="ip", component_property="pathname"),
     Input(component_id="input_period_1", component_property="value"),
     Input(component_id="input_cnt_1", component_property="value"),
     Input(component_id="input_distrib_1", component_property="value"),
     Input(component_id="page_content_two", component_property="children")
)
def render_page_content(pathname, input_period_1, input_cnt_1, input_distrib_1, page_content_two):
    from dash import dcc
    import plotly.express as px

    df_yea = px.data.iris()  # iris is a pandas dataframe
    fig = px.scatter(df_yea, x="sepal_width", y="sepal_length")

    df = pd.DataFrame(stu_dict[input_period_1])
    df.sort_values('student_names', inplace=True)
    student_names = df['student_names'].values.tolist()
    #html.P(f'Output three: {input_three}'), \

    if pathname in ["/parameters", "/"]: # Left the old one on purpose
        return html.P(f'Selection Idx: {input_period_1}'), \
               html.P(f'Students in group: {input_cnt_1}'), \
               html.P(f'Distribute Leftovers: {input_distrib_1}'), \
               [(dbc.Row([
                    dbc.Col(
                        daq.ToggleSwitch(id=f'{x}', color='#4682b4', value=True),
                        width={'size': 4, 'offset': 0, 'align':'start'},
                    ),
                    dbc.Col(
                        html.P(f'{x}'),
                        width={'size': 4, 'offset': 0, 'justify':'start'},
                    )]))for x in student_names ], \
               dcc.Graph(figure=fig), \
               styles.CONTENT_STYLE_ON, \
               styles.CONTENT_STYLE_OFF, \
               styles.CONTENT_STYLE_OFF

    elif pathname == "/roster":
        keys = [x['props']['children'][0]['props']['children']['props']['id'] for x in page_content_two]
        values = [x['props']['children'][0]['props']['children']['props']['value'] for x in page_content_two]
        df = pd.DataFrame({k:v for (k,v) in zip(keys, values)}.items(), columns=['student_names', 'present']).sort_values('student_names')
        df = df[df.present.eq(True)]
        print(df)
        return html.P(f'Selection Idx: {input_period_1}'), \
               html.P(f'Students in group: {input_cnt_1}'), \
               html.P(f'Distribute Leftovers: {input_distrib_1}'), \
               [(dbc.Row([
                    dbc.Col(
                        daq.ToggleSwitch(id=f'{x}', color='#4682b4', value=True),
                        width={'size': 4, 'offset': 0, 'align':'start'},
                    ),
                    dbc.Col(
                        html.P(f'{x}'),
                        width={'size': 4, 'offset': 0, 'justify':'start'},
                    )]))for x in student_names ], \
               dcc.Graph(figure=fig), \
               styles.CONTENT_STYLE_OFF, \
               styles.CONTENT_STYLE_ON, \
               styles.CONTENT_STYLE_OFF
    elif pathname == "/groups":
        keys = [x['props']['children'][0]['props']['children']['props']['id'] for x in page_content_two]
        values = [x['props']['children'][0]['props']['children']['props']['value'] for x in page_content_two]
        df = pd.DataFrame({k:v for (k,v) in zip(keys, values)}.items(), columns=['student_names', 'present']).sort_values('student_names')
        df = df[df.present.eq(True)]
        print(df)

        params = {'student_df': df, 'period': input_period_1, 'gps':3, 'distrib_lo': False, 'filename': 'student_ledger.xlsx'} 
        grouper = Grouper(params)
        df_gps = grouper.group_students()
        #print(df_gps.columns)

        params = {'period': '1', 'gps':3, 'distrib_lo': False, 'filename': 'student_ledger.xlsx', 'dont_plot': False}
        fig = Plotter(params, df_gps).plot_groups()

        return html.P(f'Selection Idx: {input_period_1}'), \
               html.P(f'Students in group: {input_cnt_1}'), \
               html.P(f'Distribute Leftovers: {input_distrib_1}'), \
               [(dbc.Row([
                    dbc.Col(
                        daq.ToggleSwitch(id=f'{x}', color='#4682b4', value=True),
                        width={'size': 4, 'offset': 0, 'align':'start'},
                    ),
                    dbc.Col(
                        html.P(f'{x}'),
                        width={'size': 4, 'offset': 0, 'justify':'start'},
                    )]))for x in student_names ], \
               dcc.Graph(figure=fig), \
               styles.CONTENT_STYLE_OFF, \
               styles.CONTENT_STYLE_OFF, \
               styles.CONTENT_STYLE_ON

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











