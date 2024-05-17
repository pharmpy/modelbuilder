from .style_elements import (
    create_col_dict,
    create_container,
    create_dropdown,
    create_options_list,
    create_table,
)

columns = [
    create_col_dict('Name', 'name', 'text'),
    create_col_dict('Init', 'init', 'numeric'),
    create_col_dict('Lower', 'lower', 'numeric'),
    create_col_dict('Upper', 'upper', 'numeric'),
    create_col_dict('Fix', 'fix', 'any', presentation='dropdown'),
]

dropdown = create_dropdown(
    ['fix'],
    [
        {
            'options': [{'label': 'true', 'value': True}, {'label': 'false', 'value': False}],
            'clearable': False,
        },
    ],
)

all_parameters_table = create_table('parameter-table', columns, dropdown=dropdown)

parameter_tab = create_container([all_parameters_table], className="mt-4")
