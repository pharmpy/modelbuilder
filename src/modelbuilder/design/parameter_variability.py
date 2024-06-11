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
)


def create_iov_badge():
    iov_badge = create_badge("IOV")
    return create_col([iov_badge])


def create_iov_params_component():
    iov_params_label_dict = {}
    iov_params_badge = create_badge("Parameters")
    iov_params_options = create_options_list(iov_params_label_dict)
    iov_params_radio = create_checklist('iov_params_checklist', options=iov_params_options)
    return create_col([iov_params_badge, iov_params_radio])


def create_occ_dropdown():
    occ_badge = create_badge("Occasion")
    dropdown_options = create_dropdown(['occasion'], [])
    dropdown = create_dropdown_component('occ_dropdown', options=dropdown_options)
    return create_col([occ_badge, dropdown])


def create_iov_dist():
    iov_label_dict = {
        'Joint': 'joint',
        'Disjoint': 'disjoint',
        'Same as IIV': 'same-as-iiv',
    }

    iov_dist_badge = create_badge("Distribution")
    iov_dist_options = create_options_list(iov_label_dict)
    iov_dist_radio = create_radio('radio_iov_dist', options=iov_dist_options, value='disjoint')

    return create_col([iov_dist_badge, iov_dist_radio])


def create_iov_button():
    iov_add_button = create_button('iov_add_button', 'Add IOV')
    iov_remove_button = create_button('iov_remove_button', 'Remove all IOVs')
    return create_col([iov_add_button, iov_remove_button])


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
        'iiv_table', columns, dropdown=dropdown, row_selectable='multi', selected_rows=[]
    )
    iiv_badge = create_badge("IIVs")
    return create_col([iiv_badge, iiv_table])


iiv_table = create_iiv_table()
iov_checkbox = create_iov_params_component()
iov_dropdown = create_occ_dropdown()
iov_button = create_iov_button()
iov_dist = create_iov_dist()
iov_badge = create_iov_badge()

par_var_tab = create_container(
    ([iiv_table], [iov_badge], [iov_checkbox, iov_dropdown, iov_dist], [iov_button])
)
