from .style_elements import (
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

columns = [
    create_col_dict('Name', 'name', type='text'),
    create_col_dict('Init', 'init', type='numeric'),
    create_col_dict('Lower', 'lower', type='numeric'),
    create_col_dict('Upper', 'upper', type='numeric'),
    create_col_dict('Fix', 'fix', type='any', presentation='dropdown'),
]

dropdown = create_dropdown(
    ['fix'],
    [create_options_dict({'true': True, 'false': False}, clearable=False)],
)

help_text = "Please note that parameters will be reset if any model feature is changed."
help_text_component = create_text_component('param_help_text', help_text)

help_text = create_col([create_empty_line(), help_text_component])

all_parameters_table = create_table('parameter-table', columns, dropdown=dropdown)
header = create_header('Parameters')

parameter_tab = create_container([header, all_parameters_table, help_text], className="mt-4")
