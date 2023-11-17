import dash_bootstrap_components as dbc

btn_color = "info"
badge_color = "info"
refreshtime = 1  # How often the model-code refreshes seconds


def create_badge(text, with_textbox=False):
    if with_textbox:
        style = {"width": 150, 'fontSize': 'medium'}
    else:
        style = {"font-size": "large"}
    return dbc.Badge(text, color="success", style=style)
