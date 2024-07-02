import dash_bootstrap_components as dbc
from dash import dash_table, html
from .style_elements import (
    create_table,
    create_dropdown,
    create_container,
    create_col_dict,
    create_options_list,
    create_options_dict,
    create_button,
    create_badge,
    create_col,
    create_checklist,
    create_dropdown_component,
    create_radio,
    create_empty_line,
    create_header,
)


def create_cov_table():
    columns = [
        create_col_dict('Parameter', 'parameter', presentation='dropdown'),
        create_col_dict('Covariate', 'covariate', presentation='dropdown'),
        create_col_dict('Effect', 'effect', presentation='dropdown'),
        create_col_dict('Operation', 'operation', presentation='dropdown'),
    ]

    dropdown = create_dropdown(
        ['parameter', 'covariate', 'effect', 'operation'],
        [
            create_options_dict({'CL': 'CL'}),
            create_options_dict({}),
            create_options_dict(
                {'lin': 'lin', 'cat': 'cat', 'cat2': 'cat2', 'exp': 'exp'},
                clearable=False,
            ),
            create_options_dict(
                {'+': '+', '*': '*'},
                clearable=False,
            ),
        ],
    )

    cov_table = create_table(
        'cov_table',
        columns,
        dropdown=dropdown,
        row_selectable='multi',
        row_deletable=True,
        selected_rows=[],
        fill_width=False,
    )

    line = create_empty_line()
    return create_col([cov_table, line, html.Div(id='error_message'), line])


def create_cov_button():
    add_btn = create_button('cov_btn', 'Add row')
    return create_col([add_btn])


cov_table = create_cov_table()
cov_header = create_header('Covariates')
cov_btn = create_cov_button()

covariate_tab = create_container(([cov_header], [cov_table], [cov_btn]))
