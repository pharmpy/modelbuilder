import dash_bootstrap_components as dbc
from dash import html

from .style_elements import (
    create_badge,
    create_checklist,
    create_col,
    create_container,
    create_options_list,
    create_radio,
)


def create_base_type_component():
    base_type_label_dict = {
        'Additive': 'add',
        'Proportional': 'prop',
        'Combined': 'comb',
    }

    base_type_badge = create_badge("Base types")
    base_type_options = create_options_list(base_type_label_dict)
    base_type_radio = create_radio('base-type-radio', options=base_type_options)

    return create_col([base_type_badge, base_type_radio])


def create_additional_types_component():
    additional_types_label_dict = {
        'IIV on RUV': 'iiv-on-ruv',
        'Power': 'power',
        'Time varying': 'time-varying',
    }

    additional_types_badge = create_badge("Additional types")
    additional_types_options = create_options_list(additional_types_label_dict)
    additional_types_radio = create_checklist(
        'additional-types-checklist', options=additional_types_options
    )

    return create_col([additional_types_badge, additional_types_radio])


base_type_component = create_base_type_component()
additional_types_component = create_additional_types_component()

error_tab = create_container([[base_type_component, additional_types_component]])
