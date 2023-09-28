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

def structural_callbacks(app):
    @app.callback(
            Output("data-dump", "clear_data",allow_duplicate=True),
            Input("abs_rate-radio", "value"),
            Input("elim_radio", "value"),
            prevent_initial_call=True
    )

    def update_abs_elim(abs, elim):
        if elim:
            elim_keys ={"FO": set_first_order_elimination(config.model),
                    "MM": set_michaelis_menten_elimination(config.model),
                    "mixed_MM_FO": set_mixed_mm_fo_elimination(config.model)
                    }
            
            config.model = elim_keys[elim]
            return True
        if abs:
            abs_keys ={"ZO": set_zero_order_absorption(config.model),
                    "FO": set_first_order_absorption(config.model),
                    "seq_ZO_FO": set_seq_zo_fo_absorption(config.model)
                    }
            config.model = abs_keys[abs]
            return True
        
    #Callback for disabeling absorption
    @app.callback(
            Output("abs_rate-radio", "options"),
            Output("abs_rate-radio", "value"),
            Input("route-radio", "value"),
            State("abs_rate-radio", "options"),
            State("abs_rate-radio", "value"),       
    )

    def disable_abs(value, options, rate):
        if value == "iv":
            return [{**dictionary, "disabled":True} for dictionary in options], 0
        else: 
            return [{**dictionary, "disabled":False} for dictionary in options], rate

    @app.callback(
        [Output("lag-toggle", "options"),
         Output("transit_input", "value"), 
         Output("transit_input", "disabled")],
        Input("lag-toggle", "value"),
        Input("transit_input", "value"),
        prevent_inital_call = True
)

    def toggle_disable(lag_tog, transit_input):
        
        if lag_tog:
            try:
                config.model = set_transit_compartments(config.model,0)
                config.model = add_lag_time(config.model)
                return [{"label": "Lag Time", "value" : True, "disabled":False}], None, True
            except:
                raise PreventUpdate

        if transit_input :
    
            try:
                config.model= remove_lag_time(config.model)
                if transit_input:
                    config.model = set_transit_compartments(config.model, int(transit_input))
                return [{"label": "Lag Time", "value" : False, "disabled":True}], int(transit_input), False
            except:

                raise PreventUpdate 
        else: 
            try:
                config.model= remove_lag_time(config.model)
                config.model = set_transit_compartments(config.model,0)
                return [{"label": "Lag Time", "value" : True, "disabled":False}], None, False
            except:
                return [{"label": "Lag Time", "value" : True, "disabled":False}], None, False
    
    
    #callback for peripheral compartments
    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("peripheral_input", "value"),
        prevent_initial_call = True
    )

    def peripheral_compartments(n):

        try:
            if n>0:
                globals()["peripherals"] = int(n)
                config.model = set_peripheral_compartments(config.model, int(n))
                return True
            else:
                while globals()["peripherals"] > 0:
                    config.model = remove_peripheral_compartment(config.model)
                    globals()["peripherals"] = globals()["peripherals"] - 1 
        except: return True

    @app.callback(
            Output("data-dump", "clear_data", allow_duplicate=True),
            Input("bio_toggle", "value"),
            prevent_initial_call = True
    )
    def set_bioavailability(toggle):
        if toggle:
            config.model = add_bioavailability(config.model)
            return True
        else:
            config.model = remove_bioavailability(config.model)
            return True    

    return