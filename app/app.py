# My libraries
from grouper import Grouper
from plotter import Plotter
import templates.styles as styles
import templates.core_components as core_components
import templates.roster_components as roster_components

# All dash libraries
import dash
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import Input, Output, State, dcc, html, ctx

# Easy healthcheck imports
from healthcheck import HealthCheck, EnvironmentDump

# All other imports
import base64
import io
import json
import pandas as pd
import boto3
import secrets
import os


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

# This is for the roster adjustments...
# All possible classes at PV
all_class_names = {'0':'Period 1',
                   '1':'Period 2',
                   '2':'Period 3',
                   '3':'Period 4',
                   '4':'Period 5',
                   '5':'Period 5-6',
                   '6':'Period 6',
                   '7':'Period 9',
                   '8':'Period 10'}

prelim_student_roster = all_class_names.values()

# Connection to db for read/write
#os.environ['AWS_PROFILE'] = "personal"
# if local
#dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8042")
# if containerized
print("here!!!!!!!!!!!!!!")
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")#, endpoint_url="http://dynamodb:8000")
print("here2")
database = dynamodb.Table('class_roster_storage')
print('here3')
print(database.key_schema)

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


#####################
# APP Components
#####################
app.title = 'The Student Grouper'

# Build the sidebar
sidebar = core_components.sidebar_component(title, subtitle)

# Build the params content
content_params = core_components.content_params_component(database, all_class_names)

# Build the roster content
content_roster = core_components.content_roster_component(prelim_student_roster)

# Build the database content
content_database = core_components.content_table_component()

# Build the roster tools
roster_tools = roster_components.offcanvas_control(database, all_class_names)

# This puts the whole damn thing together
app.layout = html.Div([dcc.Location(id="ip"), sidebar, roster_tools, content_params, content_roster, content_database])

############
# Call Backs
############

# Enables selecting a class to update
@app.callback(
    Output('period_selection', 'options'),
    Input('period_selection', 'value')
)
def get_loaded_classes(value):
    sorted_keys = roster_components.get_all_classes(database)
    sorted_keys.sort()
    return [{'value':x, 'label':all_class_names[x]} for x in sorted_keys]

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
def render_page_content(pathname, period_index, group_size, distribute_leftovers, student_roster):

    # Generate the df for only the particular period
    if period_index:
        period_selection = all_class_names[period_index]
        roster = database.get_item(Key={'class_name':period_index})['Item']
        df = pd.DataFrame(roster).rename(columns={'roster':'student_names'})
        student_names = df['student_names'].values.tolist()

    else:
        student_names=[]
        period_selection=None

    if pathname in ["/parameters", "/"]: # Left the old one on purpose
        return (
                    core_components.roster_builder(student_names), \
                    None, \
                    styles.CONTENT_STYLE_ON, \
                    styles.CONTENT_STYLE_OFF, \
                    styles.CONTENT_STYLE_OFF
               )

    elif pathname in ("/roster", "/groups") and period_index:

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
                        'period': period_selection,#.split('_')[1],
                        'gps':group_size_adj,
                        'distrib_lo': True if distribute_leftovers == 1 else False,
                     }
            # Run the grouping algorithm
            grouper = Grouper(params)
            df_gps = grouper.group_students()
            # Create the database figure
            fig = Plotter(params, df_gps).plot_groups()

            return (
                        core_components.roster_builder(df.student_names.to_list()), \
                        dcc.Graph(figure=fig), \
                        styles.CONTENT_STYLE_OFF, \
                        styles.CONTENT_STYLE_OFF, \
                        styles.CONTENT_STYLE_ON
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

        # Run through the classes to build the dict
        for x in database.scan()['Items']:
            roster_dict[f"{all_class_names[x['class_name']]}"] =  x['roster']
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
        roster_df = roster_components.parse_contents(contents, filename)

        roster_database = roster_components.build_roster_table(roster_df)

        if ctx.triggered_id == 'submit-upload' and value:
            roster_components.save_roster_to_database(database, value, roster_df)
            msg = f'{all_class_names[value]} has been saved'
        else:
            msg = ''

        return roster_database, msg

    return None, None

# Enables selecting a class to update
@app.callback(
    Output('select-a-class', 'options'),
    Input('select-a-class', 'value')
)
def get_loaded_classes(value):
    sorted_keys = roster_components.get_all_classes(database)
    sorted_keys.sort()
    return [{'value':x, 'label':all_class_names[x]} for x in sorted_keys]

# Controls which student is selected for removal
@app.callback(
    Output('select-a-student', 'options'),
    Input('select-a-class', 'value')
)
def get_student_names(class_index):
    if class_index:
        roster = database.get_item(Key={'class_name':class_index})['Item']['roster']
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
            styles.OFFCANVAS_ON_STYLE,
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
        roster = database.get_item(Key={'class_name':class_value})['Item']
        # Add the name
        roster['roster'].append(student_name)

        database.delete_item(Key={'class_name':class_value})
        database.put_item(Item=roster)

        msg = f'{student_name} has been added to {all_class_names[class_value]}!'

    elif ctx.triggered_id == 'delete-student' and class_value is not None and student_value is not None:
        # Get the roster
        roster = database.get_item(Key={'class_name':class_value})['Item']

        # Remove the name
        name = roster['roster'][int(student_value)]
        roster['roster'].pop(int(student_value))

        database.delete_item(Key={'class_name':class_value})
        database.put_item(Item=roster)

        msg = f'{name} has been removed from {all_class_names[class_value]}!'

    elif ctx.triggered_id == 'delete-class' and class_value is not None:
        database.delete_item(Key={'class_name':class_value})
        msg = f'{all_class_names[class_value]} has been deleted!'
    else:
        msg = ''
    return msg


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
