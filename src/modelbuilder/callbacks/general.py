import base64
import io

import pandas as pd
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from pharmpy.modeling import (
    convert_model,
    create_basic_pk_model,
    get_model_code,
    set_name,
    write_model,
)

import modelbuilder.config as config


def general_callbacks(app):
    # Create model
    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        [
            Input("route-radio", "value"),
            State("modelformat", 'value'),
        ],
        prevent_initial_call=True,
    )
    def create_model(route, format):
        if format and route:
            # Dataset is connected to model in parse_dataset
            old_dataset = config.model.dataset
            old_datainfo = config.model.datainfo

            start_model = create_basic_pk_model(route)
            start_model = set_name(start_model, "model")
            start_model = convert_model(start_model, format)
            start_model = start_model.replace(dataset=old_dataset, datainfo=old_datainfo)
            config.model = start_model.update_source()
            return True
        else:
            raise PreventUpdate

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("model-name", "value"),
        Input("model-description", "value"),
        prevent_initial_call=True,
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
        s += "------------------STATEMENTS----------------" + "\n\n"
        s += str(config.model.statements) + "\n\n"
        s += "------------------ETAS----------------------" + "\n\n"
        s += str(config.model.random_variables.etas) + "\n\n"
        s += "------------------PARAMETERS----------------" + "\n\n"
        s += str(config.model.parameters) + "\n\n"

        return s

    # Callback for changing the model print
    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("modelformat", 'value'),
        prevent_initial_call=True,
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
