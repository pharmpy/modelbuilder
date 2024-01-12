import pandas as pd
from dash import Input, Output
from dash.exceptions import PreventUpdate

import modelbuilder.config as config


def datainfo_callbacks(app):
    @app.callback(Output("datatable", "data"), Input("all-tabs", "value"))
    def render_datatable(tab):
        if tab == "data-info-tab":
            try:
                datainf = config.model.datainfo.to_dict()
                df = pd.DataFrame(datainf["columns"])
                usable = df.to_dict('records')
                return usable
            except:
                PreventUpdate

    @app.callback(
        Output("data-dump", "clear_data", allow_duplicate=True),
        Input("datatable", "data"),
        prevent_initial_call=True,
    )
    def update_datainf(data):
        try:
            datainf = config.model.datainfo.to_dict()
            datainf["columns"] = data
            datainf = config.model.datainfo.from_dict(datainf)
            config.model = config.model.replace(datainfo=datainf)
            return True
        except:
            raise PreventUpdate

    @app.callback(Output("download_dtainf", "data"), Input("makedatainf", "n_clicks"))
    def makeNone(clicked):
        if clicked:
            return dict(
                content=config.model.datainfo.to_json(), filename=config.model.name + ".datainfo"
            )

    return
