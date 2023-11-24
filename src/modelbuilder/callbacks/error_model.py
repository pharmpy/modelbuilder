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

base_error_model_funcs = {
    "add": set_additive_error_model,
    "prop": set_proportional_error_model,
    "comb": set_combined_error_model,
}


def error_model_callbacks(app):
    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("base-type-radio", "value"),
        prevent_initial_call=True,
    )
    def update_base_error_model(base_error_model):
        if base_error_model:
            config.model = base_error_model_funcs[base_error_model](config.model)
            return True

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("base-type-radio", "value"),
        Input("iiv-on-ruv-toggle", "value"),
        Input("power-toggle", "value"),
        Input("time-varying-toggle", "value"),
        prevent_initial_call=True,
    )
    def set_additional_type(base_type, iiv_toggle, power_toggle, time_varying_toggle):
        if iiv_toggle:
            config.model = set_iiv_on_ruv(config.model)
            return True
        elif power_toggle:
            config.model = set_power_on_ruv(config.model)
            return True
        elif time_varying_toggle:
            config.model = set_time_varying_error_model(config.model, cutoff=1.0)
            return True
        else:
            config.model = remove_error_model(config.model)
            config.model = base_error_model_funcs[base_type](config.model)
            return True

    return
