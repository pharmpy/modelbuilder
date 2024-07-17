from pharmpy.modeling import get_model_code
from pharmpy.model import Model

# from functools import partial
from .model_state import ModelState


def render_model_code(ms: ModelState):
    return (
        _render_model_code(ms.generate_model()),
        ms.generate_code('python'),
        ms.generate_code('r'),
    )


def _render_model_code(model):
    if type(model) != Model:
        return get_model_code(model)
    else:
        text_renderer = _render_generic_model(model)
        return text_renderer


# FIXME: Something similar should be a __repr__ method in Model
def _render_generic_model(model):
    s = ""
    s += "-----------STATEMENTS BEFORE ODE------------" + "\n\n"
    s += str(model.statements.before_odes) + "\n\n"
    s += "--------------------ODE---------------------" + "\n\n"
    s += str(model.statements.ode_system) + "\n\n"
    s += "-------------------ERROR--------------------" + "\n\n"
    s += str(model.statements.error) + "\n\n"
    s += "--------------------ETAS--------------------" + "\n\n"
    s += str(model.random_variables.etas) + "\n\n"
    s += "-----------------PARAMETERS-----------------" + "\n\n"
    s += str(model.parameters) + "\n\n"

    return s
