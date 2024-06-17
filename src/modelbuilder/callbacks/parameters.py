import json

from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from pharmpy.model import JointNormalDistribution, Parameters
from pharmpy.modeling import fix_parameters, unfix_parameters

import modelbuilder.config as config
from modelbuilder.internals.help_functions import render_model_code
from modelbuilder.internals.model_state import update_model_state


def check_all_same(p):  # p = model_parameters_to_dict["parameters"])
    if p:
        ref = p[0]['fix']
        for parameter in p:
            if parameter['fix'] is not ref:
                return False
        return True


def replace_empty(data):
    for item in data:
        for key, value in item.items():
            if value is None:
                if key == "lower":
                    item[key] = float("-inf")
                elif key == "upper":
                    item[key] = float("inf")
    return data


def fix_blocks(data):
    old_params = config.model_state.parameters
    ms = update_model_state(config.model_state, parameters=data)
    model = ms.generate_model()
    rvs = model.random_variables
    blocks = [rv.parameter_names for rv in rvs if isinstance(rv, JointNormalDistribution)]

    for block in blocks:
        old_param = old_params[block[0]].name
        old_fix = old_params[block[0]].fix
        for param in data:
            if param['name'] in block:
                new_fix = param['fix']
                if old_fix != new_fix:
                    for param in data:
                        if param['name'] in block:
                            param['fix'] = new_fix
    return data


def parameter_callbacks(app):
    # Getting the model parameters
    @app.callback(
        Output("parameter-table", "data"),
        Input('all-tabs', 'value'),
    )
    def create_table(tab):
        return config.model_state.parameters.to_dict()['parameters']

    @app.callback(
        Output("parameter-table", "data", allow_duplicate=True),
        Output("output-model", "value", allow_duplicate=True),
        Input("parameter-table", "data"),
        prevent_initial_call=True,
    )
    def update_table(data):
        data = replace_empty(data)

        data = fix_blocks(data)
        ms = update_model_state(config.model_state, parameters=data)
        config.model_state = ms

        return data, render_model_code(ms.generate_model())
