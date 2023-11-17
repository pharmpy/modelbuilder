from .style_elements import btn_color, refreshtime, create_badge

from dash import html, dcc
import dash_bootstrap_components as dbc

modelformats = [
    {"label": "generic", "value": "generic"},
    {"label": "nlmixr", "value": "nlmixr"},
    {"label": "nonmem", "value": "nonmem"},
    {"label": "rxode2", "value": "rxode"},
]

model_format_radio = dbc.Col(
    children=[
        create_badge("Model view"),
        dcc.RadioItems(
            modelformats,
            'nonmem',
            id='modelformat',
            inputStyle={"font-size": "large", "margin": "10px"},
            inline=True,
        ),
    ]
)

collapsable_model = dbc.Collapse(model_format_radio, id="collapse_model", is_open=True)

model_output_text = html.Div(
    [
        dcc.Clipboard(
            target_id="output-model",
            title="copy",
            style={
                "position": "relative",
                "top": "5vh",
                "right": "-29vw",
                'width': '5vw',
                'cursor': 'pointer',
            },
        ),
        dbc.Textarea(
            id="output-model",
            readOnly=True,
            style={
                'font-family': 'monospace',
                'resize': 'None',
                'height': '70vh',
                'fontSize': '12px',
                "backgroundColor": '#ffffff',
                'overflow-x': 'auto',
                'white-space': 'pre',
            },
        ),
        # Update interval value to change how often refresh happens
        dcc.Interval(id="text-refresh", interval=refreshtime * 1000, n_intervals=0),
    ]
)

download_model = dbc.Container(
    [
        dbc.InputGroup(
            [
                dbc.Button(
                    "Save model", id="download-btn", color=btn_color, style={"fontSize": "medium"}
                ),
                dbc.Input(id="model_path", placeholder="model path"),
            ]
        ),
        html.Div(id="model_confirm"),
    ]
)

model_format_div = html.Div(
    children=[
        html.Hr(),
        model_format_radio,
        model_output_text,
        download_model,
    ]
)
