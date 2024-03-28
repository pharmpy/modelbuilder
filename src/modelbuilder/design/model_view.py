from dash import dcc, html

from .style_elements import (
    create_clipboard,
    create_col,
    create_container,
    create_input_group_button,
    create_options_list,
    create_radio,
    create_text,
    refreshtime,
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
    )
    return create_col([model_format_radio])


def create_model_code_component():
    model_code_text = create_text('output-model')
    model_code_clipboard = create_clipboard('output-model')
    return create_col(
        [
            model_code_clipboard,
            model_code_text,
            # Update interval value to change how often refresh happens
            dcc.Interval(id="text-refresh", interval=refreshtime * 1000, n_intervals=0),
        ]
    )


def create_download_model_component():
    return create_col(
        [
            create_input_group_button('download-btn', 'model_path', 'Save model', 'model path'),
            html.Div(id="model_confirm"),
        ]
    )


model_format_div = create_container(
    [
        create_model_format_component(),
        create_model_code_component(),
        create_download_model_component(),
    ]
)
