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
from modelbuilder.internals.model_state import update_model_state
from modelbuilder.internals.help_functions import render_model_code


def parameter_variability_callbacks(app):
    @app.callback(
        Output("iiv_table", "data"), Input('all-tabs', 'value'), prevent_initial_call=True
    )
    def render_iiv(tab):
        if tab == "par-var-tab":
            parameter_names = config.model_state.individual_parameters
            rvs = config.model_state.rvs['iiv']
            if rvs:
                inits = [rv['initial_estimate'] for rv in rvs]
                expr = [rv['expression'] for rv in rvs]
            else:
                inits = 0.09
                expr = 'exp'
            df = pd.DataFrame(
                {
                    'list_of_parameters': parameter_names,
                    'initial_estimate': inits,
                    'expression': expr,
                    'operation': '*',
                    'eta_names': None,
                }
            )
            iiv_data = df.to_dict('records')
            return iiv_data
        else:
            raise PreventUpdate

    @app.callback(
        Output("iov_table", "data"),
        Output("iov_table", "dropdown"),
        Input('all-tabs', 'value'),
        prevent_initial_call=True,
    )
    def render_iov(tab):
        if tab == "par-var-tab":
            # parameter_names = [rv['list_of_parameters'] for rv in config.model_state.rvs['iiv']]
            parameter_names = config.model_state.individual_parameters
            iov_data = pd.DataFrame(
                {
                    'list_of_parameters': parameter_names,
                    'distribution': 'disjoint',
                    'eta_names': None,
                }
            )
            iov_data = iov_data.to_dict('records')
            occ_opts = config.model_state.occ

            iov_dd_options = (
                {
                    'occ': {
                        'options': [config.make_label_value(i, i) for i in occ_opts]
                        if occ_opts
                        else []
                    },
                    'distribution': {
                        'options': [
                            {'label': 'disjoint', 'value': 'disjoint'},
                            {'label': 'joint', 'value': 'joint'},
                            {'label': 'explicit', 'value': 'explicit'},
                            {'label': 'Same as IIV', 'value': 'same-as-iiv'},
                        ]
                    },
                },
            )

            return iov_data, iov_dd_options[0]
        else:
            raise PreventUpdate

    @app.callback(
        Output("iov_table", "row_selectable"),
        Input('all-tabs', 'value'),
        State("iov_table", "row_selectable"),
    )
    def check_iov(tab, selectable):
        if tab == "par-var-tab":
            if config.model_state.occ:
                select = "multi"
            else:
                select = False
            return select
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
        config.model_state = ms
        return render_model_code(ms.generate_model())

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Input("iov_table", "data"),
        Input("iov_table", "selected_rows"),
        prevent_initial_call=True,
    )
    def set_iov(data, selected_rows):
        rvs = config.model_state.rvs
        if selected_rows:
            new_data = [data[row] for row in selected_rows]
            rvs['iov'] = new_data
            ms = update_model_state(config.model_state, rvs=rvs)
        else:
            ms = config.model_state
        config.model_state = ms
        return render_model_code(ms.generate_model())

    @app.callback(
        Output("covariance_matrix", "data", allow_duplicate=True),
        Output("covariance_matrix", "columns"),
        Output("covariance_matrix", "style_data_conditional"),
        Output("covariance_matrix", "dropdown"),
        Output("covariance_matrix", "dropdown_conditional"),
        Input("all-tabs", "value"),
        prevent_initial_call=True,
    )
    def get_cov_matrix(tab):
        try:
            model = config.model
            matrix = model.random_variables.etas.names
            data = model.random_variables.etas.covariance_matrix
            df = pd.DataFrame(np.array(data).astype(str), columns=matrix)
            df.replace(str(0), None, inplace=True)
            df = df.applymap(lambda x: 'X' if isinstance(x, str) else x)
            df.insert(0, "parameter", matrix, True)
            data = df.to_dict('records')

            columns = [
                {"name": i, "id": i, "editable": i != "parameter", "presentation": "dropdown"}
                for i in df.columns
            ]

            style_data_conditional = [
                {
                    'if': {
                        'column_id': [matrix[x] for x in range(len(matrix)) if x - i >= 0],
                        'row_index': i,
                    },
                    'backgroundColor': 'gainsboro',
                }
                for i in range(len(matrix))
            ]

            dropdown = {
                i: {
                    'options': [
                        {'label': 'X', 'value': 'X'},
                    ]
                }
                for i in matrix
            }

            dropdown_conditional = [
                {
                    'if': {'column_id': i, 'filter_query': '{parameter} eq "' + str(i) + '"'},
                    'options': [],
                }
                for i in matrix
            ]
            return data, columns, style_data_conditional, dropdown, dropdown_conditional
        except:
            raise PreventUpdate

    @app.callback(
        Output("covariance_matrix", "data", allow_duplicate=True),
        Input("covariance_matrix", "data"),
        prevent_initial_call=True,
    )
    def set_covariance(data):
        d = data
        pairs = {}
        for row in d[::-1]:
            pairs[row["parameter"]] = []
            for key, value in row.items():
                if value == 'X':
                    pairs[row["parameter"]].append(key)

                for second_iter in d[::-1]:
                    if second_iter['parameter'] == key:
                        second_iter.update({row["parameter"]: value})
        for keys in pairs.values():
            config.model = split_joint_distribution(model=config.model, rvs=keys)
            try:
                config.model = create_joint_distribution(model=config.model, rvs=keys)
            except:
                pass
        return data

    return
