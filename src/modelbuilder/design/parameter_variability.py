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
    disable_component,
)


def create_iov_params_component():
    iov_params_label_dict = {}
    iov_params_badge = create_badge("IOV")
    iov_params_options = create_options_list(iov_params_label_dict)
    iov_params_radio = create_checklist('iov_params_checklist', options=iov_params_options)
    return create_col([iov_params_badge, iov_params_radio])


def create_iov_dropdown_component():
    columns_iov2 = [
        create_col_dict('Occasion column', 'occ', presentation='dropdown'),
        create_col_dict('Distribution', 'distribution', presentation='dropdown'),
    ]

    dropdown = create_dropdown(
        ['occasion', 'distribution'], [create_options_dict({}), create_options_dict({})]
    )

    iov_table_2 = create_table('iov_dropdown', columns_iov2, dropdown=dropdown)
    return create_col([iov_table_2])


def create_iov_button():
    iov_button = create_button('iov_button', 'Add IOV')
    return create_col([iov_button])


def create_iiv_table():
    columns = [
        create_col_dict('Parameter', 'list_of_parameters'),
        create_col_dict('Expression', 'expression', presentation='dropdown'),
    ]

    dropdown = create_dropdown(
        ['expression', 'correlation'],
        [
            create_options_dict(
                {'Additive': 'add', 'Proportional': 'prop', 'Exponential': 'exp', 'Logit': 'log'},
                clearable=False,
            ),
        ],
    )

    iiv_table = create_table(
        'iiv_table', columns, dropdown=dropdown, row_selectable='multi', selected_rows=[]
    )
    iiv_badge = create_badge("IIVs")
    return create_col([iiv_badge, iiv_table])


iiv_table = create_iiv_table()
iov_checkbox = create_iov_params_component()
iov_dropdown = create_iov_dropdown_component()
iov_button = create_iov_button()

par_var_tab = create_container(([iiv_table], [iov_checkbox], [iov_dropdown], [iov_button]))
