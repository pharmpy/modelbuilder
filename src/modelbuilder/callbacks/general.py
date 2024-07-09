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
        Input("model-name", "value"),
        Input("model-description", "value"),
    )
    def change_route(route, model_name, model_description):
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
        if model_name and model_description:
            ms = update_model_state(
                ms, model_attrs={'name': model_name, 'description': model_description}
            )
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
        Output('pd_effect_radio', 'value'),
        Output("pd_expression_radio", "value"),
        Output("abs_rate-radio", "value", allow_duplicate=True),
        Output("elim_radio", "value", allow_duplicate=True),
        Output("peripheral-radio", "value", allow_duplicate=True),
        Output("abs_delay_radio", "value", allow_duplicate=True),
        Output("modelformat", "value"),
        Input("model_type", "value"),
        Input("route-radio", "value"),
        Input("model-name", "value"),
        Input("model-description", "value"),
        prevent_initial_call=True,
    )
    def change_model_type(model_type, route, model_name, model_description):
        effect = None
        expr = None

        if route == "iv":
            default_abs_rate = 0
            default_abs_delay = 0
        else:
            default_abs_rate = 'FO'
            default_abs_delay = 'LAGTIME(OFF);TRANSITS(0)'
        default_elim = 'FO'
        default_peripherals = 0

        ms = ModelState.create(route)
        if model_name and model_description:
            ms = update_model_state(
                ms, model_attrs={'name': model_name, 'description': model_description}
            )
        config.model_state = ms

        if model_type == 'PD':
            mfl = 'DIRECTEFFECT(LINEAR)'
            ms = ms.replace(mfl=mfl)
            ms = update_model_state(config.model_state, mfl)
            effect = 'DIRECTEFFECT'
            expr = 'LINEAR'
            config.model_state = ms

        return (
            render_model_code(ms.generate_model()),
            effect,
            expr,
            default_abs_rate,
            default_elim,
            default_peripherals,
            default_abs_delay,
            "nonmem",
        )

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("model-name", "value"),
        Input("model-description", "value"),
        prevent_initial_call=True,
    )
    def change_name_desc(name, description):
        model_attrs = config.model_state.model_attrs
        if name:
            model_attrs['name'] = name
            ms = update_model_state(config.model_state, model_attrs=model_attrs)
            if ms != config.model_state:
                config.model_state = ms
                return render_model_code(ms.generate_model())
        if description:
            model_attrs['description'] = description
            ms = update_model_state(config.model_state, model_attrs=model_attrs)
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
            if format in ['python', 'r']:
                code = config.model_state.get_code(language=format)
                return code
            else:
                ms = config.model_state.replace(model_format=format)
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
                model = config.model_state.generate_model()
                if model.dataset is None:
                    return "Please provide a dataset"
                else:
                    if path:
                        write_model(config.model_state.generate_model(), path=path)
                        return f"Model written to {path}"
                    else:
                        write_model(config.model_state.generate_model())
                        return 'Model written to directory folder'
        return f'Provided path {path} '

    return
