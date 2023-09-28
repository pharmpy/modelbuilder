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

def allometry_callbacks(app):
    @app.callback(
        Output("allometry_dropdown", "options"), Output("allo_variable", "options"),
        Input("all-tabs", "value"),
        prevent_initial_call = True
    )

    def give_options(tab):
        if tab == "allometry-tab":
            try: BW = config.model.datainfo.descriptorix["body weight"].names
            except: BW = []
            try: LBM = config.model.datainfo.descriptorix["lean body mass"].names
            except: LBM = []
            try: FFM = config.model.datainfo.descriptorix["fat free mass"].names
            except: FFM = []

            weights = BW + LBM + FFM
            clearance = find_clearance_parameters(config.model)
            volume = find_volume_parameters(config.model)
            clearance_volume = clearance + volume
            parameters = [str(x) for x in clearance_volume]
            return parameters, weights
        else: return [], []

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Output("allo_custom", "invalid"),
        Input("allo_btn", "n_clicks"),
        State("allo_variable", "value"),
        State("allo_custom", "value"), 
        State("allo_ref_val", "value"),
        State("allometry_dropdown", "value"),
        State("allo_inits", "value"),
        State("allo_lower", "value"),
        State("allo_upper", "value"),
        State("allo_fix", "value"),
        prevent_initial_call=True
    )    

    def create_allometry(clicked, variable, custom, ref_val, params, inits, lower, upper, fix):
        pattern = True
        if custom in config.model.datainfo.names:
            pattern = False

        inputs = [ref_val, params, inits, lower, upper, fix]

        if variable is not None:
            variables = list(variable)
        else: variables = []
        if pattern is False:
            variables.append(custom)
        standard_values = { "ref_val" : 70, "params": None, 
                            "inits" : None, "lower":None,
                            "upper":None, "fix":True   }
        for key, value in zip(standard_values.keys(), inputs):
            if value is not None:
                if key in ["ref_val", "params", "fix"]:
                    standard_values[key] = value
                else:
                    standard_values[key] = json.loads("[" + value + "]")

        if clicked:
            try:
                for variable in variables:
                    config.model = add_allometry(
                        config.model, variable, reference_value=standard_values["ref_val"], 
                        parameters=standard_values["params"], initials=standard_values["inits"], 
                        lower_bounds=standard_values["lower"],
                        upper_bounds=standard_values["upper"], fixed=standard_values["fix"] )
            except: pass
            return True, pattern
        else: raise PreventUpdate
    return