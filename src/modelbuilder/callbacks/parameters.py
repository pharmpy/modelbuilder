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


def fix_blocks(rvs, data):
    blocks = [rv.parameter_names for rv in rvs if isinstance(rv, JointNormalDistribution)]

    params_in_block = []
    for item in data:
        for key, value in item.items():
            if key == 'fix' and value == True:
                param = item['name']
                for block in blocks:
                    if param in block:
                        params_in_block.append(block)

    for block in params_in_block:
        for param in block:
            for item in data:
                if str(item['name']) == param:
                    item['fix'] = True
    return data


def parameter_callbacks(app):
    # Getting the model parameters
    @app.callback(
        Output("parameter-table", "data"),
        Input("route-radio", "value"),
    )
    def create_table(route):
        if route:
            return config.model_state.parameters.to_dict()['parameters']

    @app.callback(
        Output("parameter-table", "data", allow_duplicate=True),
        Output("output-model", "value", allow_duplicate=True),
        Input("parameter-table", "data"),
        prevent_initial_call=True,
    )
    def update_table(data):
        data = replace_empty(data)

        # data = fix_blocks(model.random_variables, data)
        ms = update_model_state(config.model_state, parameters=data)
        config.model_state = ms

        return data, render_model_code(ms.generate_model())
