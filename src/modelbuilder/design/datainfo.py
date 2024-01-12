import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

from .style_elements import btn_color

cols = [
    {
        'name': 'name',
        'id': 'name',
    },
    {'name': 'type', 'id': 'type', 'presentation': 'dropdown'},
    {'name': 'scale', 'id': 'scale', 'presentation': 'dropdown'},
    {'name': 'continuous', 'id': 'continuous', 'presentation': 'dropdown'},
    {'name': 'categories', 'id': 'categories', 'presentation': 'dropdown'},
    {'name': 'unit', 'id': 'unit', 'presentation': 'dropdown'},
    {'name': 'datatype', 'id': 'datatype', 'presentation': 'dropdown'},
    {'name': 'drop', 'id': 'drop', 'presentation': 'dropdown'},
    {'name': 'descriptor', 'id': 'descriptor', 'presentation': 'dropdown'},
]

dd = {
    'type': {
        'options': [
            {'label': "id", 'value': "id"},
            {'label': "dv", 'value': "dv"},
            {'label': "idv", 'value': "idv"},
            {'label': "unknown", 'value': "unknown"},
            {'label': "dose", 'value': "dose"},
            {'label': "ii", 'value': "ii"},
            {'label': "ss", 'value': "ss"},
            {'label': "event", 'value': "event"},
            {'label': "covariate", 'value': "covariate"},
            {'label': "mdv", 'value': "mdv"},
            {'label': "nmtran_date", 'value': "nmtran_date"},
        ]
    },
    'scale': {
        'options': [
            {'label': "nominal", 'value': "nominal"},
            {'label': "ordinal", 'value': "ordinal"},
            {'label': "interval", 'value': "interval"},
            {'label': "ratio", 'value': "ratio"},
        ]
    },
    'continuous': {
        'options': [{'label': 'continuous', 'value': True}, {'label': 'discrete', 'value': False}]
    },
    'unit': {
        'options': [
            {'label': "1", 'value': 1},
            {'label': "ml", 'value': "ml"},
            {'label': "mg", 'value': "mg"},
            {'label': "h", 'value': "h"},
            {'label': "kg", 'value': "kg"},
            {'label': "mg/l", 'value': "mg/l"},
        ]
    },
    'datatype': {
        'options': [
            {'label': "int8", 'value': "int8"},
            {'label': "int16", 'value': "int16"},
            {'label': "int32", 'value': "int32"},
            {'label': "int64", 'value': "int64"},
            {'label': "uint8", 'value': "uint8"},
            {'label': "uint16", 'value': "uint16"},
            {'label': "uint32", 'value': "uint32"},
            {'label': "uint64", 'value': "uint64"},
            {'label': "float16", 'value': "float16"},
            {'label': "float32", 'value': "float32"},
            {'label': "float64", 'value': "float64"},
            {'label': "float128", 'value': "float128"},
            {'label': "nmtran-time", 'value': "nmtran-time"},
            {'label': "nmtran-date", 'value': "nmtran-date"},
        ]
    },
    'drop': {'options': [{'label': 'True', 'value': True}, {'label': 'False', 'value': False}]},
    'descriptor': {
        'options': [
            {'label': 'age', 'value': 'age'},
            {'label': 'body weight', 'value': 'body weight'},
            {'label': 'lean body mass', 'value': 'lean body mass'},
            {'label': 'fat free mass', 'value': 'fat free mass'},
        ]
    },
}

dataset = html.Div(
    children=[
        dbc.InputGroup(
            [
                dcc.Upload(dbc.Button('Select dataset', color=btn_color), id="upload-dataset"),
                dbc.Input(id="dataset-path", placeholder="No Dataset", type="text", disabled=True),
            ],
            style={"width": "50%"},
        )
    ]
)

datainfo_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row([dbc.Col(dataset)], style={}),
        html.Br(),
        dash_table.DataTable(
            id="datatable",
            columns=cols,
            editable=True,
            dropdown=dd,
        ),
        dbc.Container(
            [
                dbc.Button("Save DataInfo", id="makedatainf", n_clicks=0, color=btn_color),
                dcc.Download("download_dtainf"),
            ]
        ),
    ]
)
