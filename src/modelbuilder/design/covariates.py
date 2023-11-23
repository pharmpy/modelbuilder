from .style_elements import btn_color, create_badge

from dash import html
import dash_bootstrap_components as dbc

covariate_effect = [
    {"label": "linear", "value": "lin"},
    {"label": "categorical", "value": "cat"},
    {"label": "piece linear", "value": "piece_lin"},
    {"label": "exponential", "value": "exp"},
    {"label": "power", "value": "pow"},
]

covariate_options = dbc.Container(
    [
        create_badge("Specify covariate"),
        dbc.InputGroup(
            id="covar",
            children=[
                dbc.Select(id="covar-param-name", placeholder="Parameter name"),
                dbc.Select(id="covar-name", placeholder="Covariate name"),
                dbc.Select(id="covariate-effect", options=covariate_effect, placeholder="Effect"),
                dbc.Input(id="covar-custom-eff", placeholder="Custom effect"),
                dbc.Select(
                    id="covar-operation",
                    options=[
                        {"label": "operation= +", "value": "+"},
                        {"label": "operation= *", "value": "*"},
                    ],
                    placeholder="operation, defeault *",
                ),
                dbc.Select(
                    id="covar-allow-nestle",
                    options=[
                        {"label": "allow-nestle=False", "value": "False"},
                        {"label": "allow-nestle=True", "value": "True"},
                    ],
                    placeholder="allow-nestle=False",
                ),
                dbc.Button("Add covariate", id="covar-btn", color=btn_color, n_clicks=0),
            ],
        ),
    ]
)

model_covariate_list = html.Div(id="covar_div")

covariate_tab = dbc.Container(
    [
        html.Br(),
        dbc.Row(covariate_options),
        html.Hr(),
        html.P("Covariates"),
        model_covariate_list,
    ]
)
