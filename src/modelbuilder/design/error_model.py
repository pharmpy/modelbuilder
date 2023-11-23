from dash import html
import dash_bootstrap_components as dbc

error_multi_input = dbc.Container(
    [
        dbc.ListGroup(
            [
                dbc.ListGroupItem(
                    dbc.InputGroup(
                        children=[
                            dbc.Checkbox(
                                id="add_check",
                                label=dbc.Badge(
                                    "Additive",
                                    color="success",
                                    style={"width": 150, "font-size": "medium"},
                                ),
                                value=False,
                                style={"size": "md"},
                            ),
                        ]
                    )
                ),
                dbc.ListGroupItem(
                    dbc.InputGroup(
                        children=[
                            dbc.Checkbox(
                                id="comb_check",
                                label=dbc.Badge(
                                    "Combined",
                                    color="success",
                                    style={"width": 150, "font-size": "medium"},
                                ),
                                value=False,
                                style={"size": "md"},
                            ),
                        ]
                    ),
                ),
                dbc.ListGroupItem(
                    dbc.InputGroup(
                        children=[
                            dbc.Checkbox(
                                id="prop_check",
                                label=dbc.Badge(
                                    "Proportional",
                                    color="success",
                                    style={"width": 150, "font-size": "medium"},
                                ),
                                value=False,
                                style={"size": "md"},
                            ),
                            dbc.Input(
                                id="prop_zero_prot",
                                placeholder="zero_protection=True",
                            ),
                        ],
                        style={"width": "60%"},
                    ),
                ),
                dbc.ListGroupItem(
                    dbc.InputGroup(
                        children=[
                            dbc.Checkbox(
                                id="time_check",
                                label=dbc.Badge(
                                    "Time varying",
                                    color="success",
                                    style={"width": 150, "font-size": "medium"},
                                ),
                                style={"size": "md"},
                            ),
                            dbc.Input(
                                id="time_cutoff",
                                placeholder="cutoff",
                                style={"width": "33%"},
                                type="number",
                                min=0,
                            ),
                            dbc.Input(
                                id="data_idv", placeholder="idv='TIME'", style={"width": "33%"}
                            ),
                        ]
                    ),
                ),
                dbc.ListGroupItem(
                    dbc.InputGroup(
                        children=[
                            dbc.Checkbox(
                                id="wgt_check",
                                label=dbc.Badge(
                                    "Weighted",
                                    color="success",
                                    style={"width": 150, "font-size": "medium"},
                                ),
                                style={"size": "md"},
                            ),
                        ]
                    ),
                ),
            ]
        )
    ]
)

error_tab = dbc.Container(
    [
        dbc.Col(children=[html.Br(), error_multi_input, html.Div(id="error_div")]),
    ]
)
