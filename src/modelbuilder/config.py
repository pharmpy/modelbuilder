from modelbuilder.internals.model_state import create_model

model, model_state = create_model('iv')


def make_label_value(key, value):
    return {"label": key, "value": value}
