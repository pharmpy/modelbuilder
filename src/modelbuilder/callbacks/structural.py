from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from pharmpy.modeling import (
    add_bioavailability,
    add_lag_time,
    remove_bioavailability,
    remove_lag_time,
    set_first_order_absorption,
    set_first_order_elimination,
    set_michaelis_menten_elimination,
    set_mixed_mm_fo_elimination,
    set_peripheral_compartments,
    set_seq_zo_fo_absorption,
    set_transit_compartments,
    set_zero_order_absorption,
    set_zero_order_elimination,
)

import modelbuilder.config as config
from modelbuilder.design.style_elements import disable_component, enable_component


def structural_callbacks(app):
    @app.callback(
        Output("abs_rate-radio", "value"),
        Output("elim_radio", "value"),
        Output("peripheral-radio", "value"),
        Output("bio_toggle", "value"),
        Input("route-radio", "value"),
    )
    def reset_defaults(route):
        if route == "iv":
            default_abs_rate = 0
        else:
            default_abs_rate = 'FO'
        default_elim = 'FO'
        default_bio = False
        default_peripherals = 0
        return default_abs_rate, default_elim, default_peripherals, default_bio

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("abs_rate-radio", "value"),
        prevent_initial_call=True,
    )
    def update_abs_rate_on_click(abs_rate):
        if abs_rate:
            abs_funcs = {
                "ZO": set_zero_order_absorption,
                "FO": set_first_order_absorption,
                "seq_ZO_FO": set_seq_zo_fo_absorption,
            }
            config.model = abs_funcs[abs_rate](config.model)
            return True

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
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("elim_radio", "value"),
        prevent_initial_call=True,
    )
    def update_elim_on_click(elim):
        elim_funcs = {
            "FO": set_first_order_elimination,
            "MM": set_michaelis_menten_elimination,
            "mixed_MM_FO": set_mixed_mm_fo_elimination,
            "ZO": set_zero_order_elimination,
        }

        config.model = elim_funcs[elim](config.model)
        return True

    @app.callback(
        [
            Output("lag-toggle", "options"),
            Output("transit_input", "value"),
            Output("transit_input", "disabled"),
        ],
        Input("route-radio", "value"),
        Input("lag-toggle", "value"),
        Input("transit_input", "value"),
        prevent_inital_call=True,
    )
    def toggle_disable(route, lag_tog, transit_input):
        if route == "iv":
            return [{"label": "Lag Time", "value": True, "disabled": True}], None, True

        if lag_tog:
            try:
                config.model = set_transit_compartments(config.model, 0)
                config.model = add_lag_time(config.model)
                return [{"label": "Lag Time", "value": True, "disabled": False}], None, True
            except:
                raise PreventUpdate

        if transit_input:
            try:
                config.model = remove_lag_time(config.model)
                if transit_input:
                    config.model = set_transit_compartments(config.model, int(transit_input))
                return (
                    [{"label": "Lag Time", "value": False, "disabled": True}],
                    int(transit_input),
                    False,
                )
            except:
                raise PreventUpdate
        else:
            try:
                config.model = remove_lag_time(config.model)
                config.model = set_transit_compartments(config.model, 0)
                return [{"label": "Lag Time", "value": True, "disabled": False}], None, False
            except:
                return [{"label": "Lag Time", "value": True, "disabled": False}], None, False

    # callback for peripheral compartments
    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("peripheral-radio", "value"),
        prevent_initial_call=True,
    )
    def peripheral_compartments(n):
        if n is not None:
            config.model = set_peripheral_compartments(config.model, n)
        return True

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("bio_toggle", "value"),
        prevent_initial_call=True,
    )
    def set_bioavailability(toggle):
        if toggle:
            config.model = add_bioavailability(config.model)
            return True
        else:
            config.model = remove_bioavailability(config.model)
            return True

    return
