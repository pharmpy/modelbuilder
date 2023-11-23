from dash import Dash, html, dcc, callback, Output, Input, State, dash_table
import config
from pharmpy.modeling import *
from pharmpy.model import *
import dash_bootstrap_components as dbc
import designfile as df
from dash.exceptions import PreventUpdate

from callbacks.general import general_callbacks
from callbacks.datainfo import datainfo_callbacks
from callbacks.structural import structural_callbacks
from callbacks.parameters import parameter_callbacks
from callbacks.parameter_variability import parameter_variability_callbacks
from callbacks.error_model import error_model_callbacks
from callbacks.covariates import covariate_callbacks
from callbacks.allometry import allometry_callbacks
from callbacks.estimation import estimation_callbacks

import pandas as pd
import numpy as np
import base64
import json
import io
import time
import os

PHARMPY_LOGO = "https://pharmpy.github.io/latest/_images/Pharmpy_logo.svg"

app = Dash(
    __name__,
    title="Model Builder",
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    update_title=None,
)

app.layout = df.layout

general_callbacks(app)
datainfo_callbacks(app)
structural_callbacks(app)
parameter_callbacks(app)
parameter_variability_callbacks(app)
error_model_callbacks(app)
covariate_callbacks(app)
allometry_callbacks(app)
estimation_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
