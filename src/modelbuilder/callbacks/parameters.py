from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
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


def check_all_same(p):  # p = model_parameters_to_dict["parameters"])
    if p:
        ref = p[0]['fix']
        for parameter in p:
            if parameter['fix'] is not ref:
                return False
        return True


def parameter_callbacks(app):
    # Getting the model parameters
    @app.callback(
        Output("parameter-table", "data"),  # allow_duplicate=True),
        Output("custom_fix", "data", allow_duplicate=True),
        Input("all-tabs", "value"),
        prevent_initial_call=True,
    )
    def get_parameters(tab):
        if tab == "parameters-tab":
            parameters = config.model.parameters.to_dict()
            return parameters["parameters"], json.dumps(parameters["parameters"])
        else:
            raise PreventUpdate

    @app.callback(
        Output("parameter-table", "data", allow_duplicate=True),
        Input("unfix_btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def unfix_all(unfix_btn):
        if unfix_btn:
            names = config.model.parameters.names
            config.model = unfix_parameters(config.model, names)
            parameters = config.model.parameters.to_dict()
        return parameters["parameters"]

    @app.callback(
        Output("parameter-table", "data", allow_duplicate=True),
        Input("fix_all_btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def fix_all(fix_all_btn):
        if fix_all_btn:
            names = config.model.parameters.names
            config.model = fix_parameters(config.model, names)
            parameters = config.model.parameters.to_dict()
        return parameters["parameters"]

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("parameter-table", "data"),
        prevent_initial_call=True,
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
        Output("custom_fix", "data"),
        Input("parameter-table", "data"),
    )
    def save_state(data):
        if check_all_same(data):
            raise PreventUpdate
        else:
            data_json = json.dumps(data)
        return data_json

    @app.callback(
        Output("parameter-table", "data", allow_duplicate=True),
        Input("custom_fix_btn", "n_clicks"),
        State("custom_fix", "data"),
        prevent_initial_call=True,
    )
    def return_custom(custom_btn, stored_data):
        data = json.loads(stored_data)
        return data

    return
