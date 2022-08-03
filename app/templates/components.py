import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html, dcc

import templates.styles as styles

# This is only for the side bar
def sidebar_component(name, subtitle):
    sidebar = html.Div([
        dbc.Row(
            dbc.Col(
                html.H2(name, className="display-4"),
                width={'size': 12, 'offset': 0}
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Hr(),
                width={'size': 12, 'offset': 0}
            )
        ),
        dbc.Row(
            dbc.Col(
                html.P(subtitle, className="lead"),
                width={'size': 12, 'offset': '1'},
            ),
        ),
        dbc.Row(
            dbc.Col(
                html.Hr(),
                width={'size': 12, 'offset': 0}
            ),
        ),
        dbc.Nav([
                dbc.NavLink("Grouping Parameters", href="/", active="exact"),
                dbc.NavLink("Update Roster", href="/roster", active="exact"),
                dbc.NavLink("Student Groups", href="/groups", active="exact"),
            ],
            vertical=True,
            pills=True,
        )],
        style=styles.SIDEBAR_STYLE,
        id='sidebar-content'
    )
    return sidebar


def content_params_component(periods):
    content_params = html.Div([
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H3("Select Class Period", className="display-7"),
                        html.P(
                            "This will be the class roster that will be grouped..."
                        ),
                    ],
                ),
                width={'size': 10, 'offset': 0},
                style={'color':'#d3d3d3'}
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.RadioItems(
                    id="period_selection",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label":x, "value":x}
                    for i, x in enumerate(periods)],
                    value=periods[0],
                ),
                width={'size': 12, 'offset': 0}
            ),
        ),
        html.Br(),
        dbc.Row(
            dbc.Col(
                html.Hr(),
                width={'size': 10, 'offset': 0}
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H3("Select Group Size", className="display-7"),
                        html.P(
                            "This value will be the number of students in each group..."
                        ),
                    ],
                ),
                width={'size': 10, 'offset': 0},
                style={'color':'#d3d3d3'}
            )
        ),
        dbc.Row(
            dbc.Col(
                # dbc.Input(id="group_size", placeholder="Input a number", type="number", min=0, max=10, step=1),
                dbc.RadioItems(
                    id="group_size",
                    options=[
                        {"label": "2" , "value": 2},
                        {"label": "3" , "value": 3},
                        {"label": "4" , "value": 4},
                        {"label": "5" , "value": 5},
                    ],
                    value=2,
                    inline=True,
                 ),
                width={'size': 4, 'offset': 0}
            )
        ),
        html.Br(),
        dbc.Row(
            dbc.Col(
                html.Hr(),
                width={'size': 10, 'offset': 0}
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H3("Distribute Non-Complete Groups", className="display-7"),
                        html.P(
                            "This demarcates what to do if the roster isnt cleanly divisble by the group count..."
                        ),
                    ],
                ),
                width={'size': 10, 'offset': 0},
                style={'color':'#d3d3d3'}
            )
        ),
        dbc.Row(
                dbc.RadioItems(
                    id="distribute_leftovers",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "Yes", "value": 1},
                        {"label": "No", "value": 0},
                    ],
                    value=1,
                ),
        )], 
        id="page-content_one",
        style=styles.CONTENT_STYLE_ON
    )
    return content_params

def content_roster_component():
    content_roster = html.Div([
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H3("Update Student Attendence", className="display-7"),
                        html.P(
                            "Students not present today will not be factored into the grouping algorithm..."
                        ),
                    ],
                ),
                width={'size': 10, 'offset': 0},
                style={'color':'#d3d3d3'},
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Hr(),
                width={'size': 10, 'offset': 0}
            )
        ),
        html.Br(),
        html.Div(
            id="student_roster"
            # style=styles.CONTENT_STYLE_OFF
        )],
        id='student_roster_page',
        style=styles.CONTENT_STYLE_OFF
    )

    return content_roster

def roster_builder(students_dict):
    roster = [dbc.Row([
                dbc.Col(
                    daq.ToggleSwitch(id=f'{x}', color='#4682b4', value=True),
                    width={'size': 4, 'offset': 0, 'align':'start'},
                ),
                dbc.Col(
                    html.P(f'{x}'),
                    width={'size': 4, 'offset': 0, 'justify':'start'},
                )
            ]) for x in students_dict]
    return roster

def content_table_component():
    content_table = html.Div(
        id="page-content_three",
        style=styles.CONTENT_STYLE_OFF
    )
    return content_table




