import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import dash_bootstrap_components as dbc
import design.main as df
from callbacks.error_model import error_model_callbacks
from callbacks.general import general_callbacks
from callbacks.parameters import parameter_callbacks
from callbacks.structural import structural_callbacks
from dash import Dash

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
structural_callbacks(app)
parameter_callbacks(app)
error_model_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
