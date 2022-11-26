from flask import Flask, request, render_template, session
from healthcheck import HealthCheck, EnvironmentDump

import secrets
from grouper import Grouper
from plotter import Plotter
import pandas as pd

import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import (Input,
                 Output,
                 State,
                 dcc,
                 html,
                 ctx,
                 dash_table)
    
import templates.styles as styles
import templates.core_components as core_components
import templates.roster_components as roster_components

# All other imports
import base64
import io
import json
import pandas as pd
import redis
import secrets


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

########################
# HEALTH CHECK ENDPOINTS
########################

health = HealthCheck()
envdump = EnvironmentDump()

def app_availible():
    return True, "App good to go!"

def application_data():
    return {"maintainer": "Skibum Woodworks Web Development Division",
            "git_repo": "https://github.com/skibum227/Student_Grouper"}

health.add_check(app_availible)
envdump.add_section("application", application_data)

# Add a flask route to expose information
server.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())
server.add_url_rule("/environment", "environment", view_func=lambda: envdump.run())

# All possible classes at PV
all_class_names = {'0':'Period 1', '1':'Period 2', '2':'Period 3', '3':'Period 4', '4':'Period 5', '5':'Period 6'}
# Connection to db for read/write
database = redis.StrictRedis(host='127.0.0.1',port='6379',db=0,charset="utf-8",decode_responses=True)


################
# APP core_components
################
app.title = 'The Student Grouper'

# Build the sidebar 
sidebar = core_components.sidebar_component(title, subtitle)

# Build the params content
content_params = core_components.content_params_component(periods)

# Build the roster content
content_roster = core_components.content_roster_component(prelim_student_roster)

# Build the table content
content_table = core_components.content_table_component()

# Build the roster tools
roster_tools = roster_components.offcanvas_control(database, all_class_names)

###############
# Construct App
###############

# This puts the whole damn thing together
#app.layout = html.Div([dcc.Location(id="ip"), sidebar, content_params, content_roster, content_table]) 
# app.layout = html.Div([dcc.Location(id="ip"), sidebar, content_params, roster_tools, content_roster, content_table]) 
app.layout = html.Div([dcc.Location(id="ip"), sidebar, content_params, content_roster, content_table, roster_tools]) 


@app.callback(
     Output(component_id="student_roster", component_property="children"),
     Output(component_id="grouper_table", component_property="children"),
     Output(component_id="parameters_page", component_property="style"),
     Output(component_id="student_roster_page", component_property="style"),
     Output(component_id="grouper_table_page", component_property="style"),

     Input(component_id="ip", component_property="pathname"),
     Input(component_id="period_selection", component_property="value"),
     Input(component_id="group_size", component_property="value"),
     Input(component_id="distribute_leftovers", component_property="value"),
     Input(component_id="student_roster", component_property="children")
)
# maybe something liek main_page.render_page_content(stuffff)
def render_page_content(pathname, period_selection, group_size, distribute_leftovers, student_roster):

    # Generate the df for only the particular period 
    df = pd.DataFrame(stu_dict[period_selection]).sort_values('student_names')
    # The list of student names
    student_names = df['student_names'].values.tolist()

    if pathname in ["/parameters", "/"]: # Left the old one on purpose
        return (
                    core_components.roster_builder(student_names), \
                    None, \
                    styles.CONTENT_STYLE_ON, \
                    styles.CONTENT_STYLE_OFF, \
                    styles.CONTENT_STYLE_OFF
               )

    elif pathname in ("/roster", "/groups"):

        # This is the result of wanting it to look nice, each student is in a different object
        keys = [
                    x["props"]["children"][0]["props"]["children"]["props"]["id"] 
                    for x in student_roster
               ]
        values = [
                    x["props"]["children"][0]["props"]["children"]["props"]["on"]
                    for x in student_roster
                 ]

        # Zips together all of the disjointed student attendance data from above so its usable
        df = pd.DataFrame(
                {k:v for (k,v) in zip(keys, values)}.items(),
                columns=["student_names", "present"]
             )
        df.sort_values("student_names", inplace=True)
        df = df[df.present.eq(True)]

        if pathname == "/roster":
            return (
                        core_components.roster_builder(df.student_names.to_list()), \
                        None, \
                        styles.CONTENT_STYLE_OFF, \
                        styles.CONTENT_STYLE_ON, \
                        styles.CONTENT_STYLE_OFF
                   )

        elif pathname == "/groups":

            # If the groups size is greater than the number of students, make the group size that number
            group_size_adj = len(df) if group_size > len(df) else group_size
            # Create the input params for the grouping and plotting algorithms
            params = {
                        'student_df': df,
                        'period': period_selection.split('_')[1],
                        'gps':group_size_adj,
                        'distrib_lo': True if distribute_leftovers == 1 else False,
                     } 
            # Run the grouping algorithm
            grouper = Grouper(params)
            df_gps = grouper.group_students()
            # Create the table figure
            fig = Plotter(params, df_gps).plot_groups()

            return (
                        core_components.roster_builder(df.student_names.to_list()), \
                        dcc.Graph(figure=fig), \
                        styles.CONTENT_STYLE_OFF, \
                        styles.CONTENT_STYLE_OFF, \
                        styles.CONTENT_STYLE_ON
                   )

    # If the user tries to reach a different page, return a 404 message
    return (
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )
    return (
        core_components.roster_builder(student_names), \
        None, \
        styles.CONTENT_STYLE_ON, \
        styles.CONTENT_STYLE_OFF, \
        styles.CONTENT_STYLE_OFF
    )


# Download all roster data to csv (need to finish!)
@app.callback(
    Output("download", "data"),
    Input("download_btn", "n_clicks")
)
def generate_csv(n_nlicks):
    if ctx.triggered_id == 'download_btn':
        roster_dict = {}
        for x in database.keys():
            roster = json.loads(database.get(x))
            roster_dict[f'{all_class_names[x]}'] = roster
        roster_df = pd.DataFrame.from_dict(roster_dict, orient='index').transpose()
        return dcc.send_data_frame(roster_df.to_csv, filename="full_roster.csv")

# Open/Close the offcanvas objects
@app.callback(
    Output("offcanvas-upload", "is_open"),
    Output("offcanvas-adjust", "is_open"),
    Input("offcanvas-upload-btn", "n_clicks"),
    Input("offcanvas-adjust-btn", "n_clicks"),
    [State("offcanvas-upload", "is_open"),
     State("offcanvas-adjust", "is_open")],
)
def toggle_offcanvas(n1, n2, is_open_upload, is_open_adjust):
    print(ctx.triggered_id)
    if ctx.triggered_id == 'offcanvas-upload-btn':
        return not is_open_upload, is_open_adjust
    elif ctx.triggered_id == 'offcanvas-adjust-btn':
        return is_open_upload, not is_open_adjust
    else:
        return is_open_upload, is_open_adjust

# Control the upload roster object
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
    if contents is not None:
        roster_df = parse_contents(contents, filename)

        roster_table = build_roster_table(roster_df)

        if ctx.triggered_id == 'submit-upload' and value:
            save_df_to_database(roster_df, value)
            msg = f'{all_class_names[value]} has been saved'
        else:
            msg = ''

        return roster_table, msg

    return None, None

# Enables selecting a class to update
@app.callback(
    Output('select-a-class', 'options'),
    Input('select-a-class', 'value')
)
def get_loaded_classes(value):

    sorted_keys = database.keys()
    sorted_keys.sort()
    return [{'value':x, 'label':all_class_names[x]} for x in sorted_keys]

# Controls which student is selected for removal
@app.callback(
    Output('select-a-student', 'options'),
    Input('select-a-class', 'value')
)
def get_student_names(class_index):
    if class_index:
        roster = json.loads(database.get(class_index))
        return [{"label": x, "value": f'{i}'} for i,x in enumerate(roster)]
    return []

# Changes which adjustment options are shown dependent on the selector
@app.callback(
    Output('student-name', 'style'),
    Output('add-student', 'style'),
    Output('select-a-student', 'style'),
    Output('delete-student', 'style'),
    Output('delete-class', 'style'),
    Input('adjust-select', 'value'),
    Input('select-a-class', 'value')
)
def display_actions(action, class_name):
    if action == 1:
        return (
            styles.OFFCANVAS_ON_STYLE,
            styles.OFFCANVAS_ON_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE
        )
    elif action == 2:
        return (
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_ON_STYLE,
            styles.OFFCANVAS_OFF_STYLE
        )
    elif action == 3:
        return (
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_ON_STYLE
        )
    else:
        return (
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE,
            styles.OFFCANVAS_OFF_STYLE
        )

# Handles all actions within selector options
@app.callback(
    Output('action-confirm', 'children'),
    Input('select-a-class', 'value'),
    Input('student-name', 'value'),
    Input('select-a-student', 'value'),
    Input('add-student', 'n_clicks'),
    Input('delete-student', 'n_clicks'),
    Input('delete-class', 'n_clicks'),
)
def make_changes(class_value, student_name, student_value, n_clicks_as, n_clicks_ds, n_clicks_dc):

    if ctx.triggered_id == 'add-student' and class_value is not None and student_name is not None:
        # Get the roster
        roster = json.loads(database.get(class_value))
        # Add the name
        roster.append(student_name)
        # Save it!
        database[class_value] = json.dumps(roster)

        msg = f'{student_name} has been added to {all_class_names[class_value]}!'

    elif ctx.triggered_id == 'delete-student' and class_value is not None and student_value is not None:
        # Get the roster
        roster = json.loads(database.get(class_value))
        # Remove the name
        name = roster[int(student_value)]
        roster.pop(int(student_value))
        # Save it!
        database[class_value] = json.dumps(roster)

        msg = f'{name} has been removed from {all_class_names[class_value]}!'

    elif ctx.triggered_id == 'delete-class' and class_value is not None:
        database.delete(class_value)
        msg = f'{all_class_names[class_value]} has been deleted!'
    else:
        msg = ''
    return msg



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
