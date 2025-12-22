from dash import Input, Output, State
from dash.exceptions import PreventUpdate

import modelbuilder.config as config
from modelbuilder.design.style_elements import disable_component, enable_component
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.internals.model_state import update_model_state


def error_model_callbacks(app):
    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Output("output-python", "value", allow_duplicate=True),
        Output("output-r", "value", allow_duplicate=True),
        Output("additional-types-checklist", "value"),
        Input("base-type-radio", "value"),
        State("base-type-radio-dv2", "value"),
        prevent_initial_call=True,
    )
    def update_base_error_model(base_error, base_error2):
        if base_error:
            if base_error2 is None:
                base_error2 = ''
            ms = update_model_state(config.model_state, error={1: base_error, 2: base_error2})
            if ms != config.model_state:
                config.model_state = ms
                return *render_model_code(ms), []
        raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Output("output-python", "value", allow_duplicate=True),
        Output("output-r", "value", allow_duplicate=True),
        Input("additional-types-checklist", "value"),
        State("additional-types-checklist-dv2", "value"),
        prevent_initial_call=True,
    )
    def update_additional_error_model(additional_type, additional_type_2):
        # FIXME: when power is added after iiv on ruv then the resulting error model will be wrong
        # Issue https://github.com/pharmpy/pharmpy/issues/3102
        if additional_type is not None:
            additional_types = ';'.join(additional_type)
            if additional_type_2 is not None:
                additional_types_2 = ';'.join(additional_type_2)
            else:
                additional_types_2 = ''
            ms = update_model_state(
                config.model_state, error={1: additional_types, 2: additional_types_2}
            )
            if ms != config.model_state:
                config.model_state = ms
                return render_model_code(ms)
        raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Output("output-python", "value", allow_duplicate=True),
        Output("output-r", "value", allow_duplicate=True),
        Output("additional-types-checklist-dv2", "value"),
        Input("base-type-radio-dv2", "value"),
        State("base-type-radio", "value"),
        prevent_initial_call=True,
    )
    def update_base_error_model_dv2(base_error, base_error1):
        if base_error:
            ms = update_model_state(config.model_state, error={1: base_error1, 2: base_error})
            if ms != config.model_state:
                config.model_state = ms
                return *render_model_code(ms), []
        raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Output("output-python", "value", allow_duplicate=True),
        Output("output-r", "value", allow_duplicate=True),
        Input("additional-types-checklist-dv2", "value"),
        State("additional-types-checklist", "value"),
        prevent_initial_call=True,
    )
    def update_additional_error_model(additional_type, additional_type_1):
        # FIXME: when power is added after iiv on ruv then the resulting error model will be wrong
        # Issue https://github.com/pharmpy/pharmpy/issues/3102
        if additional_type is not None:
            additional_types = ';'.join(additional_type)
            additional_types_1 = ';'.join(additional_type_1)
            ms = update_model_state(
                config.model_state, error={1: additional_types_1, 2: additional_types}
            )
            if ms != config.model_state:
                config.model_state = ms
                return render_model_code(ms)
        raise PreventUpdate

    @app.callback(
        Output("base-type-radio-dv2", "options"),
        Output("base-type-radio-dv2", "style"),
        Output("base-type-radio-dv2", "value"),
        Output("additional-types-checklist-dv2", "options"),
        Output("additional-types-checklist-dv2", "style"),
        Input("all-tabs", "value"),
        Input("model_type", 'value'),
        Input("base-type-radio-dv2", "options"),
        Input("base-type-radio-dv2", "style"),
        Input("additional-types-checklist-dv2", "options"),
        Input("additional-types-checklist-dv2", "style"),
    )
    def enable_dv2(tab, model_type, base_opt, base_style, add_opt, add_style):
        if tab == "error-tab":
            if model_type == 'PD':
                base_opt_new, base_style_new = enable_component(base_opt, base_style)
                base_opt_new[2] = {'label': ' Combined', 'value': 'combined', 'disabled': True}
                add_opt_new, add_style_new = enable_component(add_opt, add_style)
                base_value = 'prop'
            else:
                base_opt_new, base_style_new = disable_component(base_opt, base_style)
                add_opt_new, add_style_new = disable_component(add_opt, add_style)
                base_value = None
            return base_opt_new, base_style_new, base_value, add_opt_new, add_style_new
        else:
            raise PreventUpdate

    @app.callback(
        Output("additional-types-checklist", "value", allow_duplicate=True),
        Output("additional-types-checklist-dv2", "value", allow_duplicate=True),
        Input("model_type", 'value'),
        prevent_initial_call=True,
    )
    def reset_additional_error_types(model_type):
        return [], []
