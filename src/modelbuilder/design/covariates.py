from .style_elements import (
    create_button,
    create_col,
    create_col_dict,
    create_container,
    create_dropdown,
    create_empty_line,
    create_header,
    create_options_dict,
    create_table,
    create_text_component,
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
    help_text = "Select rows to add covariates to the model. Click on 'Add row' to add more covariates to the table."
    help_text_component = create_text_component('cov_help_text', help_text)
    error_message_component = create_text_component('error_message', '', style={'color': 'red'})

    return create_col([help_text_component, line, cov_table, line, error_message_component, line])


def create_cov_button():
    add_btn = create_button('cov_btn', 'Add row')
    return create_col([add_btn])


cov_table = create_cov_table()
cov_header = create_header('Covariates')
cov_btn = create_cov_button()

covariate_tab = create_container(([cov_header], [cov_table], [cov_btn]))
