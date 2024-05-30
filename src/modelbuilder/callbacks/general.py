import base64
import io

import pandas as pd
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from pharmpy.modeling import write_model

import modelbuilder.config as config
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.internals.model_state import ModelState, update_model_state


def general_callbacks(app):
    # Create model
    @app.callback(
        Output("output-model", "value"),
        Output("abs_rate-radio", "value"),
        Output("elim_radio", "value"),
        Output("peripheral-radio", "value"),
        Output("abs_delay_radio", "value"),
        Input("route-radio", "value"),
    )
    def change_route(route):
        # Dataset is connected to model in parse_dataset
        # old_dataset = config.model.dataset
        # old_datainfo = config.model.datainfo
        if route == "iv":
            default_abs_rate = 0
            default_abs_delay = 0
        else:
            default_abs_rate = 'FO'
            default_abs_delay = 'LAGTIME(OFF);TRANSITS(0)'
        default_elim = 'FO'
        default_peripherals = 0

        ms = ModelState.create(route)
        config.model_state = ms
        return (
            render_model_code(ms.generate_model()),
            default_abs_rate,
            default_elim,
            default_peripherals,
            default_abs_delay,
        )

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("model-name", "value"),
        Input("model-description", "value"),
        prevent_initial_call=True,
    )
    def change_name_desc(name, description):
        if name:
            ms = update_model_state(config.model_state, model_attrs={'name': name})
            if ms != config.model_state:
                config.model_state = ms
                return render_model_code(ms.generate_model())
        if description:
            ms = update_model_state(config.model_state, model_attrs={'description': description})
            if ms != config.model_state:
                config.model_state = ms
                return render_model_code(ms.generate_model())
        raise PreventUpdate

    # Callback for changing the model print
    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("modelformat", 'value'),
        prevent_initial_call=True,
    )
    def change_format(format):
        if format:
            ms = config.model_state.replace(model_format=format)
            if ms != config.model_state:
                config.model_state = ms
                return render_model_code(ms.generate_model())
        raise PreventUpdate

    # Dataset-parsing
    @app.callback(
        Output("dataset-path", 'value'),
        Input("upload-dataset", 'contents'),
        State('upload-dataset', 'filename'),
    )
    def parse_dataset(contents, filename):
        if contents is not None:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            try:
                data = pd.read_table(
                    io.StringIO(decoded.decode('utf-8')), sep=r'\s+|,', engine='python'
                )
            except:
                error = "Dataset error!"
                config.model_state.dataset = None
                return error
            else:
                config.model_state.dataset = data
                return (str(filename),)
        else:
            raise PreventUpdate

    # Callback for download-btn
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
                    return 'Model written to directory folder'
        return f'Provided path {path} '

    return
