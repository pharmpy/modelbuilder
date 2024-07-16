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
    create_text_component,
)


def create_iov_params_component():
    iov_params_label_dict = {}
    iov_params_badge = create_badge("Parameters")
    params_text = 'Select parameters to add to table:'
    params_text_component = create_text_component('params_text_id', params_text)
    iov_params_options = create_options_list(iov_params_label_dict)
    iov_params_radio = create_checklist('iov_params_checklist', options=iov_params_options)
    return create_col([params_text_component, iov_params_radio, create_empty_line()])


def create_iov_button():
    add_btn = create_button('iov_add_button', 'Add to table')
    return create_col([add_btn, create_empty_line(), create_empty_line()])


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
        fill_width=False,
    )

    help_text = 'Select rows in the table to add IOVs to the model:'
    help_text_component = create_text_component('help_text_id', help_text)

    return create_col([help_text_component, iov_table])


def create_iov_error_message():
    error_text = ""
    error_text_component = create_text_component('dataset_text', error_text, style={'color': 'red'})
    return create_col([create_empty_line(), error_text_component, create_empty_line()])


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
iiv_header = create_header('IIV')
iov_header = create_header('IOV')
iov_error_message = create_iov_error_message()

par_var_tab = create_container(
    (
        [iiv_header],
        [iiv_table],
        [iov_header],
        [iov_checkbox],
        [iov_button],
        [iov_table],
        [iov_error_message],
    )
)
