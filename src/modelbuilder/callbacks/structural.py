from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate

import modelbuilder.config as config
from modelbuilder.design.style_elements import disable_component, enable_component
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.internals.model_state import update_model_state, update_ms_from_model


def structural_callbacks(app):
    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("abs_rate-radio", "value"),
        prevent_initial_call=True,
    )
    def update_abs_rate_on_click(abs_rate):
        if abs_rate:
            mfl = f'ABSORPTION({abs_rate})'
            ms = update_model_state(config.model_state, mfl)
            if ms != config.model_state:
                ms = ms.replace(rvs={'iiv': [], 'iov': []})
                model = ms.generate_model()
                ms = update_ms_from_model(model, ms)
                config.model_state = ms
                return render_model_code(model)
        raise PreventUpdate

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
        if elim:
            mfl = f'ELIMINATION({elim})'
            ms = update_model_state(config.model_state, mfl)
            if ms != config.model_state:
                ms = ms.replace(rvs={'iiv': [], 'iov': []})
                model = ms.generate_model()
                ms = update_ms_from_model(model, ms)
                config.model_state = ms
                return render_model_code(model)
        raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("abs_delay_radio", "value"),
        prevent_initial_call=True,
    )
    def update_abs_delay_on_click(abs_delay):
        if abs_delay:
            mfl = abs_delay
            ms = update_model_state(config.model_state, mfl)
            if ms != config.model_state:
                ms = ms.replace(rvs={'iiv': [], 'iov': []})
                model = ms.generate_model()
                ms = update_ms_from_model(model, ms)
                config.model_state = ms
                return render_model_code(model)
        raise PreventUpdate

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
            ms = update_model_state(config.model_state, mfl)
            if ms != config.model_state:
                ms = ms.replace(rvs={'iiv': [], 'iov': []})
                model = ms.generate_model()
                ms = update_ms_from_model(model, ms)
                config.model_state = ms
                return render_model_code(model)
        raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("pd_expression_radio", "value"),
        Input('pd_effect_radio', 'value'),
        Input('pd_production_radio', 'value'),
        prevent_initial_call=True,
    )
    def update_pd(expr, effect, prod):
        if effect and expr:
            if effect == 'INDIRECTEFFECT':
                if prod:
                    mfl = f'{effect}({expr},{prod})'
            else:
                mfl = f'{effect}({expr})'
                ms = update_model_state(config.model_state, mfl)
                if len(ms.mfl.mfl_statement_list()) != len(
                    config.model_state.mfl.mfl_statement_list()
                ):
                    ms = ms.replace(rvs={'iiv': [], 'iov': []})
                    model = ms.generate_model()
                    ms = update_ms_from_model(model, ms)
                    config.model_state = ms
                    return render_model_code(model)
        else:
            raise PreventUpdate

    @app.callback(
        Output("pd_production_radio", "options"),
        Output("pd_production_radio", "style"),
        Input("pd_effect_radio", "value"),
        Input("model_type", 'value'),
        State("pd_production_radio", "options"),
        State("pd_production_radio", "style"),
    )
    def update_pd_production(effect, model_type, options, style):
        if model_type == 'PD' and effect == 'INDIRECTEFFECT':
            options_new, style_new = enable_component(options, style)
        else:
            options_new, style_new = disable_component(options, style)

        return options_new, style_new

    @app.callback(
        Output("pd_expression_radio", "options"),
        Output("pd_expression_radio", "style"),
        Input("model_type", 'value'),
        State("pd_expression_radio", "options"),
        State("pd_expression_radio", "style"),
    )
    def update_pd_expression(model_type, options, style):
        if model_type == 'PD':
            options_new, style_new = enable_component(options, style)
        else:
            options_new, style_new = disable_component(options, style)

        return options_new, style_new

    @app.callback(
        Output("pd_effect_radio", "options"),
        Output("pd_effect_radio", "style"),
        Input("model_type", 'value'),
        State("pd_effect_radio", "options"),
        State("pd_effect_radio", "style"),
    )
    def update_pd_effect(model_type, options, style):
        if model_type == 'PD':
            options_new, style_new = enable_component(options, style)
        else:
            options_new, style_new = disable_component(options, style)

        return options_new, style_new
