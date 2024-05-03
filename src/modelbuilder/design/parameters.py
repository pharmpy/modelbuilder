from .style_elements import create_table, create_dropdown, create_container

columns = [
    {'name': 'Name', 'id': 'name', 'type': 'text'},
    {'name': 'Init', 'id': 'init', 'type': 'numeric'},
    {'name': 'Lower', 'id': 'lower', 'type': 'numeric'},
    {'name': 'Upper', 'id': 'upper', 'type': 'numeric'},
    {'name': 'Fix', 'id': 'fix', 'type': 'any', 'presentation': 'dropdown'},
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
