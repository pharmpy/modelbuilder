import dash_bootstrap_components as dbc
from dash import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
import modelbuilder.config as config
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.internals.model_state import update_model_state, update_ms_from_model

from modelbuilder.design.style_elements import (
    create_options_dropdown,
    create_col_dict,
    create_dropdown,
    create_options_dict,
)


def covariate_callbacks(app):
    @app.callback(
        Output("cov_table", "data"),
        Output("cov_table", "dropdown"),
        Output('error_message', 'children'),
        Input('all-tabs', 'value'),
        Input("dataset-path", 'value'),
        prevent_initial_call=True,
    )
    def initialize_cov(tab, path):
        if tab == "covariate-tab":
            if config.model_state.dataset is None:
                error_message = 'Please provide a dataset in order to add covariates'
            else:
                error_message = ''

            covariates = config.model_state.covariates

            parameter_names = config.model_state.individual_parameters

            columns = [
                create_col_dict('Parameter', 'parameter', presentation='dropdown'),
                create_col_dict('Covariate', 'covariate', presentation='dropdown'),
                create_col_dict('Effect', 'effect', presentation='dropdown'),
                create_col_dict('Operation', 'operation', presentation='dropdown'),
            ]

            options_parameter = [
                create_options_dict({i: i for i in parameter_names}, clearable=False)
            ]
            cov_opts = config.model_state.occ
            options_covariate = [
                create_options_dict({i: i for i in cov_opts if cov_opts}, clearable=False)
            ]
            options_effect = [
                create_options_dict(
                    {
                        'Linear': 'lin',
                        'Cat': 'cat',
                        'Cat 2': 'cat2',
                        'Exponential': 'exp',
                        'Power': 'pow',
                        'Piecewise linear': 'piece_lin',
                    },
                    clearable=False,
                )
            ]
            options_operation = [create_options_dict({'*': '*', '+': '+'}, clearable=False)]
            if config.model_state.dataset is None:
                options_covariate = [create_options_dict({}, clearable=False)]
                options = options_parameter + options_covariate + options_effect + options_operation
                dropdown = create_dropdown(
                    ['parameter', 'covariate', 'effect', 'operation'], options
                )
                cov_data = pd.DataFrame(
                    {
                        'parameter': parameter_names,
                        'covariate': 'None',
                        'effect': 'lin',
                        'operation': '*',
                    }
                )
            else:
                options = options_parameter + options_covariate + options_effect + options_operation
                dropdown = create_dropdown(
                    ['parameter', 'covariate', 'effect', 'operation'], options
                )
                cov_data = pd.DataFrame(
                    {
                        'parameter': parameter_names,
                        'covariate': cov_opts[0],
                        'effect': 'lin',
                        'operation': '*',
                    }
                )

            cov_data = cov_data.to_dict('records')
            if covariates:
                cov_data = covariates

            return cov_data, dropdown, error_message
        else:
            raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Output('error_message', 'children', allow_duplicate=True),
        Input("cov_table", "data"),
        Input("cov_table", "selected_rows"),
        Input('error_message', 'children'),
        prevent_initial_call=True,
    )
    def add_cov(data, selected_rows, error_msg):
        error_message = error_msg
        if selected_rows and config.model_state.dataset is not None:
            error_message = ''
            new_data = [data[row] for row in selected_rows if all(data[row].values())]
            # Make sure that covariate cannot be added to a parameter twice
            combinations = [
                {'parameter': d['parameter'], 'covariate': d['covariate']} for d in new_data
            ]
            combinations = []
            for d in new_data:
                new_dict = {'parameter': d['parameter'], 'covariate': d['covariate']}
                if new_dict in combinations:
                    error_message = f"ERROR. {new_dict['covariate']} has already been added to {new_dict['parameter']}"
                    combinations = None
                    break
                else:
                    combinations.append(new_dict)
            if combinations is not None:
                ms = update_model_state(config.model_state, covariates=new_data)
            else:
                ms = config.model_state
        else:
            ms = update_model_state(config.model_state, covariates=[])
        model = ms.generate_model()
        config.model_state = update_ms_from_model(model, ms)
        return render_model_code(model), error_message

    @app.callback(
        Output("cov_table", "data", allow_duplicate=True),
        Input("cov_btn", "n_clicks"),
        State('cov_table', 'data'),
        State('cov_table', 'columns'),
        prevent_initial_call=True,
    )
    def add_row_to_table(n_clicks, data, columns):
        if n_clicks > 0:
            data.append({c['id']: '' for c in columns})
            return data
        else:
            raise PreventUpdate
