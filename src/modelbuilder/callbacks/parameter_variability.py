import ast
import numpy as np
import itertools
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
    create_col_dict,
    create_dropdown,
    create_options_dict,
)


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
                        'Proportional': 'prop',
                        'Exponential': 'exp',
                        'Logit': 'log',
                    },
                    clearable=False,
                )
            ]
            options2 = [create_options_dict({'□': 'False', 'X': 'True'}, clearable=False)] * len(
                col_names
            )
            options = options1 + options2
            dropdown = create_dropdown(['expression'] + col_names, options)

            df = pd.DataFrame(table_dict)
            iiv_data = df.to_dict('records')

            block = config.model_state.block
            if block:
                for i in range(len(block)):
                    bl = block[i]
                    for row in range(len(iiv_data)):
                        if iiv_data[row]['list_of_parameters'] in bl:
                            iiv_data[row][f'corr_{i+1}'] = 'True'

            selected_rows = []
            if rvs:
                for row in range(len(iiv_data)):
                    if iiv_data[row]['list_of_parameters'] in parameter_etas:
                        selected_rows.append(row)
            return iiv_data, selected_rows, columns, dropdown
        else:
            raise PreventUpdate

    @app.callback(
        Output("iov_params_checklist", "options", allow_duplicate=True),
        Output("iov_table", "data"),
        Output("iov_table", "dropdown"),
        Output('dataset_text', 'children'),
        Input('all-tabs', 'value'),
        # Input('iiv_table', 'selected_rows'),
        Input("dataset-path", 'value'),
        State("iov_params_checklist", "value"),
        prevent_initial_call=True,
    )
    def render_iov(tab, data, filename):
        if tab == "par-var-tab":
            parameter_names = [rv['list_of_parameters'] for rv in config.model_state.rvs['iiv']]
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

                occ_opts = config.model_state.occ
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
            return iov_checkboxes_options, iov_data, dropdown_opts, outtext
        else:
            raise PreventUpdate

    @app.callback(
        Output("output-model", "value", allow_duplicate=True),
        Output("iiv_table", "data", allow_duplicate=True),
        Output("iov_table", "selected_rows"),
        Input("iiv_table", "data"),
        Input("iiv_table", "selected_rows"),
        prevent_initial_call=True,
    )
    def set_iivs(data, selected_rows):
        rvs = config.model_state.rvs
        if selected_rows:
            rvs['iov'] = {}
            new_data = []
            for row in selected_rows:
                new_data.append({k: data[row][k] for k in ('list_of_parameters', 'expression')})
            rvs['iiv'] = new_data
            ms = update_model_state(config.model_state, rvs=rvs)
        else:
            rvs['iiv'] = {}
            ms = update_model_state(config.model_state, rvs=rvs)

        if len(selected_rows) > 1:
            block_all = []
            keys = list(data[row].keys())
            for corr_col in keys[2:]:
                block = []
                for row in selected_rows:
                    param = data[row]['list_of_parameters']
                    if data[row][corr_col] == 'True':
                        if param not in itertools.chain.from_iterable(block_all):
                            block.append(param)
                block_all.append(block)
        else:
            block_all = []

        new_block = []
        for bl in block_all:
            if len(bl) < 2:
                bl = []
            new_block.append(bl)

        ms = update_model_state(config.model_state, block=new_block)

        model = ms.generate_model()
        config.model_state = update_ms_from_model(model, ms)
        return render_model_code(model), data, []

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
            # parameter_names = [Expr.symbol(a) for a in iov_checklist]
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
        params = []
        for row in rows:
            params.extend(ast.literal_eval(row['list_of_parameters']))

        new_options = []
        for opt in options:
            if (
                opt['label'] in iiv_params
                and config.model_state.dataset is not None
                and not opt['label'] in params
            ):
                opt['disabled'] = False
            else:
                opt['disabled'] = True
            new_options.append(opt)

        return new_options

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
            rvs['iov'] = {}
            ms = update_model_state(config.model_state, rvs=rvs)
        model = ms.generate_model()
        config.model_state = update_ms_from_model(model, ms)
        return render_model_code(model)
