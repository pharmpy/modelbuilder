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

def error_model_callbacks(app):
    @app.callback(
    Output("error_div", "children", allow_duplicate=True),
    Output("comb_check", "value", allow_duplicate=True),
    Output("prop_check", "value", allow_duplicate=True),
    Input("add_check", "value"),
    State("comb_check", "value"),
    State("prop_check", "value"),
    prevent_initial_call=True
)

    def create_add_error(addcheck, comb, prop):
        if addcheck:
            config.model= remove_error_model(config.model)
   
            config.model= set_additive_error_model(config.model)
            return f'', False, False
        else:
            return f'', comb, prop 
    
  
    @app.callback(
        Output("error_div", "children", allow_duplicate=True),
        Output("add_check", "value", allow_duplicate=True),
        Output("prop_check", "value", allow_duplicate=True),
        Input("comb_check", "value"),
        State("add_check", "value"),
        State("prop_check", "value"),
        
        prevent_initial_call=True
        ) 

    def create_comb_error(check, add, prop):
        if check:
            config.model= remove_error_model(config.model)

            config.model= set_combined_error_model(config.model)
                
            return f'', False, False
        else:    
            return  f'', add, prop   

    @app.callback(
        Output("error_div", "children", allow_duplicate=True),
        Output("add_check", "value", allow_duplicate=True),
        Output("comb_check", "value", allow_duplicate=True),
        Input("prop_check", "value"),
        Input("prop_zero_prot", "value"),
        State("add_check", "value"),
        State("comb_check", "value"),
        prevent_initial_call=True
        ) 

    def create_prop_error(check, protection, add, comb):
        if check:
            config.model= remove_error_model(config.model)

            if protection == "False":
                protection = False
            else: protection = True
            config.model= set_proportional_error_model(
                config.model, zero_protection=protection)
                
            return f'', False, False
        else:
            return f'', add, comb

    @app.callback(
        Output("error_div", "children", allow_duplicate=True),
        Output("time_cutoff", "value"),
        Input("time_check", "value"),
        Input("time_cutoff", "value"),
        Input("data_idv", "value"),
        prevent_initial_call=True
        ) 

    def create_time_error(check, cutoff, idv):
        if check:
            if not cutoff or cutoff < 0:
                cutoff = 0
            if idv: 
                config.model= set_time_varying_error_model(config.model, cutoff=cutoff, idv = idv)
            else:
                config.model= set_time_varying_error_model(config.model, cutoff=cutoff,)
        return f'', cutoff    

    @app.callback(
        Output("error_div", "children", allow_duplicate=True),
        Input("wgt_check", "value"),
        prevent_initial_call = True
    )

    def create_wgt_error(check):
        if check:
            config.model = set_weighted_error_model(config.model)
        return f''
    return