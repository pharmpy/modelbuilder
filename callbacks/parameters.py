from dash import Dash, html, dcc,  callback, Output, Input, State, dash_table
from dash.exceptions import PreventUpdate
import config

from pharmpy.modeling import *
from pharmpy.model import *

import pandas as pd
import numpy as np
import base64
import json
import io
import time
import os

def parameter_callbacks(app):
        #Getting the model parameters
    @app.callback(
        Output("parameter-table", "data"), #allow_duplicate=True),
        Input("all-tabs", "value"),
    )

    def get_parameters(tab):
        if tab == "parameters-tab":
            parameters = config.model.parameters.to_dict()
            return parameters["parameters"]
        else:
            raise PreventUpdate


    @app.callback(
        Output("parameter-table", "data", allow_duplicate=True),
        Input("fix_all_toggle", "value"),
        prevent_initial_call = True

    )

    def fix_all_parameters(fixed):
        if fixed:
            names = config.model.parameters.names
            config.model = fix_parameters(config.model,names)
            parameters = config.model.parameters.to_dict()

        else:
            names = config.model.parameters.names
            config.model = unfix_parameters(config.model,names)
            parameters = config.model.parameters.to_dict()
        return parameters["parameters"]


    @app.callback(
            Output("data-dump", "clear_data", allow_duplicate=True),
            Input("parameter-table", "data"),
            prevent_initial_call = True
    )
    def visualise_data(data):
        def replace_empty(data):
                for item in data:
                    for key, value in item.items():
                        if value is None:
                            if key == "lower":
                                item[key] = float("-inf")
                            elif key == "upper":
                                item[key] = float("inf")
                return data
        data = replace_empty(data)
        current = config.model.parameters.to_dict()
        current["parameters"] = data
        config.model = config.model.replace(parameters=Parameters.from_dict(current))
        config.model = config.model.update_source()

        return True



    @app.callback(
        Output("parameter-table", "data", allow_duplicate=True),
        Output("pop-param-name", "value"),
        Output("pop-param-init", "value"),
        Output("pop-param-upper", "value"),
        Output("pop-param-lower", "value"),
        Output("pop-param-fix", "value"),
        Input("pop-param-btn", "n_clicks"),
        State("pop-param-name", "value"),
        State("pop-param-init", "value"),
        State("pop-param-upper", "value"),
        State("pop-param-lower", "value"),
        State("pop-param-fix", "value"),
        prevent_initial_call=True
    )

    def create_pop_param(n_clicks, name, init, upper,lower,fix):
        if n_clicks:
            if upper:
                upper = float(upper)
            if lower:
                lower = float(lower)
            config.model = add_population_parameter(config.model, name, float(init), lower, upper, fix == "True")
            parameters = config.model.parameters.to_dict()
            df = pd.DataFrame(parameters["parameters"])
            model_parameters = df.to_dict('records')
            return model_parameters, None, None, None, None, None
        else: raise PreventUpdate
    return
