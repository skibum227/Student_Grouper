from flask import Flask, request, render_template, session
from healthcheck import HealthCheck, EnvironmentDump

import secrets
from grouper import Grouper
from plotter import Plotter
import pandas as pd

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, dcc, html, ctx

import templates.styles as styles
import templates.components as components

#------

# for reading in a file
import base64
import datetime
import io

from dash.dependencies import Input, Output, State
from dash import dash_table
# ----

# for redis
import redis
import json

import pandas as pd
# Notes
# Want to use this: Offcanvas and start with loading/deleting a whole class

#https://dash-bootstrap-components.opensource.faculty.ai/docs/components/table/
#https://dash.plotly.com/basic-callbacks#dash-app-with-chained-callbacks

################
# APP DEFINITION
################

# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
secret = secrets.token_urlsafe(32)
app.secret_key = secret
server = app.server

###############
# APP Constants
###############

class_names = {'0':'Period 1', '1':'Period 2', '2':'Period 3', '3':'Period 4', '4':'Period 5', '5':'Period 6'}
r = redis.StrictRedis(host='127.0.0.1',port='6379',db=0,charset="utf-8",decode_responses=True)

def current_availible_classes():
    r = redis.StrictRedis(host='127.0.0.1',port='6379',db=0,charset="utf-8",decode_responses=True)
    sorted_keys = r.keys()
    sorted_keys.sort()
    return [{'value':x, 'label':class_names[x]} for x in sorted_keys]

on_style =  {'margin': '10px', 'width': '100%', 'display':'block'}
off_style = {'margin': '10px', 'width': '100%', 'display':'block'}

###############
# APP Layout
###############

df = pd.DataFrame()
app.layout = html.Div(
    dbc.Row([
        dbc.Col([
            html.H3(
                "Upload Class",
                className="my-2",
                style={'margin': '10px', 'width': '100%', 'textAlign': 'center'}
            ),
            html.Hr(style={'margin': '10px', 'width': '100%'}),
            dbc.Select(
                id="upload-a-class",
                options=[{"label": v, "value": k} for k,v in class_names.items()],
                style={'margin': '10px', 'width': '100%'}
            ),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    dbc.Button(
                        "Drag and Drop or Select Files",
                        outline=True,
                        color='primary',
                        style={'margin': '10px', 'width': '100%'}
                    )
                ]),
            ),
            html.Br(),
            html.Hr(
                style={'margin': '10px', 'width': '100%'}
            ),
            dbc.Button(
                'Submit Period Name and Roster',
                id='submit-upload',
                className="me-2",
                style={'margin': '10px', 'width': '100%'},
                n_clicks=0
            ),
            html.P(
                id='upload-confirm',
                className="my-2",
                style={'margin': '10px', 'width': '100%', 'textAlign': 'center'}
            ),
        ], width={'size':2, 'offset': 1}),
        dbc.Col([
            html.Div(id='data-to-upload', style={'margin': '10px', 'width': '100%'}),
        ], width={'size':2, 'offset': 0}),
        dbc.Col([
            html.H3(
                "Select Class",
                className="my-2",
                style={'margin': '10px', 'width': '100%', 'textAlign': 'center'}
            ),
            html.Hr(style={'margin': '10px', 'width': '100%'}),
            dbc.Select(
                id="select-a-class",
                options=current_availible_classes(),
                style={'margin': '10px', 'width': '100%'}
            ),
            dbc.RadioItems(
                id='adjsut-select',
                options=[
                    {"label": "Add Student", "value": 1},
                    {"label": "Remove Student", "value": 2},
                    {"label": "Delete Class", "value": 3},
                ],
                value=1,
                style=on_style,
            ),
            dbc.Input(
                placeholder="Enter New Student's Name...", 
                type="text",
                style=off_style,
            ),
            dbc.Button(
                'Add Student',
                id='add-student',
                color='success',
                className="me-1",
                style=off_style,
                n_clicks=0
            ),
            dbc.Select(
                id="select-a-student",
                options=[],
                style=off_style,
            ),
            dbc.Button(
                'Delete Student',
                id='delete-student',
                color='danger',
                className="me-1",
                style=off_style,
                n_clicks=0
            ),
            dbc.Button(
                'Delete Class',
                id='delete-class',
                color='danger',
                className="me-1",
                style=off_style,
                n_clicks=0
            ),
            html.P(
                id='delete-confirm',
                className="my-2",
                style={'margin': '10px', 'width': '100%', 'textAlign': 'center'}
            ),
        ], width={'size':2, 'offset': 0}),
    ])
)



def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df

def save_to_redis(df, name):
    data = json.dumps(df.student_names.tolist())
    r[name] = data
#    print(r.get(name))
    # print(r.keys())
  
def build_roster_table(df):
    # Create the header for the table
    table_header = [html.Thead(html.Tr([html.Th("Class Roster")]))]
    # Create tehe body of the tabl
    table_body = [html.Tbody([html.Tr([html.Td(x)]) for x in df.student_names.to_list()])]
    # Create the table
    table = dbc.Table(
        table_header + table_body,
        bordered=True,
        dark=True,
        hover=True,
        responsive=True,
        striped=True
    )
    return table

@app.callback(
    Output('data-to-upload', 'children'),
    Output('upload-confirm', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    Input('submit-upload', 'n_clicks'),
    State('upload-a-class', 'value')
)
def update_output(contents, filename,  n_clicks, value):
    # This enables the button and roster to work together
    #roster_df = pd.DataFrame()
    if contents is not None:
        roster_df = parse_contents(contents, filename)

        roster_table = build_roster_table(roster_df)

        if ctx.triggered_id == 'submit-upload' and value:
            save_to_redis(roster_df, value)
            msg = f'{class_names[value]} has been saved'
        else:
            msg = ''

        return roster_table, msg

    return None, None


@app.callback(
    Output('select-a-class', 'options'),
    Output('delete-confirm', 'children'),
    Input('delete-class', 'n_clicks'),
    State('select-a-class', 'value')
)
def get_loaded_classes(n_clicks, value):
    # needs a redis connection
    if ctx.triggered_id == 'delete-class' and value:
        r.delete(value)
        msg = f'{class_names[value]} has been deleted!'
    else:
        msg = ''

    sorted_keys = r.keys()
    sorted_keys.sort()
    return [{'value':x, 'label':class_names[x]} for x in sorted_keys], msg

@app.callback(
    Output('select-a-student', 'options'),
    Input('select-a-class', 'value')
)
def get_student_names(class_index):
    if class_index:
        roster = json.loads(r.get(class_index))
        return [{"label": x, "value": f'{i}'} for i,x in enumerate(roster)]
    return []


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
















