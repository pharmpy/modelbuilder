import os
import sys
import webbrowser
from threading import Timer

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

import dash_bootstrap_components as dbc
from dash import Dash

import modelbuilder.design.main as df
from modelbuilder.callbacks.error_model import error_model_callbacks
from modelbuilder.callbacks.general import general_callbacks
from modelbuilder.callbacks.parameters import parameter_callbacks
from modelbuilder.callbacks.structural import structural_callbacks
from modelbuilder.callbacks.parameter_variability import parameter_variability_callbacks

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
parameter_variability_callbacks(app)


def open_browser():
    webbrowser.open_new("http://localhost:8050")


def run():
    Timer(1, open_browser).start()
    app.run_server(debug=True, use_reloader=False)


if __name__ == '__main__':
    run()
