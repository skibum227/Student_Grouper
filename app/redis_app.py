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

################
# APP DEFINITION
################

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

@app.callback()
def render_page_content():

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
