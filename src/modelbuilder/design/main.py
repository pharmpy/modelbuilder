from .base import base_tab
from .covariates import covariate_tab
from .datainfo import datainfo_tab
from .error_model import error_tab
from .parameter_variability import par_var_tab
from .parameters import parameter_tab
from .structural import structural_tab
from .model_view import model_format_div

from dash import html, dcc
import dash_bootstrap_components as dbc


# Navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src="https://pharmpy.github.io/latest/_images/Pharmpy_logo.svg",
                                height="60px",
                            )
                        ),
                    ]
                ),
                href="https://pharmpy.github.io",
            ),
            dbc.Col(
                dbc.NavbarBrand(
                    "Model Builder",
                    className="ms-5",
                    style={"font-size": "25px", "font-weight": "bold"},
                )
            ),
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src="assets\github-mark.png", height="50px")),
                    ]
                ),
                href="https://github.com/pharmpy/modelbuilder",
            ),
        ],
        fluid=True,
    )
)

all_tabs = html.Div(
    dcc.Tabs(
        id="all-tabs",
        value='base-tab',
        children=[
            dcc.Tab(label="General", value='base-tab', children=base_tab),
            dcc.Tab(label="Dataset", value='data-info-tab', children=datainfo_tab),
            dcc.Tab(label="Structural", value='structural-tab', children=structural_tab),
            dcc.Tab(label='Parameters', value='parameters-tab', children=parameter_tab),
            dcc.Tab(label='Parameter variability', value='par-var-tab', children=par_var_tab),
            dcc.Tab(label="Error model", value="error-tab", children=error_tab),
            dcc.Tab(label="Covariates", value="covariate-tab", children=covariate_tab),
        ],
        className='nav-link active',
    )
), html.Div(id='tab-content', children=[])


layout = dbc.Container(
    [
        dcc.Store(id="data-dump"),
        navbar,
        dbc.Row(
            [dbc.Col(children=[model_format_div], width=4), dbc.Col(all_tabs, width=8)],
            style={
                'width': '100vw',
            },
        ),
    ],
    style={
        'height': '100vh',
        'width': '100vw',
        "margin-bottom": "0%",
    },
    fluid=True,
)
