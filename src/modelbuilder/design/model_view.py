from dash import dcc, html

from .style_elements import (
    create_clipboard,
    create_col,
    create_container,
    create_input_group_button,
    create_upload_group_button,
    create_options_list,
    create_radio,
    create_text,
    create_empty_line,
    create_text_component,
)


def create_model_format_component():
    model_format_dict = {
        'generic': 'generic',
        'nlmixr': 'nlmixr',
        'nonmem': 'nonmem',
        'rxode2': 'rxode',
    }
    model_format_options = create_options_list(model_format_dict)

    model_format_radio = create_radio(
        'modelformat',
        model_format_options,
        inputStyle={"font-size": "large", "margin": "10px"},
        inline=True,
        value='nonmem',
    )
    return create_col([model_format_radio, create_empty_line()])


background_color = 'white'
border_color = '#0f8282'
tab_style = {
    'borderTop': 'white',
    'borderBottom': f'1px solid {border_color}',
    'borderLeft': 'white',
    'borderRight': 'white',
    'backgroundColor': background_color,
    'color': '#0f8282',
    'border-top-right-radius': '10px',
    'border-top-left-radius': '10px',
}
tab_selected_style = {
    'borderTop': f'1px solid {border_color}',
    'borderLeft': f'1px solid {border_color}',
    'borderRight': f'1px solid {border_color}',
    'backgroundColor': 'white',
    'color': '#0f8282',
    'border-top-right-radius': '10px',
    'border-top-left-radius': '10px',
}
text_style = {
    'font-family': 'monospace',
    'resize': 'None',
    'height': '70vh',
    'fontSize': '12px',
    "backgroundColor": '#ffffff',
    'overflow-x': 'auto',
    'white-space': 'pre',
    'borderTop': 'white',
    'borderLeft': f'1px solid {border_color}',
    'borderRight': f'1px solid {border_color}',
    'borderBottom': f'1px solid {border_color}',
    'border-top-right-radius': '0',
    'border-top-left-radius': '0',
}


def create_model_code_component():
    model_code_text = create_text('output-model', style=text_style)
    model_code_clipboard = create_clipboard('output-model')
    python_code_text = create_text('output-python', style=text_style)
    python_code_clipboard = create_clipboard('output-python')
    r_code_text = create_text('output-r', style=text_style)
    r_code_clipboard = create_clipboard('output-r')

    tabs = dcc.Tabs(
        id="model-view-tabs",
        value='output-model',
        children=[
            dcc.Tab(
                label='Model',
                value='output-model',
                children=[model_code_clipboard, model_code_text, html.Br()],
                style=tab_style,
                selected_style=tab_selected_style,
            ),
            dcc.Tab(
                label='Python',
                value='output-python',
                children=[python_code_clipboard, python_code_text, html.Br()],
                style=tab_style,
                selected_style=tab_selected_style,
            ),
            dcc.Tab(
                label='R',
                value='output-r',
                children=[r_code_clipboard, r_code_text, html.Br()],
                style=tab_style,
                selected_style=tab_selected_style,
            ),
        ],
        style={'margin-bottom': '-24px'},
    )

    return tabs


def create_download_model_component():
    return create_col(
        [
            create_input_group_button('download-btn', 'model_path', 'Save model', 'model path'),
            html.Div(id="model_confirm"),
            html.Br(),
        ]
    )


def create_load_dataset_component():
    return create_col(
        [
            create_upload_group_button(
                'upload-dataset', 'dataset-path', 'Load dataset', 'No dataset'
            ),
            html.Div(id="load-dataset"),
        ]
    )


model_format_div = create_container(
    [
        create_model_format_component(),
        create_model_code_component(),
        create_download_model_component(),
        create_load_dataset_component(),
    ]
)
