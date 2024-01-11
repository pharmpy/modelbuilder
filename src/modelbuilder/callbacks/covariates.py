from dash import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import config
from config import make_label_value
from pharmpy.modeling import *


def covariate_callbacks(app):
    @app.callback(
        [Output("covar-param-name", "options")],
        [Output("covar-name", "options")],
        [Output("covar_div", "children", allow_duplicate=True)],
        Input("all-tabs", "value"),
        prevent_initial_call=True,
    )
    def get_params_covars(tab):
        def param_expression(parameter):
            return [
                parameter + ": ",
                str(config.model.statements.before_odes.full_expression(parameter)),
            ]

        if tab == "covariate-tab":
            try:
                covar_names = (
                    get_model_covariates(config.model, strings=True)
                    if get_model_covariates(config.model, strings=True)
                    else config.model.datainfo.typeix["unknown"].names
                )
                covar_opt = [make_label_value(covar, covar) for covar in covar_names]
                param_opt = [
                    make_label_value(param, param)
                    for param in get_individual_parameters(config.model)
                ]
                render = dbc.ListGroup(
                    children=[
                        dbc.ListGroupItem(param_expression(item))
                        for item in get_individual_parameters(config.model)
                    ]
                )

                return param_opt, covar_opt, render
            except:
                raise PreventUpdate
        else:
            return (
                [{"label": "No Options", "value": True}],
                [{"label": "No Options", "value": True}],
                "No covariates found",
            )

    @app.callback(
        Output("covar_div", "children", allow_duplicate=True),
        Output("covar-btn", "n_clicks"),
        Input("covar-param-name", "value"),
        Input("covar-name", "value"),
        Input("covariate-effect", "value"),
        State("covar-custom-eff", "value"),
        Input("covar-operation", "value"),
        Input("covar-allow-nestle", "value"),
        Input("covar-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def create_covariate(parameter, covariate, effect, custom, operation, nestle, button):
        try:

            def param_expression(parameter):
                return [
                    parameter + ": ",
                    str(config.model.statements.before_odes.full_expression(parameter)),
                ]

            if button:
                if custom:
                    config.model = add_covariate_effect(
                        config.model,
                        parameter,
                        covariate,
                        custom,
                        operation=operation,
                        allow_nested=nestle == "True",
                    )
                config.model = add_covariate_effect(
                    config.model,
                    parameter,
                    covariate,
                    effect,
                    operation=operation,
                    allow_nested=nestle == "True",
                )
                return (
                    dbc.ListGroup(
                        children=[
                            dbc.ListGroupItem(param_expression(item))
                            for item in get_individual_parameters(config.model)
                        ]
                    ),
                    0,
                )
            return (
                dbc.ListGroup(
                    children=[
                        dbc.ListGroupItem(param_expression(item))
                        for item in get_individual_parameters(
                            config.model,
                        )
                    ]
                ),
                0,
            )
        except:
            raise PreventUpdate

    return
