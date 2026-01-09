import ast
import itertools

import pandas as pd
from dash import Input, Output, State, ctx
from dash.exceptions import PreventUpdate
from pharmpy.mfl import IIV, Covariance

import modelbuilder.config as config
from modelbuilder.design.style_elements import (
    create_col_dict,
    create_dropdown,
    create_options_dict,
)
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.internals.model_state import update_model_state


def parameter_variability_callbacks(app):
    @app.callback(
        Output("iiv_table", "data"),
        Output("iiv_table", "selected_rows"),
        Output("iiv_table", "columns"),
        Output("iiv_table", "dropdown"),
        Input('all-tabs', 'value'),
        prevent_initial_call=True,
    )
    def render_iiv(tab):
        if tab == "par-var-tab":
            iivs = config.model_state.mfl.iiv
            parameters_with_iiv = {iiv.parameter: iiv.fp.lower() for iiv in iivs}
            parameter_names = config.model_state.individual_parameters
            if iivs:
                expr = []
                for param in parameter_names:
                    if param in parameters_with_iiv.keys():
                        expr.append(parameters_with_iiv[param])
                    else:
                        expr.append('exp')
            else:
                expr = 'exp'

            table_dict = {'list_of_parameters': parameter_names, 'expression': expr}
            col_names = []
            columns = [
                create_col_dict('Parameter', 'list_of_parameters'),
                create_col_dict('Expression', 'expression', presentation='dropdown'),
            ]
            for i in range(1, len(parameter_names) // 2 + 1):
                col_names.append(f'corr_{i}')
                col = (create_col_dict(f'Block {i}', f'corr_{i}', presentation='dropdown'),)
                columns.append(col[0])
                table_dict[f'corr_{i}'] = 'False'

            options1 = [
                create_options_dict(
                    {
                        'Additive': 'add',
                        # 'Proportional': 'prop',
                        'Exponential': 'exp',
                        # 'Logit': 'log',
                    },
                    clearable=False,
                )
            ]
            options2 = [create_options_dict({' ': 'False', 'X': 'True'}, clearable=False)] * len(
                col_names
            )
            options = options1 + options2
            dropdown = create_dropdown(['expression'] + col_names, options)

            df = pd.DataFrame(table_dict)
            iiv_data = df.to_dict('records')

            block = config.model_state.mfl.covariance
            if block:
                for i, block in enumerate(block):
                    parameters = block.parameters
                    for row in range(len(iiv_data)):
                        if iiv_data[row]['list_of_parameters'] in parameters:
                            iiv_data[row][f'corr_{i+1}'] = 'True'

            selected_rows = []
            if iivs:
                for row in range(len(iiv_data)):
                    if iiv_data[row]['list_of_parameters'] in parameters_with_iiv.keys():
                        selected_rows.append(row)
            return iiv_data, selected_rows, columns, dropdown
        else:
            raise PreventUpdate

    @app.callback(
        Output("iov_params_checklist", "options", allow_duplicate=True),
        Output("iov_table", "data"),
        Output("iov_table", "dropdown"),
        Output('dataset_text', 'children'),
        Output("iov_table", "selected_rows", allow_duplicate=True),
        Input('all-tabs', 'value'),
        Input("dataset-path", 'value'),
        State("iov_params_checklist", "value"),
        prevent_initial_call=True,
    )
    def render_iov(tab, data, filename):
        if tab == "par-var-tab":
            parameter_names = [rv['list_of_parameters'] for rv in config.model_state.iov]
            iov_checkboxes_options = config.model_state.individual_parameters
            iov_checkboxes_options = [
                {'label': value, 'value': value, "disabled": True}
                for value in iov_checkboxes_options
            ]

            if config.model_state.dataset is None:
                iov_data = pd.DataFrame(
                    {
                        'list_of_parameters': [],
                        'occ': [],
                        'distribution': '',
                    }
                )
                dropdown_opts = {}
                outtext = 'Please provide a dataset to add IOVs'
            else:
                new_iov_checklist = []
                for d in iov_checkboxes_options:
                    if d['value'] in parameter_names:
                        d['disabled'] = False
                    new_iov_checklist.append(d)
                iov_checkboxes_options = new_iov_checklist

                occ_opts = config.model_state.col
                outtext = ''
                dropdown_opts = create_dropdown(
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
                        'list_of_parameters': [],
                        'occ': [],
                        'distribution': [],
                    }
                )

            iov_data = iov_data.to_dict('records')

            if config.model_state.iov:
                iov_data = config.model_state.iov
                # Lists must be converted to strings again
                for dicts in iov_data:
                    for keys in dicts:
                        dicts[keys] = str(dicts[keys])
                selected_rows = list(range(len(iov_data)))
            else:
                selected_rows = []
            return iov_checkboxes_options, iov_data, dropdown_opts, outtext, selected_rows
        else:
            raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Output("output-python", "value", allow_duplicate=True),
        Output("output-r", "value", allow_duplicate=True),
        Output("iiv_table", "data", allow_duplicate=True),
        Output("iov_table", "selected_rows"),
        Input("iiv_table", "data"),
        Input("iiv_table", "selected_rows"),
        Input("iov_table", "selected_rows"),
        State("iov_table", "data"),
        prevent_initial_call=True,
    )
    def set_iivs(data, selected_rows, iov_selected_rows, iov_data):
        selected_rows_changed = (
            'iiv_table.selected_rows' in ctx.triggered_prop_ids.keys()
            and 'iiv_table.data' not in ctx.triggered_prop_ids.keys()
        )
        features = []
        if selected_rows:
            # Remove/unselect IOV when IIV is removed
            if selected_rows_changed:
                iiv_params = [data[row]['list_of_parameters'] for row in selected_rows]
                new_iovs = []
                new_iov_selected_rows = []
                for iov_row in iov_selected_rows:
                    params = iov_data[iov_row]['list_of_parameters']
                    if isinstance(params, str):
                        params = ast.literal_eval(params)
                    if set(params) <= set(iiv_params):
                        new_iovs.append(iov_data[iov_row])
                        new_iov_selected_rows.append(iov_row)
                iov_selected_rows = new_iov_selected_rows
                iov = new_iovs
            else:
                iov = {}

            for row in selected_rows:
                parameter = data[row]['list_of_parameters']
                expression = data[row]['expression']
                iiv = IIV.create(parameter, fp=expression, optional=False)
                features.append(iiv)

        else:
            iov_selected_rows = []
            iov = {}

        if len(selected_rows) > 1:
            keys = list(data[row].keys())
            for corr_col in keys[2:]:
                current_block = []
                for row in selected_rows:
                    param = data[row]['list_of_parameters']
                    if data[row][corr_col] == 'True':
                        current_block.append(param)
                if len(current_block) > 1:
                    blocks_new = [
                        Covariance.create(type='IIV', parameters=block)
                        for block in itertools.combinations(current_block, 2)
                    ]
                    features.extend(blocks_new)

        ms = update_model_state(config.model_state, mfl=features, iov=iov, type='variability')

        config.model_state = ms
        return *render_model_code(ms), data, iov_selected_rows

    @app.callback(
        Output("iov_table", "data", allow_duplicate=True),
        Output("iov_params_checklist", 'value'),
        Input("iov_add_button", "n_clicks"),
        State("iov_params_checklist", "value"),
        State('iov_table', 'data'),
        State('iov_table', 'columns'),
        prevent_initial_call=True,
    )
    def add_iov_to_table(n_clicks, iov_checklist, rows, columns):
        if n_clicks > 0 and iov_checklist:
            rows.append(
                {'list_of_parameters': f"{iov_checklist}", 'occ': "ID", 'distribution': "disjoint"}
            )
            return rows, []
        else:
            raise PreventUpdate

    @app.callback(
        Output("iov_params_checklist", "options"),
        Input('iov_table', 'data'),
        Input("iiv_table", "selected_rows"),
        State("iov_params_checklist", "options"),
        State("iiv_table", "data"),
        prevent_initial_call=True,
    )
    def update_checklist(rows, iiv_selected_rows, options, iiv_data):
        iiv_params = [iiv_data[row]['list_of_parameters'] for row in iiv_selected_rows]
        iov_params = []
        for row in rows:
            # NOTE: values in data table cannot be lists. Therefore IOV parameters are strings of lists
            if isinstance(row['list_of_parameters'], str):
                iov_params.extend(ast.literal_eval(row['list_of_parameters']))
            else:
                iov_params.extend(row['list_of_parameters'])

        new_options = []
        for opt in options:
            if (
                opt['label'] in iiv_params
                and config.model_state.dataset is not None
                and not opt['label'] in iov_params
            ):
                opt['disabled'] = False
            else:
                opt['disabled'] = True
            new_options.append(opt)

        return new_options

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Output("output-python", "value", allow_duplicate=True),
        Output("output-r", "value", allow_duplicate=True),
        Output('dataset_text', 'children', allow_duplicate=True),
        Input("iov_table", "data"),
        Input("iov_table", "selected_rows"),
        State('dataset_text', 'children'),
        prevent_initial_call=True,
    )
    def set_iov(data, selected_rows, outtext):
        outtext = outtext
        iivs = config.model_state.mfl.iiv
        iiv_params = [iiv.parameter for iiv in iivs]
        if selected_rows:
            new_data = []
            covariates = []
            if config.model_state.mfl.covariates:
                covariates = [cov.covariate for cov in config.model_state.mfl.covariates]
            for row in selected_rows:
                param = data[row]['list_of_parameters']
                if isinstance(param, str):
                    param = ast.literal_eval(param)
                if not set(param) <= set(iiv_params):
                    outtext = "Cannot add IOV on parameter without IIV! Please add IIV first."
                elif data[row]['occ'] in covariates:
                    outtext = f"{data[row]['occ']} is used as a covariate. Please choose an occasion column instead."
                else:
                    outtext = ''
                    new_data.append(data[row])
            iov = new_data
            ms = update_model_state(config.model_state, iov=iov)
        else:
            iov = {}
            ms = update_model_state(config.model_state, iov=iov)
        config.model_state = ms
        return *render_model_code(ms), outtext
