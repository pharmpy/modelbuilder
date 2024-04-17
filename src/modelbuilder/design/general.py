from .style_elements import (
    create_badge,
    create_col,
    create_container,
    create_options_list,
    create_radio,
    create_text_input,
)


def create_type_component():
    type_label_dict = {'PK': 'PK'}

    type_badge = create_badge('Model type')
    type_options = create_options_list(type_label_dict)
    type_radio = create_radio('model_type', options=type_options)

    return create_col([type_badge, type_radio])


def create_route_component():
    route_label_dict = {'IV': 'iv', 'Oral': 'oral'}

    route_badge = create_badge('Administration route')
    route_options = create_options_list(route_label_dict)
    route_radio = create_radio('route-radio', options=route_options, value='iv')

    return create_col([route_badge, route_radio])


name_component = create_text_input('model-name', 'Name', 'Write model name here...')
description_component = create_text_input(
    'model-description', 'Description', 'Write model description here...'
)

type_component = create_type_component()
route_component = create_route_component()


general_tab = create_container(
    [[name_component], [description_component], [type_component], [route_component]]
)
