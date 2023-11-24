from .style_elements import create_badge

from dash import html, dcc
import dash_bootstrap_components as dbc

base_types = [
    {"label": "Additive", "value": "add"},
    {"label": "Proportional", "value": "prop"},
    {"label": "Combined", "value": "comb"},
]

pk_default = {"base-type-radio": "prop"}

id_elem = 'base-type-radio'
base_type_radio = dbc.Col(
    children=[
        create_badge("Base types"),
        dcc.RadioItems(
            options=base_types, value=pk_default[id_elem], id=id_elem, style={"font-size": "large"}
        ),
    ]
)


additional_types_toggle = html.Div(
    [
        dbc.Checklist(
            options=[{"label": "IIV on RUV", "value": True, "disabled": False}],
            value=[],
            id="iiv-on-ruv-toggle",
        ),
        dbc.Checklist(
            options=[{"label": "Power", "value": True, "disabled": False}],
            value=[],
            id="power-toggle",
        ),
        dbc.Checklist(
            options=[{"label": "Time varying", "value": True, "disabled": False}],
            value=[],
            id="time-varying-toggle",
        ),
    ]
)

additional_types_col = dbc.Col(
    children=[
        create_badge("Additional types"),
        additional_types_toggle,
    ]
)


error_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                base_type_radio,
                additional_types_col,
            ]
        ),
    ]
)
