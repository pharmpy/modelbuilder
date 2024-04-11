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
        Input("route-radio", "value"),
    )
    def change_route(route):
        if route:
            # Dataset is connected to model in parse_dataset
            # old_dataset = config.model.dataset
            # old_datainfo = config.model.datainfo

            ms = ModelState.create(route)
            config.model_state = ms
            return render_model_code(ms.generate_model())
        else:
            raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("model-name", "value"),
        Input("model-description", "value"),
        prevent_initial_call=True,
    )
    def change_name_desc(name, description):
        if name:
            ms = update_model_state(config.model_state, model_attrs={'name': name})
            config.model_state = ms
            return render_model_code(ms.generate_model())
        if description:
            ms = update_model_state(config.model_state, model_attrs={'description': description})
            config.model_state = ms
            return render_model_code(ms.generate_model())
        return render_model_code(config.model_state.generate_model())

    # Callback for changing the model print
    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("modelformat", 'value'),
        prevent_initial_call=True,
    )
    def change_format(format):
        if format:
            ms = config.model_state.replace(model_format=format)
            config.model_state = ms
            return render_model_code(ms.generate_model())

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
            if str(filename).endswith('csv'):
                # Assume that the user uploaded a CSV file
                data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

                config.model = config.model.replace(dataset=data)
                config.model = config.model.update_source()
            else:
                # Raise error
                pass
            return (str(filename),)  # dis, dis
        else:
            raise PreventUpdate
        # else: return f'No dataset, editable ={editable}', dis, dis

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
