from modelbuilder.internals.model_state import ModelState

model_state = ModelState.create('iv')


def make_label_value(key, value):
    return {"label": key, "value": value}
