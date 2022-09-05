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

# Notes
# Want to use this: Offcanvas and start with loading/deleting a whole class



################
# APP DEFINITION
################

# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
secret = secrets.token_urlsafe(32)
app.secret_key = secret
server = app.server

###############
# APP CONSTANTS
###############

title = 'Student Grouper'
subtitle = 'Room 253'
stu_dict = pd.read_excel("student_ledger.xlsx", sheet_name=None)
periods = list(stu_dict.keys())
prelim_student_roster = list(stu_dict[periods[0]].student_names.values)


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(external_stylesheets=external_stylesheets)

app.layout = html.Div(
    dbc.Row([
        dbc.Col([
            html.Div(dcc.Input(id='input-on-submit',
                               type='text',
                               placeholder='Enter Period Name',
                               autoFocus=True,
                               style={'margin': '10px', 'width': '25%'}
                               )
                    ),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '25%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload', style={'margin': '10px', 'width': '25%'}),
            html.Br(),
            html.Button('Submit Period Name and Roster', id='submit-val', style={'margin': '10px', 'width': '25%'}, n_clicks=0),
            html.Div(id='container-button-basic', children='Enter a value and press submit'),
        ], width={'size': 5, 'offset': 1}),
        dbc.Col([
            html.Div(dcc.Input(id='input-on-submit2',
                               type='text',
                               placeholder='Enter Period Name',
                               autoFocus=True,
                               style={'margin': '20px', 'width': '25%'}
                               )
                    ),
            dcc.Upload(
                id='upload-data2',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '25%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=True
            ),
            html.Div(id='output-data-upload2', style={'margin': '10px', 'width': '25%'}),
            html.Br(),
            html.Button('Submit Period Name and Roster', id='submit-val2', style={'margin': '10px', 'width': '25%'}, n_clicks=0),
            html.Div(id='container-button-basic2', children='Enter a value and press submit'),
        ], width={'size': 5, 'offset': 6})
    ])
)

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    # Redis test
    test = json.dumps(df.iloc[:,0].tolist())

    r = redis.StrictRedis(host='127.0.0.1',
            port='6379',
            db=0,
            charset="utf-8",
            decode_responses=True
        )
    r['roster'] = test
    print(r.get('roster'))


    return html.Div([
        # html.H5(filename),
        # html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns]
        ),

        # html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
    ])

@app.callback(Output('output-data-upload', 'children'),
              Output('container-button-basic', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
              Input('submit-val', 'n_clicks'),
              State('input-on-submit', 'value')
              )
def update_output(list_of_contents, list_of_names, list_of_dates, n_clicks, value):
    # This enables the button and roster to work together
    children = None
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]

    if ctx.triggered_id == 'submit-val':
        msg = f'Period {value} has been saved'
    else:
        msg = ''

    return children, msg





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
