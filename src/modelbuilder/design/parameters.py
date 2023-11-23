from .style_elements import btn_color

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

unfix_custom_false_btns = html.Div(
    children=[
        dbc.ButtonGroup(
            [
                dbc.Button("Unfix All", id="unfix_btn", color=btn_color),
                dbc.Button("Custom", id="custom_fix_btn", color=btn_color),
                dbc.Button("Fix All", id="fix_all_btn", color=btn_color),
            ]
        )
    ],
    style={"padding-right": "15px", "padding-top": "15px", "padding-bottom": "15px"},
)

all_parameters_table = dash_table.DataTable(
    id='parameter-table',
    columns=[
        {'name': 'Name', 'id': 'name', 'type': 'text'},
        {'name': 'Init', 'id': 'init', 'type': 'numeric'},
        {'name': 'Lower', 'id': 'lower', 'type': 'numeric'},
        {'name': 'Upper', 'id': 'upper', 'type': 'numeric'},
        {'name': 'Fix', 'id': 'fix', 'type': 'any', 'presentation': 'dropdown'},
    ],
    editable=True,
    row_deletable=False,
    dropdown={
        'fix': {
            'options': [{'label': 'true', 'value': True}, {'label': 'false', 'value': False}],
            'clearable': False,
        }
    },
    style_data_conditional=[
        {
            'if': {'state': 'active'},
            'backgroundColor': 'rgba(0, 116, 217, 0.3)',
            'border': '1px solid rgb(0, 116, 217)',
        },
        {'if': {'column_type': 'numeric'}, 'textAlign': 'right'},
    ],
    style_cell={'textAlign': 'left'},
)

parameter_tab = dbc.Container(
    [
        dcc.Store(id="custom_fix"),
        unfix_custom_false_btns,
        all_parameters_table,
    ],
    className="mt-4",
)
