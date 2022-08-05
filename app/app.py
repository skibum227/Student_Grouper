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
subtitle = 'Room 1234'
stu_dict = pd.read_excel("student_ledger.xlsx", sheet_name=None)
periods = list(stu_dict.keys())
prelim_student_roster = list(stu_dict[periods[0]].student_names.values)

######################
# HEALTH CHECK ENDPOINTS
######################

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


################
# APP COMPONENTS
################

# Build the sidebar 
sidebar = components.sidebar_component(title, subtitle)

# Build the params content
content_params = components.content_params_component(periods)

# Build the roster content
content_roster = components.content_roster_component(prelim_student_roster)

# Build the table content
content_table = components.content_table_component()


###############
# Construct App
###############

# This puts the whole damn thing together
app.layout = html.Div([dcc.Location(id="ip"), sidebar, content_params, content_roster, content_table])


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
def render_page_content(pathname, period_selection, group_size, distribute_leftovers, student_roster):

    # Generate the df for only the particular period 
    df = pd.DataFrame(stu_dict[period_selection]).sort_values('student_names')
    # The list of student names
    student_names = df['student_names'].values.tolist()

    if pathname in ["/parameters", "/"]: # Left the old one on purpose
        return (
                    components.roster_builder(student_names), \
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
                        components.roster_builder(df.student_names.to_list()), \
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
                        components.roster_builder(df.student_names.to_list()), \
                        dcc.Graph(figure=fig), \
                        styles.CONTENT_STYLE_OFF, \
                        styles.CONTENT_STYLE_OFF, \
                        styles.CONTENT_STYLE_ON
                   )

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
