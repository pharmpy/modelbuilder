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
                ms = ms.replace(rvs={'iiv': [], 'iov': []}, block=[])
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
                ms = ms.replace(rvs={'iiv': [], 'iov': []}, block=[])
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
                ms = ms.replace(rvs={'iiv': [], 'iov': []}, block=[])
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
            # FIXME: Workaround to reset to PK model
            mfl_pk = config.model_state.mfl.filter('pk')
            ms_pk = config.model_state.replace(mfl=mfl_pk)
            if effect == 'INDIRECTEFFECT':
                if prod:
                    mfl = f'{effect}({expr},{prod})'
            else:
                mfl = f'{effect}({expr})'
            ms = update_model_state(ms_pk, mfl)
            ms = ms.replace(rvs={'iiv': [], 'iov': []}, block=[])
            model = ms.generate_model()
            ms = update_ms_from_model(model, ms)
            config.model_state = ms
            return render_model_code(model)
        else:
            raise PreventUpdate

    @app.callback(
        Output("pd_expression_radio", "options"),
        Output("pd_expression_radio", "style"),
        Output("pd_effect_radio", "options"),
        Output("pd_effect_radio", "style"),
        Output("pd_production_radio", "options"),
        Output("pd_production_radio", "style"),
        Input("model_type", 'value'),
        Input("pd_effect_radio", "value"),
        State("pd_expression_radio", "options"),
        State("pd_expression_radio", "style"),
        State("pd_effect_radio", "options"),
        State("pd_effect_radio", "style"),
        State("pd_production_radio", "options"),
        State("pd_production_radio", "style"),
    )
    def update_pd_radio(
        model_type,
        effect,
        options_expr,
        style_expr,
        options_eff,
        style_eff,
        options_prod,
        style_prod,
    ):
        if model_type == 'PD':
            options_new_expr, style_new_expr = enable_component(options_expr, style_expr)
            options_new_eff, style_new_eff = enable_component(options_eff, style_eff)
            if effect == 'INDIRECTEFFECT':
                options_new_prod, style_new_prod = enable_component(options_prod, style_prod)
            else:
                options_new_prod, style_new_prod = disable_component(options_prod, style_prod)
        else:
            options_new_expr, style_new_expr = disable_component(options_expr, style_expr)
            options_new_eff, style_new_eff = disable_component(options_eff, style_eff)
            options_new_prod, style_new_prod = disable_component(options_prod, style_prod)

        return (
            options_new_expr,
            style_new_expr,
            options_new_eff,
            style_new_eff,
            options_new_prod,
            style_new_prod,
        )
