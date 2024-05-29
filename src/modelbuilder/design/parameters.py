from .style_elements import (
    create_col_dict,
    create_container,
    create_dropdown,
    create_options_list,
    create_table,
    create_options_dict,
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

all_parameters_table = create_table('parameter-table', columns, dropdown=dropdown)

parameter_tab = create_container([all_parameters_table], className="mt-4")
