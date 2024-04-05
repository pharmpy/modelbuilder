from dash import Input, Output, State, ctx

import modelbuilder.config as config
from modelbuilder.design.style_elements import disable_component, enable_component
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.internals.model_state import update_model


def structural_callbacks(app):
    @app.callback(
        Output("abs_rate-radio", "value"),
        Output("elim_radio", "value"),
        Output("peripheral-radio", "value"),
        Output("abs_delay_radio", "value"),
        Input("route-radio", "value"),
    )
    def reset_defaults(route):
        if route == "iv":
            default_abs_rate = 0
            default_abs_delay = 0
        else:
            default_abs_rate = 'FO'
            default_abs_delay = 'LAGTIME(OFF);TRANSITS(0)'
        default_elim = 'FO'
        default_peripherals = 0
        return default_abs_rate, default_elim, default_peripherals, default_abs_delay

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("abs_rate-radio", "value"),
        prevent_initial_call=True,
    )
    def update_abs_rate_on_click(abs_rate):
        if abs_rate:
            mfl = f'ABSORPTION({abs_rate})'
            model_new, ms_new = update_model(config.model, config.model_state, mfl)
            config.model, config.model_state = model_new, ms_new
            return render_model_code(config.model)

    @app.callback(
        Output("abs_rate-radio", "options"),
        Output("abs_rate-radio", "style"),
        Input("route-radio", "value"),
        State("abs_rate-radio", "options"),
        State("abs_rate-radio", "style"),
    )
    def update_abs_rate_from_route(route, options, style):
        if route == "iv":
            options_new, style_new = disable_component(options, style)
        else:
            options_new, style_new = enable_component(options, style)

        return options_new, style_new

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("elim_radio", "value"),
        prevent_initial_call=True,
    )
    def update_elim_on_click(elim):
        mfl = f'ELIMINATION({elim})'
        model_new, ms_new = update_model(config.model, config.model_state, mfl)
        config.model, config.model_state = model_new, ms_new
        return render_model_code(model_new)

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("abs_delay_radio", "value"),
        prevent_initial_call=True,
    )
    def update_abs_delay_on_click(abs_delay):
        if abs_delay:
            mfl = abs_delay
            model_new, ms_new = update_model(config.model, config.model_state, mfl)
            config.model, config.model_state = model_new, ms_new
            return render_model_code(config.model)

    @app.callback(
        Output("abs_delay_radio", "options"),
        Output("abs_delay_radio", "style"),
        Input("route-radio", "value"),
        State("abs_delay_radio", "options"),
        State("abs_delay_radio", "style"),
    )
    def update_abs_delay_from_route(route, options, style):
        if route == "iv":
            options_new, style_new = disable_component(options, style)
        else:
            options_new, style_new = enable_component(options, style)

        return options_new, style_new

    # callback for peripheral compartments
    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("peripheral-radio", "value"),
        prevent_initial_call=True,
    )
    def peripheral_compartments(n):
        if n is not None:
            mfl = f'PERIPHERALS({n})'
            model_new, ms_new = update_model(config.model, config.model_state, mfl)
            config.model, config.model_state = model_new, ms_new
            return render_model_code(model_new)
