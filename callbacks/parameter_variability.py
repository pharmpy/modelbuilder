from dash import Dash, html, dcc,  callback, Output, Input, State, dash_table
from dash.exceptions import PreventUpdate
import config

from pharmpy.modeling import *
from pharmpy.model import *
from config import make_label_value

import pandas as pd
import numpy as np
import base64
import json
import io
import time
import os

def parameter_variability_callbacks(app):
    @app.callback(
            Output("iiv_table", "data"),
            Input('all-tabs', 'value'),
            prevent_initial_call = True
    )
    def render_iiv_iov_data(tab):
        if tab == "par-var-tab":
            parameter_names = get_individual_parameters(config.model)
            df = pd.DataFrame({'parameter':parameter_names, 'initial_estimate':0.09, 'operation':'*', 'eta_names':None})
            iiv_data = df.to_dict('records')
            return iiv_data
        else:
            raise PreventUpdate
    @app.callback(
                Output("iov_table","data"),
                Output("iov_table","dropdown"),
                Input('all-tabs', 'value'),
                prevent_initial_call = True
        )        

    def render_iov(tab):
        if tab == "par-var-tab":
            parameter_names = get_individual_parameters(config.model)
            iov_data = pd.DataFrame({'parameter': parameter_names, 'distribution':'disjoint', 'eta_names':None})
            iov_data = iov_data.to_dict('records')
            occ_opts = []
            if config.model.datainfo:
                try:
                    occ_opts = config.model.datainfo.typeix["idv"].names + config.model.datainfo.typeix["unknown"].names
                except:
                    occ_opts = config.model.datainfo.typeix["unknown"].names 

            iov_dd_options = {
                'occasion': {
                    'options' : [make_label_value(i, i) for i in occ_opts] if occ_opts else []
                },
                    
                'distribution' : {
                'options' : [
                    {'label': 'disjoint' , 'value': 'disjoint'},
                    {'label': 'joint' , 'value': 'joint'},
                    {'label': 'explicit' , 'value': 'explicit'},
                    {'label': 'Same as IIV' , 'value': 'same-as-iiv'},
                    ]
                    },
            },
            
            
            return iov_data, iov_dd_options[0]
        else:
            raise PreventUpdate

    @app.callback(
        Output("iov_table","row_selectable"),
        Input('all-tabs', 'value'),
        State("iov_table","row_selectable"),
    )
    def check_iov(tab, selectable):
        if tab == "par-var-tab":
            if config.model.datainfo:
                select = "multi"
            else:
                select = False
            return select
        else: raise PreventUpdate

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("iiv_table", "selected_rows"),
        State("iiv_table", "data"),
        prevent_initial_call=True
    )
    def set_iivs(selected_index, data):
        new = []
        idx_to_remove = [i for i in range(len(data)) if i not in selected_index]
        for i in selected_index:
            new.append(data[i])
        for i in idx_to_remove:
            p = data[i]
            config.model = remove_iiv(model=config.model, to_remove=p["parameter"])      

        created={}
        for i in new: 
            if "custom" in i:
                i["expression"] = i["custom"]
                del i["custom"]
            
            if has_random_effect(model=config.model, parameter=i["parameter"], level="iiv"):
                pass    
            else:
                config.model = add_iiv(model=config.model, list_of_parameters=i["parameter"],
                                            expression=i["expression"], operation=i["operation"], 
                                            initial_estimate=i["initial_estimate"], eta_names=i["eta_names"])
                
            created[i["parameter"]] = [frozenset(i.values()),has_random_effect(model=config.model, parameter=i["parameter"])]

        return True


    @app.callback(
            Output("data-dump", "clear_data", allow_duplicate=True),
            Input('iov_table', 'selected_rows'),
            State('iov_table', 'data'),
            prevent_initial_call=True
    )

    def set_iov(selected_index, data):
    
        new = []
        idx_to_remove = [i for i in range(len(data)) if i not in selected_index]
        for i in selected_index:
            new.append(data[i])
        for i in idx_to_remove:
            par = data[i]
            try:
                config.model = remove_iov(model=config.model, to_remove=par["parameter"])      
            except: pass
        creator = {}
        
        for i in new:
            if has_random_effect(model=config.model, parameter=i["parameter"], level="iov"):
                pass
            else:         
                config.model = add_iov(model=config.model,occ=i["occasion"] ,list_of_parameters=i["parameter"], eta_names=i["eta_names"])    
            creator[i["parameter"]] = [frozenset(i.values()),has_random_effect(model=config.model, parameter=i["parameter"])]
        return True

    @app.callback(
            Output('iiv_table', 'selected_rows'),
            Input('iiv_table','data'),
            prevent_initial_call=True
    )

    def check_iiv(iiv_data):
        def render_checks(data, level):
            to_check = []
            for i, j in enumerate(data):
                try:
                    if has_random_effect(model=config.model , parameter=j["parameter"], level=level):
                        to_check.append(i)
                except: pass
            return to_check
        iiv_checks = render_checks(iiv_data, "iiv")
        return iiv_checks
    
    @app.callback(
            Output('iov_table', 'selected_rows'),
            Input('iov_table', 'data'),
            prevent_initial_call=True
    )
    def check_iov(iov_data):
        def render_checks(data, level):
            to_check = []
            for i, j in enumerate(data):
                try:
                    if has_random_effect(model=config.model , parameter=j["parameter"], level=level):
                        to_check.append(i)
                except: pass
            return to_check
        iov_checks = render_checks(iov_data, "iov")
        return iov_checks

    @app.callback(
        Output("covariance_matrix", "data", allow_duplicate=True),
        Output("covariance_matrix", "columns"),
        Output("covariance_matrix", "style_data_conditional"),
        Output("covariance_matrix", "dropdown"),
        Output("covariance_matrix", "dropdown_conditional"),
        Input("all-tabs", "value"),
        prevent_initial_call = True
    )

    def get_cov_matrix(tab):
        try:
            model = config.model
            matrix = model.random_variables.etas.names
            data = model.random_variables.etas.covariance_matrix
            df = pd.DataFrame(np.array(data).astype(str), columns=matrix)
            df.replace(str(0), None, inplace=True)
            df = df.applymap(lambda x: 'X' if isinstance(x, str) else x)
            df.insert(0, "parameter" ,matrix, True)
            data = df.to_dict('records')

            columns=[{"name": i, "id": i, "editable": i != "parameter", "presentation": "dropdown"} for i in df.columns]

            style_data_conditional=[{
                                    'if':{'column_id' : [matrix[x] for x in range(len(matrix)) if x-i >= 0],
                                            'row_index' : i
                                            }, 'backgroundColor' : 'gainsboro'
                                    }
                                    for i in range(len(matrix))]

            dropdown= { 
                    i:{
                        'options': [
                                    {'label':'X', 'value':'X'},
                                    ]
                        } for i in matrix     
                    }

            dropdown_conditional=[{
                                'if': {
                                    'column_id' : i,
                                    'filter_query': '{parameter} eq "' + str(i) + '"'
                                    }, 
                                    'options': []
                                } for i in matrix]  
            return data, columns, style_data_conditional, dropdown, dropdown_conditional
        except: raise PreventUpdate

    @app.callback(
        Output("covariance_matrix", "data", allow_duplicate=True),
        Input("covariance_matrix", "data"),
        prevent_initial_call=True
        )

    def set_covariance(data):
        d = data
        pairs = {}
        for row in d[::-1]:
            pairs[row["parameter"]] = []
            for key, value in row.items():
                    if value == 'X':
                        pairs[row["parameter"]].append(key)
                        
                    for second_iter in d[::-1]:
                        if second_iter['parameter'] == key:
                            second_iter.update({row["parameter"]:value})
        for keys in pairs.values():
            config.model = split_joint_distribution(model=config.model, rvs=keys)              
            try:
                config.model = create_joint_distribution(model = config.model,rvs=keys)
            except: pass
        return data    

    return