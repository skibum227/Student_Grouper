import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html, dcc

import templates.styles as styles

# This is only for the side bar
def sidebar_component(name, subtitle):
    sidebar = html.Div([
        dbc.Row(
            dbc.Col(
                html.H2(name, className="display-4", style={'text-align':'center'}),
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
                html.P(f'- {subtitle} -', className="lead", style={'text-align':'center', 'font-size':30}),
                width={'size': 12, 'offset': 0},
            ),
        ),
        dbc.Row(
            dbc.Col(
                html.Hr(),
                width={'size': 12, 'offset': 0}
            ),
        ),
        dbc.Nav([
                dbc.NavLink("Grouping Parameters", href="/", active="exact", style={"font-size":20}),
                dbc.NavLink("Update Roster", href="/roster", active="exact", style={"font-size":20}),
                dbc.NavLink("Student Groups", href="/groups", active="exact", style={"font-size":20}),
            ],
            vertical=True,
            pills=True,
        )],
        style=styles.SIDEBAR_STYLE,
        id='sidebar_content'
    )
    return sidebar


def content_params_component(periods):
    content_params = html.Div([
        dbc.Row(
            dbc.Col(
                html.Div(
                    html.H3("Select Class Period", className="display-7"),
                ),
                width={"size": 10, "offset": 0},
                style={"color":"#d3d3d3"}
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
                        {"label":f"Period {x.split('_')[1]}", "value":x} # +2 b/c periods start at 2
                    for i, x in enumerate(periods)],
                    value=periods[0],
                ),
                width={'size': 10, 'offset': 0}
            ),
        ),
        html.Br(),
        dbc.Row(
            dbc.Col(
                html.Hr(),
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    html.H3("Select Group Size", className="display-7"),
                ),
                width={"size": 10, "offset": 0},
                style={"color":"#d3d3d3"}
            )
        ),
        dbc.Row(
            dbc.Col(
                dbc.RadioItems(
                    id="group_size",
                    options=[ {"label": f"{x}" , "value": x} for x in range(2,11)],
                    value=3,
                    inline=True,
                 ),
                width={"size": 10, "offset": 0}
            )
        ),
        html.Br(),
        dbc.Row(
            dbc.Col(
                html.Hr(),
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(
                    html.H3("Distribute Non-Complete Groups", className="display-7"),
                ),
                width={"size": 10, "offset": 0},
                style={"color":"#d3d3d3"}
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
                    value=0,
                ),
        )], 
        id="parameters_page",
        style=styles.CONTENT_STYLE_ON
    )
    return content_params

def content_roster_component(student_roster_list):
    content_roster = html.Div([
        dbc.Row(
            dbc.Col(
                html.Div(
                    html.H3("Update Student Attendence", className="display-7"),
                ),
                style={"color":"#d3d3d3"},
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Hr(),
            )
        ),
        html.Br(),
        html.Div(
            roster_builder(student_roster_list),
            id="student_roster"
        )],
        id='student_roster_page',
        style=styles.CONTENT_STYLE_OFF
    )

    return content_roster

def roster_builder(student_roster_list):
    roster = [dbc.Row([
                dbc.Col(
                    daq.BooleanSwitch(id=f"{x}", color="#4682b4", on=True),
                    width={"offset": 0, "align":"start"},
                ),
                dbc.Col(
                    html.P(f"{x}"),
                    width={"offset": 0, "justify":"start"},
                )
            ]) for x in student_roster_list]
    return roster

def content_table_component():
    content_table = html.Div([
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H3("Student Groups Table", className="display-7"),
                    ],
                ),
                style={"color":"#d3d3d3"},
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Hr(),
            )
        ),
        html.Div(
            id="grouper_table"
        )],
        id="grouper_table_page",
        style=styles.CONTENT_STYLE_OFF
    )
    return content_table
