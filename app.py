from dash import Dash, html, dcc,  callback, Output, Input, State, dash_table
from pharmpy.modeling import *
from pharmpy.model import *
import dash_bootstrap_components as dbc
import designfile as df
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import base64
import json
import io
import time
import os
PHARMPY_LOGO = "https://pharmpy.github.io/latest/_images/Pharmpy_logo.svg"


def make_label_value(key, value):
            return {"label": key, "value":value}



app = Dash(__name__, title="Pharmpy GUI", external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True, update_title=None)


app.layout = dbc.Container([
    dcc.Store(id="data-dump"),
    df.navbar,
    dbc.Row([
        dbc.Col(children=[
            html.Div(children=[
                html.Hr(),
                df.model_format_radio,
                df.model_output_text,
                dbc.Row([
                    dbc.Col(
                        dcc.Clipboard(target_id= "output-model", title="copy", 
                                    style={"position": "relative", "top": "-70vh", "right":"-25vw", 'cursor':'pointer'}
                        )
                    )
                    ], style={'width':'5vw'} #Ensure clipboard stays within row
                )
                ]
            ),
            ],
            width=4,  
        ), 
        
        dbc.Col(df.all_tabs, width=8) ,
        
    dbc.Row([   
        dbc.Col(children=[
        df.download_model
        ] 
        ,width=4),
        dbc.Col(width=8)

    ],)
    ], style={'width':'100vw', }),
    
   
]

, style={'height': '100vh', 'width': '100vw', "margin-bottom": "0%", }, fluid=True)

#Create model
@app.callback(
        Output("data-dump", "clear_data",allow_duplicate=True),
        [
        Input("route-radio", "value"),
        
        Input('upload-dataset', 'filename'),
        State("modelformat", 'value'),
        ]
        ,prevent_initial_call=True
)
def create_model(route, dataset, format):
    if format and route:
        if dataset:
            time.sleep(1)
            path = 'dataset/'+dataset
        else:
            path=None
        start_model = create_basic_pk_model(route, dataset_path=path)    
        start_model = set_name(start_model, "model")
        
        start_model = convert_model(start_model, format)
        globals()["model"] = start_model
        return True
    else: 
        raise PreventUpdate

@app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("model-name", "value"),
        Input("model-description", "value"),
        prevent_initial_call = True        
)            

def change_name_desc(name, description):
    if name:
        globals()["model"] = set_name(globals()["model"], name)
    if description:
        globals()["model"] = globals()["model"].replace(description=description)
    return True    

#Callback for changing the model print
@app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("modelformat", 'value'),
        prevent_initial_call=True
)
def change_format(format):
    if format != "generic":
        globals()["model"] = convert_model(globals()["model"], format)
        return get_model_code(globals()["model"])
    elif format == "generic":
        globals()["model"] = convert_model(globals()["model"], format)
        text_renderer = ""
        text_renderer += str(globals()["model"].statements)
        text_renderer += str(globals()["model"].random_variables.etas)
        return text_renderer
    

@app.callback(
    Output("output-model", "value"),
    Input("text-refresh", "n_intervals"),
    State("modelformat", 'value'),
    
)

def get_code(n, format):   
    try:
        if format != "generic":
            return get_model_code(globals()["model"])
        else: 
            text_renderer = str(globals()["model"].statements)
            text_renderer += str(globals()["model"].random_variables.etas)
            return text_renderer
    except: 
        raise PreventUpdate 

#Dataset-parsing
@app.callback(
   Output("dataset-path", 'value'),
   Input("upload-dataset", 'contents'),
   State('upload-dataset', 'filename') 
)
def parse_dataset(contents, filename):
     
    if contents is not None:
        for file in os.listdir('dataset'):
            if file.endswith(".csv"):
                os.remove('dataset/'+file)
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        if 'csv' in filename:
        # Assume that the user uploaded a CSV file
            data = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))

            data.to_csv('dataset/'+filename, index=False)   
        return str(filename), #dis, dis
    else: raise PreventUpdate
    #else: return f'No dataset, editable ={editable}', dis, dis 
    


#Callback for absorption, elimination
@app.callback(
        Output("data-dump", "clear_data",allow_duplicate=True),
        Input("abs_rate-radio", "value"),
        Input("elim_radio", "value"),
        prevent_initial_call=True
)

def update_abs_elim(abs, elim):
    if elim:
        elim_keys ={"FO": set_first_order_elimination(globals()["model"]),
                "MM": set_michaelis_menten_elimination(globals()["model"]),
                "mixed_MM_FO": set_mixed_mm_fo_elimination(globals()["model"])
                }
        
        globals()["model"] = elim_keys[elim]
        return True
    if abs:
        abs_keys ={"ZO": set_zero_order_absorption(globals()["model"]),
                "FO": set_first_order_absorption(globals()["model"]),
                "seq_ZO_FO": set_seq_zo_fo_absorption(globals()["model"])
                }
        globals()["model"] = abs_keys[abs]
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
    if value == "IV":
        return [{**dictionary, "disabled":True} for dictionary in options], 0
    else: 
        return [{**dictionary, "disabled":False} for dictionary in options], rate

#Callback for download-btn
@app.callback(
    Output("model_confirm", "children"),
    Input("download-btn", "n_clicks"),
    State("model-name", "value"),
    State("model_path", "value"),
    prevent_initial_call=True,
              )

def make_mod(n_clicks, name, path):
    if not name:
        return "please provide model name"
    if name and n_clicks:
        if n_clicks:
    
                if path:
                    write_model(globals()["model"], path=path)
                    return f"Model written to {path}"
                else: 
                    write_model(globals()["model"])
                    return f'Model written to directory folder'
    return f'Provided path {path} '

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
            globals()["model"] = set_transit_compartments(globals()["model"],0)
            globals()["model"] = add_lag_time(globals()["model"])
            return [{"label": "Lag Time", "value" : True, "disabled":False}], None, True
        except:
            raise PreventUpdate

    if transit_input :

        try:
            globals()["model"]= remove_lag_time(globals()["model"])
            if transit_input:
                globals()["model"] = set_transit_compartments(globals()["model"], int(transit_input))
            return [{"label": "Lag Time", "value" : False, "disabled":True}], int(transit_input), False
        except:

            raise PreventUpdate 
    else: 
        try:
            globals()["model"]= remove_lag_time(globals()["model"])
            globals()["model"] = set_transit_compartments(globals()["model"],0)
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
            globals()["model"] = set_peripheral_compartments(globals()["model"], int(n))
            return True
        else:
            while globals()["peripherals"] > 0:
                globals()["model"] = remove_peripheral_compartment(globals()["model"])
                globals()["peripherals"] = globals()["peripherals"] - 1 
    except: return True

@app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("bio_toggle", "value"),
        prevent_initial_call = True
)
def set_bioavailability(toggle):
    if toggle:
        try:
            globals()["model"] = add_bioavailability(globals()["model"])

    else:
        globals()["model"] = remove_bioavailability(globals()["model"])
        return True

#Getting the model parameters
@app.callback(
    Output("parameter-table", "data", allow_duplicate=True),
    Input("fix_all_toggle", "value"),
    Input("all-tabs", "value"),
    prevent_initial_call = 'initial_duplicate' 
    
)

def get_parameters(fixed, tab):
    if tab == "parameters-tab":
        
        if fixed:
            names = globals()["model"].parameters.names 
            globals()["model"] = fix_parameters(globals()["model"],names)
            parameters = globals()["model"].parameters.to_dict()
            
            
            return parameters["parameters"]
        else:
            names = globals()["model"].parameters.names 
            globals()["model"] = unfix_parameters(globals()["model"],names)
            parameters = globals()["model"].parameters.to_dict()
            
            
            return parameters["parameters"]
    else:
        raise PreventUpdate

@app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("parameter-table", "data"),
        prevent_initial_call = True
)
def visualise_data(data):
    def replace_empty(data):
            for item in data:
                for key, value in item.items():
                    if value == "":
                        item[key] = None
            return data
    data = replace_empty(data)
    current = globals()["model"].parameters.to_dict()
    current["parameters"] = data
    
    try:
        globals()["model"] = globals()["model"].replace(parameters= Parameters.from_dict(current))
        globals()["model"] = globals()["model"].update_source()
    except: raise PreventUpdate

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
    try:
        if n_clicks:
            if upper:
                upper = float(upper)
            if lower:
                lower = float(lower)    
            globals()["model"] = add_population_parameter(globals()["model"], name, float(init), lower, upper, fix == "True")
            parameters = globals()["model"].parameters.to_dict()
            df = pd.DataFrame(parameters["parameters"])
            model_parameters = df.to_dict('records')
            return model_parameters, None, None, None, None, None
    except:
        PreventUpdate

@app.callback(
        Output("iiv_table", "data"),
        Output("iov_table","data"),
        Output("iov_table","dropdown"),
        Input('all-tabs', 'value'),
        prevent_initial_call = True
)
def render_iiv_iov_data(tab):
     

    if tab == "par-var-tab":
        try:
            parameter_names = [str(s.symbol) for s in globals()["model"].statements if not isinstance(s, CompartmentalSystem)]
            df = pd.DataFrame({'parameter':parameter_names, 'initial_estimate':0.09, 'operation':'*', 'eta_names':None})
            iiv_data = df.to_dict('records')

            iov_data = pd.DataFrame({'parameter': parameter_names, 'distribution':'disjoint', 'eta_names':None})
            iov_data = iov_data.to_dict('records')
            try:
                occ_opts = globals()["model"].datainfo.typeix["idv"].names + globals()["model"].datainfo.typeix["unknown"].names
            except:
                occ_opts = globals()["model"].datainfo.typeix["unknown"].names  
                
            iov_dd_options = {
            
            'occasion': {
                'options' : [make_label_value(i, i) for i in occ_opts]
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

            return iiv_data, iov_data, iov_dd_options[0]
        except: raise PreventUpdate
    else:
        raise PreventUpdate
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
        globals()["model"] = remove_iiv(model=globals()["model"], to_remove=p["parameter"])      

    created={}
    for i in new: 
        if "custom" in i:
            i["expression"] = i["custom"]
            del i["custom"]
        
        if has_random_effect(model=globals()["model"], parameter=i["parameter"], level="iiv"):
            pass    
        else:
            globals()["model"] = add_iiv(model=globals()["model"], list_of_parameters=i["parameter"],
                                        expression=i["expression"], operation=i["operation"], 
                                        initial_estimate=i["initial_estimate"], eta_names=i["eta_names"])
            
        created[i["parameter"]] = [frozenset(i.values()),has_random_effect(model=globals()["model"], parameter=i["parameter"])]

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
            globals()["model"] = remove_iov(model=globals()["model"], to_remove=par["parameter"])      
        except: pass
    creator = {}
    
    for i in new:
        if has_random_effect(model=globals()["model"], parameter=i["parameter"], level="iov"):
            pass
        else:         
            globals()["model"] = add_iov(model=globals()["model"],occ=i["occasion"] ,list_of_parameters=i["parameter"], eta_names=i["eta_names"])    
        creator[i["parameter"]] = [frozenset(i.values()),has_random_effect(model=globals()["model"], parameter=i["parameter"])]
    return True

@app.callback(
        Output('iiv_table', 'selected_rows'),
        Output('iov_table', 'selected_rows'),
        #Input('iov_table', 'selected_rows'),
        #Input('iiv_table', 'selected_rows'),
        Input('iiv_table','data'),
        Input('iov_table', 'data'),
        prevent_initial_call=True
)

def check_tables(iiv_data, iov_data):
    def render_checks(data, level):
        to_check = []
        for i, j in enumerate(data):
            try:
                if has_random_effect(model=globals()["model"] , parameter=j["parameter"], level=level):
                    to_check.append(i)
            except: pass
        return to_check
    iiv_checks, iov_checks = render_checks(iiv_data, "iiv"), render_checks(iov_data, "iov")
    return iiv_checks, iov_checks

@app.callback(
    Output("error_div", "children", allow_duplicate=True),
    Output("comb_check", "value", allow_duplicate=True),
    Output("prop_check", "value", allow_duplicate=True),
    Input("add_check", "value"),
    Input("add_dv", "value"),
    Input("add_data_trans", "value"),
    Input("add_series_terms", "value"),
    State("comb_check", "value"),
    State("prop_check", "value"),
    prevent_initial_call=True
)



def create_add_error(addcheck, dv, data_trans, series_terms, comb, prop):
 
    #current = globals()["model"]
    if addcheck:
        globals()["model"]= remove_error_model(globals()["model"])

        if type(series_terms) == int:
            series_terms = int(series_terms)
        else:
            series_terms = 2    
        globals()["model"]= set_additive_error_model(
        globals()["model"], dv=dv, data_trans=data_trans,series_terms=series_terms)
        return f'Addititve Error model: {has_additive_error_model(globals()["model"])}', False, False
    return f'', comb, prop 
 #Addititve Error model: {has_additive_error_model(globals()["model"])}      
    #else:
        #globals()["model"] = current
    
    


    
   
@app.callback(
    Output("error_div", "children", allow_duplicate=True),
    Output("add_check", "value", allow_duplicate=True),
    Output("prop_check", "value", allow_duplicate=True),
    Input("comb_check", "value"),
    Input("comb_dv", "value"),
    Input("comb_data_trans", "value"),
    State("add_check", "value"),
    State("prop_check", "value"),
    
    prevent_initial_call=True
    ) 

def create_comb_error(check, dv, data_trans, add, prop):
    if check:
        globals()["model"]= remove_error_model(globals()["model"])

        globals()["model"]= set_combined_error_model(
        globals()["model"], dv=dv, data_trans=data_trans)
            
        return f'Combined Error model: {has_combined_error_model(globals()["model"])}', False, False    
    return f'', add, prop   
    #Combined Error model: {has_combined_error_model(globals()["model"])}

@app.callback(
    Output("error_div", "children", allow_duplicate=True),
    Output("add_check", "value", allow_duplicate=True),
    Output("comb_check", "value", allow_duplicate=True),
    Input("prop_check", "value"),
    Input("prop_dv", "value"),
    Input("prop_data_trans", "value"),
    Input("prop_zero_prot", "value"),
    State("add_check", "value"),
    State("comb_check", "value"),
    prevent_initial_call=True
    ) 

def create_prop_error(check, dv, data_trans, protection, add, comb):
    if check:
        globals()["model"]= remove_error_model(globals()["model"])

        if protection == "False":
            protection = False
        else: protection = True
        globals()["model"]= set_proportional_error_model(
            globals()["model"], dv=dv, data_trans=data_trans, zero_protection=protection)
            
        return f'Proportional Error model: {has_proportional_error_model(globals()["model"])}', False, False
    return f'', add, comb
           #Proportional Error model: {has_proportional_error_model(globals()["model"])}
    

    

@app.callback(
    Output("error_div", "children", allow_duplicate=True),
    Input("time_check", "value"),
    Input("time_cutoff", "value"),
    Input("data_idv", "value"),
    prevent_initial_call=True
    ) 

def create_time_error(check, cutoff, idv):
    if check:
        if not cutoff:
            cutoff = 1
        if idv: 
            globals()["model"]= set_time_varying_error_model(globals()["model"], cutoff=cutoff, idv = idv)
        else:
            globals()["model"]= set_time_varying_error_model(globals()["model"], cutoff=cutoff,)
   
    return f''    
    #Time Error model: {str(globals()["model"].statements.find_assignment("Y"))}

    

@app.callback(
    Output("error_div", "children", allow_duplicate=True),
    Input("wgt_check", "value"),
    prevent_initial_call = True
)

def create_wgt_error(check):
    
    #current = globals()["model"]
    if check:
        globals()["model"] = set_weighted_error_model(globals()["model"])
    #else:
        #globals()["model"] = remove_error_model(globals()["model"])
        #globals()["model"] = current 
    return f''
    #Weighted Error model: {has_weighted_error_model(globals()["model"])}
    
@app.callback(
    [Output("covar-param-name", "options")],
    [Output("covar-name", "options")],
    [Output("covar_div", "children", allow_duplicate=True)],
    Input("all-tabs", "value"),
    prevent_initial_call = True
)

def get_params_covars(tab):
        
        
        def param_expression (parameter):
            return [parameter+": ", str(globals()["model"].statements.before_odes.full_expression(parameter))]

        if tab == "covariate-tab":
            try:
                covar_names = get_model_covariates(globals()["model"], strings=True) if get_model_covariates(globals()["model"], strings=True) else globals()["model"].datainfo.typeix["unknown"].names
                covar_opt = [make_label_value(covar,covar) for covar in covar_names]
                param_opt = [make_label_value(param,param) for param in get_individual_parameters(globals()["model"])]
                render = dbc.ListGroup(children=[dbc.ListGroupItem(param_expression(item)) for item in get_individual_parameters(globals()["model"])]) 

                return param_opt, covar_opt, render
            except: PreventUpdate
        else:
            return  [{"label": "No Options", "value":True}], [{"label": "No Options", "value":True}], "No covariates found"   
    
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
    prevent_initial_call = True
)

def create_covariate(parameter,covariate,effect,custom,operation,nestle,button):
    try:
        def param_expression (parameter):
            return [parameter+": ", str(globals()["model"].statements.before_odes.full_expression(parameter))]
            
        

        if button:
            if custom:
                globals()["model"]= add_covariate_effect(
                    globals()["model"], parameter, covariate, custom, operation=operation, allow_nested= nestle=="True")
            globals()["model"]= add_covariate_effect(
                globals()["model"], parameter, covariate, effect, operation=operation, allow_nested= nestle=="True")
            return dbc.ListGroup(children=[dbc.ListGroupItem(param_expression(item)) for item in get_individual_parameters(globals()["model"])]), 0 
        return dbc.ListGroup(children=[dbc.ListGroupItem(param_expression(item)) for item in get_individual_parameters(globals()["model"], )]) , 0
    except:PreventUpdate

@app.callback(
    Output("datatable", "data"),
    Input("all-tabs", "value")
)
def render_datatable(tab):
    if tab=="data-info-tab":
        try:
            datainf = globals()["model"].datainfo.to_dict()
            df = pd.DataFrame(datainf["columns"])
            usable = df.to_dict('records') 
            return usable
        except: PreventUpdate
@app.callback(
    Output("data-dump", "clear_data", allow_duplicate=True),
    Input("datatable", "data"),
    prevent_initial_call = True
)
    
def update_datainf(data):
    try:
        datainf = globals()["model"].datainfo.to_dict()
        datainf["columns"] = data
        datainf = globals()["model"].datainfo.from_dict(datainf)
        globals()["model"] = globals()["model"].replace(datainfo=datainf)
        return True 
    except: raise PreventUpdate


@app.callback(
            Output("download_dtainf", "data"),
            Input("makedatainf","n_clicks")
)
def makeNone(clicked):
      if clicked:
            return dict(content=globals()["model"].datainfo.to_json(), filename=globals()["model"].name +".datainfo")
      


@app.callback(
    Output("data-dump", "clear_data", allow_duplicate=True),
    Input("estimation_btn", "n_clicks"),
    State("estimation_method","value"),
    State("estimation_index","value"),
    State("estimation_covs", "value"),
    State("int_eval_lapl", "value"),
    State("solver", "value"),
    State("solver_abstol", "value"),
    State("solver_reltol", "value"),
    State("estimation_keywords","value"),
    State("estimation_arguments", "value"),
    prevent_initial_call=True
)      

def create_estimation_step(clicked, method, index,cov,int_ev_lapl,solver,atol,rtol,keywords, arguments):
    keywords_arguments = {}
    if keywords and arguments is not None:
        for key, value in zip(json.loads('['+keywords+']'), json.loads('['+arguments+']')):
            keywords_arguments[key] = value
    

    checker =  ["interaction", "evaluation", "laplace"]
    if int_ev_lapl is not None:
        int_ev_lap_bools = [True if i in checker else False for i in int_ev_lapl]
    else:
        int_ev_lap_bools = [False, False, False]
    inputs = [method, index,cov]+int_ev_lap_bools+[solver, atol, rtol, keywords_arguments]
    
    default = {"method": method, "index" : None,
               "cov":None, "interaction" : False, 
               "evaluation" : False, "laplace" : False, 
               "solver" : None, "abstol" : None, 
                "reltol" : None ,"kwargs" : None}    
    if clicked:

        for key, value in zip(default.keys(), inputs):
            if value is not None or value is not False:
                default[key] = value
        globals()["model"] = add_estimation_step(
            globals()["model"],
            method=default["method"],
            interaction=default["interaction"],
            cov=default["cov"],
            evaluation=default["evaluation"],
            laplace=default["laplace"],
            solver=default["solver"],
            solver_rtol=default["reltol"],
            solver_atol=default["abstol"],
            idx=default["index"],
            tool_options = default["kwargs"]
        )   
    
    return str(globals()["model"].estimation_steps)

@app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),        
        Input("covariance_check", "value"),
        prevent_initial_call = True
)
def add_covariance(checked):
    if checked:
        globals()["model"] = add_covariance_step(globals()["model"])
        True
    else:
        True

@app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("remove_est_btn", "n_clicks"),
        State("remove_estimation", "value"),
        prevent_initial_call = True
)
def remove_estimation_idx(clicked, index):
    if clicked:
        globals()["model"] = remove_estimation_step(globals()["model"], index if index else 0)
        return True
    return True

@app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True), 
        Input("eval_btn", "n_clicks"),
        State("evaluation_index", "value"),
        prevent_initial_call = True
)
def estimation(clicked, index):
    if clicked:
        globals()["model"] = set_evaluation_step(globals()["model"], index if index else 0)
        return True
    return True
@app.callback(
    Output("data_dump","clear_data" ,allow_duplicate=True),
    Input("eval_btn", "n_clicks"),
    State("evaluation_index", "value"),   
    prevent_initial_call = True
    )
def set_eval(clicked, index):
    if clicked:
        globals()["model"] = set_evaluation_step(globals()["model"], index if index else -1)
        return True
    return True

@app.callback(
    Output("data_dump","clear_data" ,allow_duplicate=True),
    Input("covariance_check", "value"),
    prevent_initial_call = True
)

def covariance(checked):
    if checked:
        globals()["model"] = add_covariance_step(globals()["model"])
        return True
    else:
        globals()["model"] = remove_covariance_step(globals()["model"])
        return True   

@app.callback(
    Output("allometry_dropdown", "options"), Output("allo_variable", "options"),
    Input("all-tabs", "value"),
    prevent_initial_call = True
)

def give_options(tab):
    if tab == "allometry-tab":
        try: BW = globals()["model"].datainfo.descriptorix["body weight"].names
        except: BW = []
        try: LBM = globals()["model"].datainfo.descriptorix["lean body mass"].names
        except: LBM = []
        try: FFM = globals()["model"].datainfo.descriptorix["fat free mass"].names
        except: FFM = []

        weights = BW + LBM + FFM
        clearance = find_clearance_parameters(globals()["model"])
        volume = find_volume_parameters(globals()["model"])
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
    if custom in globals()["model"].datainfo.names:
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
                globals()["model"] = add_allometry(
                    globals()["model"], variable, reference_value=standard_values["ref_val"], 
                    parameters=standard_values["params"], initials=standard_values["inits"], 
                    lower_bounds=standard_values["lower"],
                    upper_bounds=standard_values["upper"], fixed=standard_values["fix"] )
            
            return True, pattern
        except: True, pattern
    else: True, pattern

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
        model = globals()["model"]
        matrix = model.random_variables.etas.names
        data = model.random_variables.etas.covariance_matrix
        df = pd.DataFrame(np.array(data).astype(str), columns=matrix)
        df.replace(str(0), None, inplace=True)
        df = df.applymap(lambda x: isinstance(x, str))
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
                                 {'label':'True', 'value':True},
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
    #FIXME! 
    #try:
    d = data
    for row in d[::-1]:
        true_keys = [row["parameter"]]
        for key, value in row.items():
                if value == True:
                    true_keys.append(key)
                    
                for second_iter in d[::-1]:
                    if second_iter['parameter'] == key:
                        second_iter.update({row["parameter"]:value})
    globals()["model"] = split_joint_distribution(model=globals()["model"], rvs=true_keys)              
    globals()["model"] = create_joint_distribution(model = globals()["model"],rvs=true_keys)


    return data 
        
    #except: raise PreventUpdate

    
                 
    
if __name__ == '__main__':
    app.run_server(debug=True)
    

