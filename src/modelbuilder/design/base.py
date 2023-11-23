from .style_elements import btn_color, create_badge

from dash import html, dcc
import dash_bootstrap_components as dbc


typeoptions = [
    {"label": "PK", "value": "PK"},
]

model_type_radio = dbc.Col(
    children=[
        create_badge("Model type"),
        dcc.RadioItems(typeoptions, "PK", id="model_type", style={"font-size": "large"}),
    ]
)

collapsable_pk = dbc.Collapse(model_type_radio, id="collapse_pk", is_open=True)

model_name = html.Div(
    children=[
        dbc.InputGroup(
            [
                create_badge("Name", with_textbox=True),
                dbc.Input(id="model-name", placeholder="Write model name here...", type="text"),
            ],
        )
    ],
)

model_description = html.Div(
    children=[
        dbc.InputGroup(
            [
                create_badge("Description", with_textbox=True),
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

admin_route = [{"label": "IV", "value": "iv"}, {"label": "Oral", "value": "oral"}]

route_radio = dbc.Col(
    children=[
        create_badge("Administration route"),
        dcc.RadioItems(admin_route, value='iv', id="route-radio", style={"font-size": "large"}),
    ]
)

collapsable_route = dbc.Collapse(route_radio, id="collapse_route", is_open=True)


base_tab = dbc.Container(
    [
        dbc.Col(
            children=[
                html.Br(),
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
