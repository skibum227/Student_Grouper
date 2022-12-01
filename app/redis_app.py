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
import boto3
import secrets

# Specific for app
import templates.styles as styles
import templates.roster_components as roster_components

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
#database = redis.StrictRedis(host='127.0.0.1',port='6379',db=0,charset="utf-8",decode_responses=True)


# Get the service resource.
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

# Create the DynamoDB table.
# docker run -p 8000:8000 amazon/dynamodb-local
try:
    table = dynamodb.create_table(
        TableName='rosters',
        KeySchema=[
            {
                'AttributeName': 'class_name',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'class_name',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 25,
            'WriteCapacityUnits': 25
        }
    )

    # Wait until the table exists.
    table.wait_until_exists()
except:
    print("db exists")

table = dynamodb.Table('rosters')

# Displays styles for on/off switing
on_style =  {'margin': '10px', 'width': '95%', 'display':'block'}
off_style = {'margin': '10px', 'width': '95%', 'display':'None'}


def current_availible_classes():
    # Simply returns all possible classes for initialization of app
    sorted_keys = get_all_classes()
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

def save_roster_to_database(class_name, df):
    # Takes input value and saves to the database with key
    data_dict = {}
    df.student_names.tolist()
    data_dict['roster'] = df.student_names.tolist()
    data_dict['class_name'] = class_name
    table.put_item(Item=data_dict)

def get_all_classes():
    return [x['class_name'] for x in table.scan()['Items']]

def build_roster_table(df):
    # Creates the output table for the uploaded class
    table_header = [html.Thead(html.Tr([html.Th("Class Roster")]))]
    table_body = [html.Tbody([html.Tr([html.Td(x)]) for x in df.iloc[:,0].to_list()])]
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
    dbc.Row([dbc.Col([
        dbc.Button("Upload a Roster", id="offcanvas-upload-btn", n_clicks=0, style={'margin': '10px', 'size':'3'})
    ], width=2)], justify='end'),
    dbc.Row([dbc.Col([
        dbc.Button("Adjust a Roster", id="offcanvas-adjust-btn", n_clicks=0, style={'margin': '10px', 'size':'3'}),
    ], width=2)], justify='end'),
    dbc.Row([dbc.Col([
        dbc.Button("Download Roster", id='download_btn', href="data_file.txt", color="primary", style={'margin': '10px', 'size':'4'}),
    ], width=2)], justify='end'),
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
    if ctx.triggered_id == 'download_btn':
        roster_dict = {}

        # Run through the classes to build the dict
        for x in table.scan()['Items']:
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
        roster_df = parse_contents(contents, filename)

        roster_table = build_roster_table(roster_df)

        if ctx.triggered_id == 'submit-upload' and value:
            save_roster_to_database(value, roster_df)
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

    sorted_keys = get_all_classes()
    sorted_keys.sort()
    return [{'value':x, 'label':all_class_names[x]} for x in sorted_keys]

# Controls which student is selected for removal
@app.callback(
    Output('select-a-student', 'options'),
    Input('select-a-class', 'value')
)
def get_student_names(class_index):
    if class_index:
        roster = table.get_item(Key={'class_name':class_index})['Item']['roster']
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
        roster = table.get_item(Key={'class_name':class_value})['Item']
        # Add the name
        roster['roster'].append(student_name)

        table.delete_item(Key={'class_name':class_value})
        table.put_item(Item=roster)

        msg = f'{student_name} has been added to {all_class_names[class_value]}!'

    elif ctx.triggered_id == 'delete-student' and class_value is not None and student_value is not None:
        # Get the roster
        roster = table.get_item(Key={'class_name':class_value})['Item']

        # Remove the name
        name = roster['roster'][int(student_value)]
        roster['roster'].pop(int(student_value))

        table.delete_item(Key={'class_name':class_value})
        table.put_item(Item=roster)

        msg = f'{name} has been removed from {all_class_names[class_value]}!'

    elif ctx.triggered_id == 'delete-class' and class_value is not None:
        table.delete_item(Key={'class_name':class_value})
        msg = f'{all_class_names[class_value]} has been deleted!'
    else:
        msg = ''
    return msg


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
















