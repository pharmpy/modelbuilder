import dash_bootstrap_components as dbc
from dash import dash_table, html
from .style_elements import (
    create_table,
    create_dropdown,
    create_container,
    create_col_dict,
    create_options_list,
    create_options_dict,
)

from .style_elements import create_badge

columns = [
    create_col_dict('Parameter', 'list_of_parameters'),
    create_col_dict('Occasion column', 'occ', presentation='dropdown'),
    create_col_dict('ETA name', 'eta_names'),
    create_col_dict('Distribution', 'distribution', presentation='dropdown'),
]

dropdown = {
    'occasion': {'options': []},
    'distribution': {'options': []},
}

iov_table = create_table(
    'iov_table', columns, dropdown=dropdown, row_selectable='multi', selected_rows=[]
)

columns = [
    create_col_dict('Parameter', 'list_of_parameters'),
    create_col_dict('Expression', 'expression', presentation='dropdown'),
    create_col_dict('Operation', 'operation', presentation='dropdown'),
    create_col_dict('Initial estimate', 'initial_estimate'),
    create_col_dict('ETA name', 'eta_names'),
]

dropdown = create_dropdown(
    ['expression', 'operation'],
    [
        create_options_dict(
            {'Additive': 'add', 'Proportional': 'prop', 'Exponential': 'exp', 'Logit': 'log'},
            clearable=False,
        ),
        create_options_dict({'*': '*', '+': '+'}, clearable=False),
    ],
)

iiv_table = create_table(
    'iiv_table', columns, dropdown=dropdown, row_selectable='multi', selected_rows=[]
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
