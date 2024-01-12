import dash_bootstrap_components as dbc
from dash import dash_table, html

from .style_elements import create_badge

iov_table = dash_table.DataTable(
    id='iov_table',
    columns=[
        {'name': 'Parameter', 'id': 'parameter'},
        {'name': 'Occasion column', 'id': 'occasion', 'presentation': 'dropdown'},
        {'name': 'ETA name', 'id': 'eta_names'},
        {'name': 'Distribution', 'id': 'distribution', 'presentation': 'dropdown'},
    ],
    dropdown={
        'occasion': {'options': []},
        'distribution': {'options': []},
    },
    editable=True,
    row_selectable='multi',
)

iiv_table = dash_table.DataTable(
    id='iiv_table',
    columns=[
        {
            'name': 'Parameter',
            'id': 'parameter',
        },
        {'name': 'Expression', 'id': 'expression', 'presentation': 'dropdown'},
        {'name': 'Custom', 'id': 'custom'},
        {'name': 'Operation', 'id': 'operation', 'presentation': 'dropdown'},
        {
            'name': 'Initial estimate',
            'id': 'initial_estimate',
        },
        {'name': 'ETA Name', 'id': 'eta_names'},
    ],
    dropdown={
        'expression': {
            'options': [
                {'label': 'Additive', 'value': 'add'},
                {'label': 'Proportional', 'value': 'prop'},
                {'label': 'Exponential', 'value': 'exp'},
                {'label': 'Logit', 'value': 'log'},
                {'label': 'Custom', 'value': 'custom'},
            ]
        },
        'operation': {
            'options': [
                {'label': '+', 'value': '+'},
                {'label': '*', 'value': '*'},
            ]
        },
    },
    editable=True,
    row_selectable='multi',
)

covariance_matrix = dash_table.DataTable(id="covariance_matrix")

par_var_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        create_badge("IIVs"),
                        iiv_table,
                    ]
                )
            ]
        ),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        create_badge("IOVs"),
                        iov_table,
                    ]
                )
            ]
        ),
        html.Br(),
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        create_badge("Covariance matrix"),
                        covariance_matrix,
                    ]
                )
            ]
        ),
    ]
)
