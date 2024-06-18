import dash_bootstrap_components as dbc
from dash import html

from .style_elements import (
    create_badge,
    create_checklist,
    create_col,
    create_container,
    create_options_list,
    create_radio,
    create_empty_line,
    create_header,
)


def create_base_type_component():
    base_type_label_dict = {
        'Additive': 'add',
        'Proportional': 'prop',
        'Combined': 'comb',
    }
    base_type_label_dict_dv2 = {
        'Additive': 'add',
        'Proportional': 'prop',
    }

    dv1_badge = create_badge('DVID = 1')
    line = create_empty_line()

    base_type_options = create_options_list(base_type_label_dict)
    base_type_radio = create_radio('base-type-radio', options=base_type_options, value='prop')

    dv2_badge = create_badge('DVID = 2')
    base_type_options_dv2 = create_options_list(base_type_label_dict_dv2)
    base_type_options_dv2.append(create_options_list({'Combined': 'combined'}, disabled=True)[0])
    base_type_radio_2 = create_radio('base-type-radio-dv2', options=base_type_options_dv2)

    return create_col([dv1_badge, base_type_radio, line, dv2_badge, base_type_radio_2])


def create_additional_types_component():
    additional_types_label_dict = {
        'Power': 'power',
        'IIV on RUV': 'iiv-on-ruv',
        'Time varying': 'time-varying',
    }

    dv1_badge = create_badge('DVID = 1')
    dv2_badge = create_badge('DVID = 2')
    line = create_empty_line()
    additional_types_options = create_options_list(additional_types_label_dict)
    additional_types_radio = create_checklist(
        'additional-types-checklist', options=additional_types_options
    )
    additional_types_radio_2 = create_checklist(
        'additional-types-checklist-dv2', options=additional_types_options
    )

    return create_col(
        [
            dv1_badge,
            additional_types_radio,
            line,
            dv2_badge,
            additional_types_radio_2,
        ]
    )


base_type_component = create_base_type_component()
additional_types_component = create_additional_types_component()
base_header = create_header('Base types')
add_types_header = create_header('Additional types')

error_tab = create_container(
    [[base_header, add_types_header], [base_type_component, additional_types_component]]
)
