import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html, dcc

import templates.styles as styles

# This is only for the side bar
def sidebar_builder(name, subtitle):
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


def content_params_builder(periods):
    content_params = html.Div([
        dbc.Row(
            dbc.Col(
                dbc.RadioItems(
                    id="input_period_1",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label":x, "value":x}
                    for i, x in enumerate(periods)],
                    value=periods[0],
                ),
                width={'size': 4, 'offset': 0}
            ),
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id='output_period_1'),
                width={'size': 4, 'offset': 0}
            )

        ),
        dbc.Row(
            dbc.Col(
                dbc.Input(id="input_cnt_1", placeholder="Number of Students in group", type="number", min=0, max=10, step=1),
                width={'size': 4, 'offset': 0}
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id='output_cnt_1'),
                width={'size': 4, 'offset': 0}
            )

        ),
        dbc.Row(
                dbc.RadioItems(
                    id="input_distrib_1",
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
        ),
        dbc.Row(
            dbc.Col(
                html.Div(id='output_distrib_1'),
                width={'size': 4, 'offset': 0}
            )
        )], 
        id="page-content_one",
        style=styles.CONTENT_STYLE_ON
    )
    return content_params

def content_roster_builder(student_names):
    content_roster = html.Div([
        (dbc.Row([
            dbc.Col(
                daq.ToggleSwitch(id=f'{x}', color='#4682b4', value=True),
                width={'size': 4, 'offset': 0, 'align':'start'},
            ),
            dbc.Col(
                html.P(f'{x}'),
                width={'size': 4, 'offset': 0, 'justify':'start'},
            )
        ]))
        for x in student_names ], id="page_content_two", style=styles.CONTENT_STYLE_OFF)
    return content_roster

def content_table_builder(fig):
    content_table = html.Div(#[
        # dbc.Row(
        #     dbc.Col(
        #         dcc.Input(id='input_three', value='test input three', type='text'),
        #         width={'size': 4, 'offset': 0}
        #     ),
        # ),
        # dbc.Row(
        #     dbc.Col(
        #         html.Div(id='output_three')
        #     )
        # )], 
        dcc.Graph(figure=fig),
        id="page-content_three",
        style=styles.CONTENT_STYLE_OFF
    )
    return content_table




