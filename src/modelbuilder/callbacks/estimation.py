from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
from dash.exceptions import PreventUpdate
import config

from pharmpy.modeling import *
from pharmpy.model import *

import pandas as pd
import numpy as np
import base64
import json
import io
import time
import os


def estimation_callbacks(app):
    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("estimation_btn", "n_clicks"),
        State("estimation_method", "value"),
        State("estimation_index", "value"),
        State("estimation_covs", "value"),
        State("int_eval_lapl", "value"),
        State("solver", "value"),
        State("solver_abstol", "value"),
        State("solver_reltol", "value"),
        State("estimation_keywords", "value"),
        State("estimation_arguments", "value"),
        prevent_initial_call=True,
    )
    def create_estimation_step(
        clicked, method, index, cov, int_ev_lapl, solver, atol, rtol, keywords, arguments
    ):
        keywords_arguments = {}
        if keywords and arguments is not None:
            for key, value in zip(
                json.loads('[' + keywords + ']'), json.loads('[' + arguments + ']')
            ):
                keywords_arguments[key] = value

        checker = ["interaction", "evaluation", "laplace"]
        if int_ev_lapl is not None:
            int_ev_lap_bools = [True if i in checker else False for i in int_ev_lapl]
        else:
            int_ev_lap_bools = [False, False, False]
        inputs = [method, index, cov] + int_ev_lap_bools + [solver, atol, rtol, keywords_arguments]

        default = {
            "method": method,
            "index": None,
            "cov": None,
            "interaction": False,
            "evaluation": False,
            "laplace": False,
            "solver": None,
            "abstol": None,
            "reltol": None,
            "kwargs": None,
        }
        if clicked:
            for key, value in zip(default.keys(), inputs):
                if value is not None or value is not False:
                    default[key] = value
            config.model = add_estimation_step(
                config.model,
                method=default["method"],
                interaction=default["interaction"],
                cov=default["cov"],
                evaluation=default["evaluation"],
                laplace=default["laplace"],
                solver=default["solver"],
                solver_rtol=default["reltol"],
                solver_atol=default["abstol"],
                idx=default["index"],
                tool_options=default["kwargs"],
            )

        return str(config.model.estimation_steps)

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("covariance_check", "value"),
        prevent_initial_call=True,
    )
    def add_covariance(checked):
        if checked:
            config.model = add_covariance_step(config.model)
            True
        else:
            True

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("remove_est_btn", "n_clicks"),
        State("remove_estimation", "value"),
        prevent_initial_call=True,
    )
    def remove_estimation_idx(clicked, index):
        if clicked:
            config.model = remove_estimation_step(config.model, index if index else 0)
            return True
        return True

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("eval_btn", "n_clicks"),
        State("evaluation_index", "value"),
        prevent_initial_call=True,
    )
    def estimation(clicked, index):
        if clicked:
            config.model = set_evaluation_step(config.model, index if index else 0)
            return True
        return True

    @app.callback(
        Output("data_dump", "clear_data", allow_duplicate=True),
        Input("eval_btn", "n_clicks"),
        State("evaluation_index", "value"),
        prevent_initial_call=True,
    )
    def set_eval(clicked, index):
        if clicked:
            config.model = set_evaluation_step(config.model, index if index else -1)
            return True
        return True

    @app.callback(
        Output("data_dump", "clear_data", allow_duplicate=True),
        Input("covariance_check", "value"),
        prevent_initial_call=True,
    )
    def covariance(checked):
        if checked:
            config.model = add_covariance_step(config.model)
            return True
        else:
            config.model = remove_covariance_step(config.model)
            return True

    return
