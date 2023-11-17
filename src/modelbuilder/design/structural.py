from .style_elements import create_badge

from dash import html, dcc
import dash_bootstrap_components as dbc

# ABSORPTION

absorptionoptions = [
    {"label": "Rate", "value": "Rate"},
    {"label": "Delay", "value": "Delay"},
]

absorptionrates = [
    {"label": "Zero order", "value": "ZO", "disabled": "False"},
    {"label": "First order", "value": "FO", "disabled": "False"},
    {"label": "Sequential ZO FO", "value": "seq_ZO_FO", "disabled": "False"},
]

abs_rates_radio = dbc.Col(
    children=[
        create_badge("Absorption rate"),
        dcc.RadioItems(options=absorptionrates, id="abs_rate-radio", style={"font-size": "large"}),
    ]
)

# Elimination rate

elimination_rates = [
    {"label": "First order", "value": "FO"},
    {"label": "Michaelis-Menten", "value": "MM"},
    {"label": "Mixed MM FO", "value": "mixed_MM_FO"},
    {"label": "Zero order", "value": "ZO"},
]

elimination_radio = dbc.Col(
    children=[
        create_badge("Elimination rate"),
        dcc.RadioItems(elimination_rates, id="elim_radio", style={"font-size": "large"}),
    ],
)

# Absorption delay

lag_toggle = html.Div(
    [
        dbc.Checklist(
            options=[
                {"label": "Lag time", "value": True, "disabled": False},
            ],
            id="lag-toggle",
            value=[],
        )
    ],
)

transits = dbc.InputGroup(
    children=[
        dbc.InputGroupText("Transit compartments"),
        dbc.Input(id="transit_input", placeholder=0, type="number", min=0, step=1),
    ],
    style={"width": "70%"},
)

bioavailability_toggle = html.Div(
    [
        dbc.Checklist(
            options=[{"label": "Bioavailability", "value": 1}],
            value=[],
            id="bio_toggle",
        )
    ]
)

# Distribution

peripheral_compartments = [
    {"label": "0", "value": 0},
    {"label": "1", "value": 1},
    {"label": "2", "value": 2},
]

peripherals_radio = dbc.Col(
    children=[
        create_badge("Peripheral compartments"),
        dcc.RadioItems(
            peripheral_compartments, id="peripheral-radio", style={"font-size": "large"}
        ),
    ],
    style={"width": "70%"},
)

# Full tab

structural_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        abs_rates_radio,
                    ]
                ),
                dbc.Col(elimination_radio),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        create_badge("Absorption delay"),
                        transits,
                        lag_toggle,
                        bioavailability_toggle,
                    ],
                    style={"padding-top": "2em"},
                ),
                dbc.Col(children=[peripherals_radio], style={"padding-top": "2em"}),
            ]
        ),
    ]
)
