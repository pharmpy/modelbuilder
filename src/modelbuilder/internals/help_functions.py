from pharmpy.modeling import get_model_code
from pharmpy.model import Model


def render_model_code(model):
    if type(model) != Model:
        return get_model_code(model)
    else:
        text_renderer = _render_generic_model(model)
        return text_renderer


# FIXME: Something similar should be a __repr__ method in Model
def _render_generic_model(model):
    s = ""
    s += "------------------STATEMENTS----------------" + "\n\n"
    s += str(model.statements) + "\n\n"
    s += "------------------ETAS----------------------" + "\n\n"
    s += str(model.random_variables.etas) + "\n\n"
    s += "------------------PARAMETERS----------------" + "\n\n"
    s += str(model.parameters) + "\n\n"

    return s
