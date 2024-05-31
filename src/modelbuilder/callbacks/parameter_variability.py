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
from modelbuilder.design.style_elements import create_dropdown, create_options_dict


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
                inits, expr, eta_names = [], [], []
                for param in parameter_names:
                    if param in parameter_etas:
                        for rv in rvs:
                            if param == rv['list_of_parameters']:
                                inits.append(rv['initial_estimate'])
                                expr.append(rv['expression'])
                                eta_names.append(rv['eta_names'])
                    else:
                        inits.append(0.09)
                        expr.append('exp')
                        eta_names.append(None)
            else:
                inits = 0.09
                expr = 'exp'
                eta_names = None
            df = pd.DataFrame(
                {
                    'list_of_parameters': parameter_names,
                    'initial_estimate': inits,
                    'expression': expr,
                    'operation': '*',
                    'eta_names': eta_names,
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
        Output("iov_table", "data", allow_duplicate=True),
        Output("iov_table", "dropdown", allow_duplicate=True),
        Input('all-tabs', 'value'),
        Input('iiv_table', 'selected_rows'),
        Input("dataset-path", 'value'),
        State("iov_table", "data"),
        prevent_initial_call=True,
    )
    def render_iov(tab, selected_rows, data, filename):
        if tab == "par-var-tab":
            if config.model_state.dataset is None:
                iov_data = pd.DataFrame(
                    {
                        'list_of_parameters': [],
                        'occ': [],
                        'distribution': '',
                        'eta_names': None,
                    }
                )
                iov_dd_options = {}
            else:
                parameter_names = [rv['list_of_parameters'] for rv in config.model_state.rvs['iiv']]
                occ_opts = config.model_state.occ

                iov_dd_options = create_dropdown(
                    ['occ', 'distribution'],
                    [
                        create_options_dict({i: i for i in occ_opts if occ_opts}, clearable=False),
                        create_options_dict(
                            {
                                'disjoint': 'disjoint',
                                'joint': 'joint',
                                'explicit': 'explicit',
                                'Same as IIV': 'same-as-iiv',
                            },
                            clearable=False,
                        ),
                    ],
                )
                iov_data = pd.DataFrame(
                    {
                        'list_of_parameters': parameter_names,
                        'occ': iov_dd_options['occ']['options'][0]['value'],
                        'distribution': 'disjoint',
                        'eta_names': None,
                    }
                )
            iov_data = iov_data.to_dict('records')
            return iov_data, iov_dd_options
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
