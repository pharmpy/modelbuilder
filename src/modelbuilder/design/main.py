import dash_bootstrap_components as dbc
from dash import dcc, html

from .covariates import covariate_tab
from .datainfo import datainfo_tab
from .error_model import error_tab
from .general import general_tab
from .model_view import model_format_div
from .parameter_variability import par_var_tab
from .parameters import parameter_tab
from .structural import structural_tab
from .covariates import covariate_tab

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

background_color = '#0f8282'
border_color = '#0f8282'
tab_style = {
    'borderTop': f'1px solid {border_color}',
    'borderBottom': f'1px solid {border_color}',
    'borderLeft': f'1px solid {border_color}',
    'borderRight': f'1px solid {border_color}',
    'backgroundColor': background_color,
    'color': 'white',
}
border_color = 'white'
tab_selected_style = {
    'borderTop': f'1px solid {border_color}',
    'borderLeft': f'1px solid {border_color}',
    'borderRight': f'1px solid {border_color}',
    'backgroundColor': 'white',
    'color': 'black',
}

all_tabs = (
    html.Div(
        dcc.Tabs(
            id="all-tabs",
            value='general-tab',
            children=[
                dcc.Tab(
                    label="General",
                    value='general-tab',
                    children=general_tab,
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label="Structural",
                    value='structural-tab',
                    children=structural_tab,
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label='Parameter Variability',
                    value='par-var-tab',
                    children=par_var_tab,
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label="Error model",
                    value="error-tab",
                    children=error_tab,
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label="Covariates",
                    value="covariate-tab",
                    children=covariate_tab,
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label='Parameters',
                    value='parameters-tab',
                    children=parameter_tab,
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
            ],
            className='nav-link active',
        )
    ),
    html.Div(id='tab-content', children=[]),
)


layout = dbc.Container(
    [
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
