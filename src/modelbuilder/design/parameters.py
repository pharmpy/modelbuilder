import dash_bootstrap_components as dbc
from dash import dash_table

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
    style_cell={'textAlign': 'left', 'width': '20%'},
)

parameter_tab = dbc.Container(
    [
        all_parameters_table,
    ],
    className="mt-4",
)
