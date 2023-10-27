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

def base_callbacks(app):
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
            config.model = start_model
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
            config.model = set_name(config.model, name)
        if description:
            config.model = config.model.replace(description=description)
        config.model = config.model.update_source()
        return True

    def render_generic_model(model):
       s = ""
       s += str(config.model.statements) + "\n\n"
       s += str(config.model.random_variables.etas)
       return s

    #Callback for changing the model print
    @app.callback(
            Output("output-model", "value", allow_duplicate=True),
            Input("modelformat", 'value'),
            prevent_initial_call=True
    )
    def change_format(format):
        if format != "generic":
            config.model = convert_model(config.model, format)
            return get_model_code(config.model)
        elif format == "generic":
            config.model = convert_model(config.model, format)
            text_renderer = render_generic_model(config.model)
            return text_renderer


    @app.callback(
        Output("output-model", "value"),
        Input("text-refresh", "n_intervals"),
        State("modelformat", 'value'),

    )
    def get_code(n, format):
        try:
            if format != "generic":
                return get_model_code(config.model)
            else:
                text_renderer = render_generic_model(config.model)
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
                        write_model(config.model, path=path)
                        return f"Model written to {path}"
                    else:
                        write_model(config.model)
                        return f'Model written to directory folder'
        return f'Provided path {path} '

    return
