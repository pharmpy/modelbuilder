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


def create_iov_params_component():
    iov_params_label_dict = {}
    iov_params_badge = create_badge("Parameters")
    iov_params_options = create_options_list(iov_params_label_dict)
    iov_params_radio = create_checklist('iov_params_checklist', options=iov_params_options)
    return create_col([iov_params_badge, iov_params_radio])


def create_iov_button():
    add_btn = create_button('iov_add_button', 'Add')
    return create_col([add_btn, html.Div(id='dataset_text')])


def create_iov_table():
    columns = [
        create_col_dict('Parameters', 'list_of_parameters'),
        create_col_dict('Occasion column', 'occ', presentation='dropdown'),
        create_col_dict('Distribution', 'distribution', presentation='dropdown'),
    ]
    dropdown = create_dropdown(
        ['occasion', 'distribution'], [create_options_dict({}), create_options_dict({})]
    )

    iov_table = create_table(
        'iov_table',
        columns,
        dropdown=dropdown,
        row_selectable='multi',
        row_deletable=True,
        selected_rows=[],
    )

    return create_col([iov_table])


def create_iiv_table():
    columns = [
        create_col_dict('Parameter', 'list_of_parameters'),
        create_col_dict('Expression', 'expression', presentation='dropdown'),
    ]

    dropdown = create_dropdown(
        ['expression'],
        [
            create_options_dict(
                {'Additive': 'add', 'Proportional': 'prop', 'Exponential': 'exp', 'Logit': 'log'},
                clearable=False,
            ),
        ],
    )

    iiv_table = create_table(
        'iiv_table',
        columns,
        dropdown=dropdown,
        row_selectable='multi',
        row_deletable=True,
        selected_rows=[],
        fill_width=False,
    )
    return create_col([iiv_table, create_empty_line()])


iiv_table = create_iiv_table()
iov_checkbox = create_iov_params_component()
iov_button = create_iov_button()
iov_table = create_iov_table()
iiv_header = create_header('IIVs')
iov_header = create_header('IOVs')

par_var_tab = create_container(
    ([iiv_header], [iiv_table], [iov_header], [iov_checkbox, iov_button], [iov_table])
)
