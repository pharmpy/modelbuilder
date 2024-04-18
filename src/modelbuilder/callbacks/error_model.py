from dash import Input, Output
from dash.exceptions import PreventUpdate

import modelbuilder.config as config
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.internals.model_state import update_model_state


def error_model_callbacks(app):
    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("base-type-radio", "value"),
        prevent_initial_call=True,
    )
    def update_base_error_model(base_error):
        if base_error:
            ms = update_model_state(config.model_state, error=base_error)
            if ms != config.model_state:
                config.model_state = ms
                return render_model_code(ms.generate_model())
        raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("additional-types-checklist", "value"),
        prevent_initial_call=True,
    )
    def update_additional_error_model(additional_type):
        if additional_type is not None:
            additional_types = ';'.join(additional_type)
            ms = update_model_state(config.model_state, error=additional_types)
            if ms != config.model_state:
                config.model_state = ms
                return render_model_code(ms.generate_model())
        raise PreventUpdate
