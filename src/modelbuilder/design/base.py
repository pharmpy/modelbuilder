from .style_elements import btn_color

from dash import html, dcc
import dash_bootstrap_components as dbc


typeoptions = [
    {"label": "PK", "value": "PK"},
]

model_type_radio = dbc.Col(
    children=[
        dbc.Badge("Model type", color="success", style={"font-size": "large"}),
        dcc.RadioItems(typeoptions, "PK", id="model_type", style={"font-size": "large"}),
    ]
)

collapsable_pk = dbc.Collapse(model_type_radio, id="collapse_pk", is_open=True)

model_name = html.Div(
    children=[
        dbc.InputGroup(
            [
                dbc.Badge("Name", color="success", style={"width": 150, 'fontSize': 'medium'}),
                dbc.Input(id="model-name", placeholder="Write model name here...", type="text"),
            ],
        )
    ],
)

model_description = html.Div(
    children=[
        dbc.InputGroup(
            [
                dbc.Badge(
                    "Description",
                    color="success",
                    style={
                        "width": 150,
                        'fontSize': 'medium',
                    },
                ),
                dbc.Input(
                    id="model-description",
                    placeholder="Write model description here...",
                    type="text",
                ),
            ],
            style={'marginTop': '5px'},
        ),
    ],
)

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

admin_route = [{"label": "IV", "value": "iv"}, {"label": "Oral", "value": "oral"}]

route_radio = dbc.Col(
    children=[
        dbc.Badge("Administration route", color="success", style={"font-size": "large"}),
        dcc.RadioItems(admin_route, value='iv', id="route-radio", style={"font-size": "large"}),
    ]
)

collapsable_route = dbc.Collapse(route_radio, id="collapse_route", is_open=True)


base_tab = dbc.Container(
    [
        dbc.Col(
            children=[
                html.Br(),
                html.P(
                    """Basic model operations. Set model name and description, upload dataset and select model type
                administration route."""
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            children=[model_name, model_description],
                            style={},
                        ),
                        dbc.Col(children=[], style={"height": "8vh"}),
                    ],
                    style={},
                ),
                dbc.Row([dbc.Col(dataset)], style={}),
                html.Br(),
                dbc.Row([dbc.Col(model_type_radio)], style={"height": "10vh"}),
                dbc.Row([dbc.Col(route_radio)], style={"height": "10vh"}),
            ]
        )
    ],
    style={
        "display": "flex",
    },
)
