import dash_bootstrap_components as dbc
from dash import dash_table, dcc, html

success_color = '#18bc9c'
pharmpy_color = '#0f8282'
main_color = pharmpy_color
btn_color = "info"
badge_color = "info"
refreshtime = 1  # How often the model-code refreshes seconds


def create_empty_line():
    return html.Br()


def create_header(text):
    line = html.Hr(style={'height': '2px', 'background': 'grey', 'color': 'grey'})
    header = html.Header(text, style={'color': main_color, 'font-size': 30})
    return create_col([header, line])


def create_options_list(dict_original, disabled=False):
    return [
        {'label': " " + key, 'value': value, 'disabled': disabled}
        for key, value in dict_original.items()
    ]


def create_options_dropdown(list_original):
    return [{'label': i, 'value': i} for i in list_original]


def create_options_dict(dict_original, **kwargs):
    d = [{'label': key, 'value': value} for key, value in dict_original.items()]
    return {'options': d, **kwargs}


def create_col_dict(name, id, **kwargs):
    return {'name': name, 'id': id, **kwargs}


def create_badge(text, with_textbox=False):
    if with_textbox:
        style = {"width": 150, 'fontSize': 'large', 'padding': '15px'}
    else:
        style = {"font-size": "large"}
    return dbc.Badge(text, color=main_color, style=style)


def create_radio(elem_id, options, style=None, **kwargs):
    if not style:
        style = {"font-size": "large"}
    return dcc.RadioItems(options=options, id=elem_id, style=style, **kwargs)


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


def create_input_group_button(button_id, input_id, button_text, default_value):
    style = {"fontSize": "medium"}
    return dbc.InputGroup(
        [
            dbc.Button(button_text, id=button_id, color=btn_color, style=style),
            dbc.Input(id=input_id, placeholder=default_value),
        ]
    )


def create_upload_group_button(button_id, input_id, button_text, default_value):
    style = {"fontSize": "medium"}
    return dbc.InputGroup(
        [
            dcc.Upload(dbc.Button(button_text, color=btn_color), id=button_id, style=style),
            dbc.Input(id=input_id, placeholder=default_value),
        ]
    )


def create_button(button_id, button_text, color=btn_color):
    style = {'fontsize': 'medium'}
    return dbc.Button(button_text, id=button_id, color=color, style=style, n_clicks=0)


def create_text(elem_id):
    style = {
        'font-family': 'monospace',
        'resize': 'None',
        'height': '70vh',
        'fontSize': '12px',
        "backgroundColor": '#ffffff',
        'overflow-x': 'auto',
        'white-space': 'pre',
    }
    return dbc.Textarea(id=elem_id, readOnly=True, style=style)


def create_clipboard(target_id):
    style = {
        "position": "relative",
        "top": "5vh",
        "right": "-29vw",
        'width': '5vw',
        'cursor': 'pointer',
    }
    return dcc.Clipboard(target_id=target_id, title="copy", style=style)


def create_text_input(elem_id, label, placeholder):
    label_badge = create_badge(label, with_textbox=True)
    input_text = dbc.Input(id=elem_id, placeholder=placeholder, type="text")
    return dbc.InputGroup([label_badge, input_text], style={"margin-bottom": "5px"})


def create_col(children, **kwargs):
    return dbc.Col(children=children, **kwargs)


def create_container(rows, **kwargs):
    return dbc.Container([html.Br(), *[dbc.Row(row) for row in rows]], **kwargs)


def disable_component(options, style=None):
    options_new = [{**dictionary, 'disabled': True} for dictionary in options]
    style_new = {**style, 'opacity': 0.42} if style else None
    return options_new, style_new


def enable_component(options, style=None):
    options_new = [{**dictionary, 'disabled': False} for dictionary in options]
    style_new = {**style, 'opacity': 1.0} if style else None
    return options_new, style_new


def create_dropdown(names, options):
    return {name: option for (name, option) in zip(names, options)}


def create_table(ID, COL, **kwargs):
    table = dash_table.DataTable(
        id=ID,
        columns=COL,
        editable=True,
        style_data_conditional=[
            {
                'if': {'state': 'active'},
                'backgroundColor': '#44bdbd',
                'border': f'1px solid {main_color}',
            },
            {'if': {'column_type': 'numeric'}, 'textAlign': 'right'},
        ],
        style_cell={'textAlign': 'left', 'width': '20%'},
        css=[
            {
                "selector": ".dash-spreadsheet .Select-option",
                "rule": f"color: {main_color}",
            },
        ],
        **kwargs,
    )
    return table


def create_dropdown_component(ID, options, clearable=False):
    return dcc.Dropdown(options=options, id=ID, clearable=clearable, style={'color': pharmpy_color})


def create_number_input(ID, MIN=0, MAX=100, STEP=1, PLACEHOLDER="", **kwargs):
    return dcc.Input(
        id=ID, type='number', min=MIN, max=MAX, step=STEP, placeholder=PLACEHOLDER, **kwargs
    )


def create_text_component(ID, text, **kwargs):
    return html.Div(id=ID, children=text, **kwargs)
