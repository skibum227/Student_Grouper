import templates.styles as styles

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

def current_availible_classes(database):
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

def save_df_to_database(df, name, database):
    # Takes input value and saves to the database with key
    data = json.dumps(df.student_names.tolist())
    database[name] = data

def build_roster_table(df):
    # Creates the output table for the uploaded class
    table_header = [html.Thead(html.Tr([html.Th("Class Roster")]))]
    table_body = [html.Tbody([html.Tr([html.Td(x)]) for x in df.iloc[:,0].to_list()])]
    table = dbc.Table(
        table_header + table_body,
        bordered=True, dark=True, hover=True, responsive=True, striped=True,
    )
    return table

# This is only for the side bar
def control_buttons_component():
    control_buttons = html.Div([
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
    ])
    return control_buttons

def upload_class_component():
    upload_class = html.Div([
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
    ])
    return upload_class

def adjust_class_component():
    adjust_class = html.Div([
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
                style=styles.OFFCANVAS_ON_STYLE,
            ),
            html.Br(),
            html.Hr(
                style={'margin': '10px', 'width': '95%'}
            ),
            dbc.Input(
                id='student-name',
                placeholder="Enter New Student's Name...",
                type="text",
                style=styles.OFFCANVAS_OFF_STYLE,
            ),
            dbc.Button(
                'Add Student',
                id='add-student',
                color='success',
                className="me-1",
                style=styles.OFFCANVAS_OFF_STYLE,
                n_clicks=0
            ),
            dbc.Select(
                id="select-a-student",
                options=[],
                style=styles.OFFCANVAS_OFF_STYLE,
            ),
            dbc.Button(
                'Delete Student',
                id='delete-student',
                color='warning',
                className="me-1",
                style=styles.OFFCANVAS_OFF_STYLE,
                n_clicks=0
            ),
            dbc.Button(
                'Delete Class',
                id='delete-class',
                color='danger',
                className="me-1",
                style=styles.OFFCANVAS_OFF_STYLE,
                n_clicks=0
            ),
            html.P(
                id='action-confirm',
                className="my-2",
                style={'margin': '10px', 'width': '95%', 'textAlign': 'center'}
            ),
        ], id="offcanvas-adjust", title="Roster Database", is_open=False, placement='end', backdrop=True),
    ])
    return adjust_class


