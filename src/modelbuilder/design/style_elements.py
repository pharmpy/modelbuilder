import dash_bootstrap_components as dbc
from dash import dcc, html

btn_color = "info"
badge_color = "info"
refreshtime = 1  # How often the model-code refreshes seconds


def create_options_list(dict_original, disabled=False):
    return [
        {'label': key, 'value': value, 'disabled': disabled} for key, value in dict_original.items()
    ]


def create_badge(text, with_textbox=False):
    if with_textbox:
        style = {"width": 150, 'fontSize': 'medium'}
    else:
        style = {"font-size": "large"}
    return dbc.Badge(text, color="success", style=style)


def create_radio(elem_id, options):
    style = {"font-size": "large"}
    return dcc.RadioItems(options=options, id=elem_id, style=style)


def create_checklist(elem_id, options):
    return dbc.Checklist(
        options=options,
        id=elem_id,
    )


def create_input_group(elem_id, input_group_text, default_value, **kwargs):
    style = {"width": "70%"}
    return dbc.InputGroup(
        children=[
            dbc.InputGroupText(input_group_text),
            dbc.Input(id=elem_id, placeholder=default_value, **kwargs),
        ],
        style=style,
    )


def create_col(children, **kwargs):
    return dbc.Col(children=children, **kwargs)


def create_container(rows):
    return dbc.Container([html.Br(), *[dbc.Row(row) for row in rows]])


def disable_component(options, style=None):
    options_new = [{**dictionary, 'disabled': True} for dictionary in options]
    style_new = {**style, 'opacity': 0.42} if style else None
    return options_new, style_new


def enable_component(options, style=None):
    options_new = [{**dictionary, 'disabled': False} for dictionary in options]
    style_new = {**style, 'opacity': 1.0} if style else None
    return options_new, style_new
