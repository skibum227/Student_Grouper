# All Dash Imports
import dash
from dash import (Input,
                 Output,
                 State,
                 dcc,
                 html,
                 ctx,
                 dash_table)
import dash_bootstrap_components as dbc
import templates.styles as styles

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

#############
# APP Globals
#############

# All possible classes at PV
all_class_names = {'0':'Period 1', '1':'Period 2', '2':'Period 3', '3':'Period 4', '4':'Period 5', '5':'Period 6'}
# Connection to db for read/write
database = redis.StrictRedis(host='127.0.0.1',port='6379',db=0,charset="utf-8",decode_responses=True)

# Displays styles for on/off switing
on_style =  {'margin': '10px', 'width': '95%', 'display':'block'}
off_style = {'margin': '10px', 'width': '95%', 'display':'None'}

def current_availible_classes():
    # Simply returns all possible classes for initialization of app
    sorted_keys = database.keys()
    sorted_keys.sort()
    return [{'value':x, 'label':all_class_names[x]} for x in sorted_keys]

def parse_contents(contents, filename):
    # Read in differetn formats for class roster data
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

def save_to_database(df, name):
    # Takes input value and saves to the database with key
    data = json.dumps(df.student_names.tolist())
    database[name] = data

def build_roster_table(df):
    # Creates the output table for the uploaded class
    table_header = [html.Thead(html.Tr([html.Th("Class Roster")]))]
    table_body = [html.Tbody([html.Tr([html.Td(x)]) for x in df.student_names.to_list()])]
    table = dbc.Table(
        table_header + table_body,
        bordered=True, dark=True, hover=True, responsive=True, striped=True,
    )
    return table

############
# APP Layout
############

df = pd.DataFrame()
app.layout = html.Div([
    dbc.Button("Open Upload", id="offcanvas-upload-btn", n_clicks=0, style={'margin': '10px'}),
    dbc.Button("Open Adjust", id="offcanvas-adjust-btn", n_clicks=0, style={'margin': '10px'}),
    dbc.Button("Download Roster", id='download_btn', href="data_file.txt", color="primary", style={'margin': '10px'}),
    dcc.Download(id="download"), # this just enables the download to occur, nothing is displayed
    dbc.Offcanvas([
        html.H3(
            "Upload Class",
            className="my-2",
            style={'margin': '10px', 'width': '95%', 'textAlign': 'center'}
        ),
        html.Hr(style={'margin': '10px', 'width': '95%'}),
        dbc.Select(
            id="upload-a-class",
            options=[{"label": v, "value": k} for k,v in all_class_names.items()],
            style={'margin': '10px', 'width': '95%'}
        ),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                dbc.Button(
                    "Drag and Drop or Select Files",
                    outline=True,
                    color='primary',
                    style={'margin': '10px', 'width': '95%'}
                )
            ]),
        ),
        html.Br(),
        html.Hr(
            style={'margin': '10px', 'width': '95%'}
        ),
        dbc.Button(
            'Submit Period Name and Roster',
            id='submit-upload',
            className="me-2",
            style={'margin': '10px', 'width': '95%'},
            n_clicks=0
        ),
        html.P(
            id='upload-confirm',
            className="my-2",
            style={'margin': '10px', 'width': '95%', 'textAlign': 'center'}
        ),
        html.Div(id='data-to-upload', style={'margin': '10px', 'width': '100%'}),
    ], id="offcanvas-upload", title="Roster Database", is_open=False, placement='end', backdrop=True),
    dbc.Offcanvas([
        html.H3(
            "Select Class",
            className="my-2",
            style={'margin': '10px', 'width': '95%', 'textAlign': 'center'}
        ),
        html.Hr(style={'margin': '10px', 'width': '95%'}),
        dbc.Select(
            id="select-a-class",
            options=current_availible_classes(),
            style={'margin': '10px', 'width': '95%'}
        ),
        dbc.RadioItems(
            id='adjust-select',
            options=[
                {"label": "Add Student", "value": 1},
                {"label": "Remove Student", "value": 2},
                {"label": "Delete Class", "value": 3},
            ],
            value=1,
            style=on_style,
        ),
        html.Br(),
        html.Hr(
            style={'margin': '10px', 'width': '95%'}
        ),
        dbc.Input(
            id='student-name',
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
            color='warning',
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
            id='action-confirm',
            className="my-2",
            style={'margin': '10px', 'width': '95%', 'textAlign': 'center'}
        ),
    ], id="offcanvas-adjust", title="Roster Database", is_open=False, placement='end', backdrop=True),
])

# Download all roster data to csv (need to finish!)
@app.callback(
    Output("download", "data"),
    Input("download_btn", "n_clicks")
)
def generate_csv(n_nlicks):
    df = pd.DataFrame()
    if ctx.triggered_id == 'dwnld_btn':
        return dcc.send_data_frame(df.to_csv, filename="full_roster.csv")

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
        roster_df = parse_contents(contents, filename)

        roster_table = build_roster_table(roster_df)

        if ctx.triggered_id == 'submit-upload' and value:
            save_to_database(roster_df, value)
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
        return on_style, on_style, off_style, off_style, off_style
    elif action == 2:
        return off_style, off_style, on_style, on_style, off_style
    elif action == 3:
        return off_style, off_style, off_style, off_style, on_style
    else:
        return off_style, off_style, off_style, off_style, off_style

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
















