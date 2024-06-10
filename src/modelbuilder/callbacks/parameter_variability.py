import numpy as np
import pandas as pd
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from pharmpy.modeling import (
    create_joint_distribution,
    get_individual_parameters,
    has_random_effect,
    remove_iiv,
    remove_iov,
    split_joint_distribution,
)

import modelbuilder.config as config
from modelbuilder.internals.model_state import update_model_state, update_ms_from_model
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.design.style_elements import (
    create_options_dropdown,
)


def parameter_variability_callbacks(app):
    @app.callback(
        Output("iiv_table", "data"),
        Output("iiv_table", "selected_rows"),
        Input('all-tabs', 'value'),
        prevent_initial_call=True,
    )
    def render_iiv(tab):
        if tab == "par-var-tab":
            rvs = config.model_state.rvs['iiv']
            parameter_names = config.model_state.individual_parameters
            if rvs:
                parameter_etas = [rv['list_of_parameters'] for rv in config.model_state.rvs['iiv']]
                expr = []
                for param in parameter_names:
                    if param in parameter_etas:
                        for rv in rvs:
                            if param == rv['list_of_parameters']:
                                expr.append(rv['expression'])
                    else:
                        expr.append('exp')
            else:
                expr = 'exp'

            df = pd.DataFrame(
                {
                    'list_of_parameters': parameter_names,
                    'expression': expr,
                }
            )
            iiv_data = df.to_dict('records')

            selected_rows = []
            if rvs:
                for row in range(len(iiv_data)):
                    if iiv_data[row]['list_of_parameters'] in parameter_etas:
                        selected_rows.append(row)
            return iiv_data, selected_rows
        else:
            raise PreventUpdate

    @app.callback(
        Output("iov_params_checklist", "options", allow_duplicate=True),
        Output("occ_dropdown", "options"),
        # Output("radio_iov_dist", "options")
        Input('all-tabs', 'value'),
        Input('iiv_table', 'selected_rows'),
        Input("dataset-path", 'value'),
        State("iov_params_checklist", "value"),
        prevent_initial_call=True,
    )
    def render_iov(tab, selected_rows, data, filename):
        if tab == "par-var-tab":
            parameter_names = [rv['list_of_parameters'] for rv in config.model_state.rvs['iiv']]
            iov_checkboxes_options = config.model_state.individual_parameters
            iov_checkboxes_options = [
                {'label': value, 'value': value, "disabled": True}
                for value in iov_checkboxes_options
            ]

            if config.model_state.dataset is None:
                occ_opts = {}
            else:
                new_iov_checklist = []
                for d in iov_checkboxes_options:
                    if d['value'] in parameter_names:
                        d['disabled'] = False
                    new_iov_checklist.append(d)
                iov_checkboxes_options = new_iov_checklist

                occ_data = config.model_state.occ
                occ_opts = create_options_dropdown([i for i in occ_data if occ_data])

            return iov_checkboxes_options, occ_opts
        else:
            raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("iiv_table", "data"),
        Input("iiv_table", "selected_rows"),
        prevent_initial_call=True,
    )
    def set_iivs(data, selected_rows):
        rvs = config.model_state.rvs
        if selected_rows:
            new_data = [data[row] for row in selected_rows]
            rvs['iiv'] = new_data
            ms = update_model_state(config.model_state, rvs=rvs)
        else:
            ms = config.model_state
        model = ms.generate_model()
        config.model_state = update_ms_from_model(model, ms)
        return render_model_code(model)

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        State("iov_params_checklist", "value"),
        State("occ_dropdown", "value"),
        State('radio_iov_dist', 'value'),
        Input("iov_button", "n_clicks"),
        prevent_initial_call=True,
    )
    def set_iov(iov_checklist, occ_dropdown, iov_dist, n_clicks):
        if n_clicks > 0:
            rvs = config.model_state.rvs
            if iov_checklist and occ_dropdown:
                occ = occ_dropdown
                dist = iov_dist
                print(occ, dist)
                rvs['iov'] = {'list_of_parameters': iov_checklist, 'occ': occ, 'distribution': dist}
                ms = update_model_state(config.model_state, rvs=rvs)
            else:
                ms = config.model_state
            model = ms.generate_model()
            config.model_state = update_ms_from_model(model, ms)
            return render_model_code(model)
        else:
            raise PreventUpdate
