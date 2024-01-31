from dash import Input, Output, State, ctx
from pharmpy.modeling import (
    add_lag_time,
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
        Input("route-radio", "value"),
    )
    def reset_defaults(route):
        if route == "iv":
            default_abs_rate = 0
        else:
            default_abs_rate = 'FO'
        default_elim = 'FO'
        default_peripherals = 0
        return default_abs_rate, default_elim, default_peripherals

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
        Output("lag-toggle", "options"),
        Output("transit_input", "value"),
        Output("transit_input", "disabled"),
        Input("route-radio", "value"),
        Input("lag-toggle", "options"),
        Input("lag-toggle", "value"),
        Input("transit_input", "value"),
    )
    def update_abs_delay(route, lag_options, set_lag_time, no_of_transits):
        click_id = ctx.triggered_id

        if not click_id or click_id == 'route-radio':
            lag_options_new, transit_value, transit_disabled = _update_abs_delay_from_route(
                route, lag_options
            )
        else:
            lag_options_new, transit_value, transit_disabled = _update_abs_delay_on_click(
                lag_options, set_lag_time, no_of_transits
            )

        return lag_options_new, transit_value, transit_disabled

    def _update_abs_delay_from_route(route, lag_options):
        if route == 'iv':
            lag_options_new, _ = disable_component(lag_options)
            transit_disabled = True
        else:
            lag_options_new, _ = enable_component(lag_options)
            transit_disabled = False
        transit_value = 0
        return lag_options_new, transit_value, transit_disabled

    def _update_abs_delay_on_click(lag_options, set_lag_time, no_of_transits):
        if set_lag_time:
            # FIXME: This should be a value and not a list?
            set_lag_time = set_lag_time[0]
            if set_lag_time is True:
                config.model = set_transit_compartments(config.model, 0)
                config.model = add_lag_time(config.model)
            elif set_lag_time is False:
                config.model = remove_lag_time(config.model)
            lag_options_new = lag_options
            transit_value, transit_disabled = 0, True
        elif no_of_transits is not None:
            config.model = remove_lag_time(config.model)
            config.model = set_transit_compartments(config.model, no_of_transits)
            if no_of_transits > 0:
                lag_options_new, _ = disable_component(lag_options)
            else:
                lag_options_new, _ = enable_component(lag_options)
            transit_value, transit_disabled = no_of_transits, False
        else:
            lag_options_new = lag_options
            transit_value, transit_disabled = 0, False

        return lag_options_new, transit_value, transit_disabled

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
