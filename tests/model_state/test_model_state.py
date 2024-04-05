from functools import partial

from pharmpy.modeling import (
    create_basic_pk_model,
    has_additive_error_model,
    has_first_order_absorption,
    has_first_order_elimination,
    has_instantaneous_absorption,
    has_michaelis_menten_elimination,
    has_proportional_error_model,
    has_zero_order_absorption,
    set_additive_error_model,
    set_iiv_on_ruv,
    set_proportional_error_model,
    set_time_varying_error_model,
)
from pharmpy.tools.mfl.parse import get_model_features, parse

from modelbuilder.internals.model_state import ModelState, create_model, update_model


def test_model_state_init():
    model = create_basic_pk_model('iv')
    mfl_str = get_model_features(model)
    mfl = parse(mfl_str, mfl_class=True)
    model_state = ModelState('iv', mfl, (set_proportional_error_model,))
    assert (
        repr(model_state.mfl)
        == 'ABSORPTION(INST);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'
    )


def test_create_model():
    model, model_state = create_model('iv')
    assert has_instantaneous_absorption(model)
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    assert (
        repr(model_state.mfl)
        == 'ABSORPTION(INST);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'
    )
    assert model_state.error_funcs == [set_proportional_error_model]

    model, model_state = create_model('oral')
    assert has_first_order_absorption(model)
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    assert (
        repr(model_state.mfl)
        == 'ABSORPTION(FO);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'
    )
    assert model_state.error_funcs == [set_proportional_error_model]


def test_update_model():
    model, model_state = create_model('iv')
    assert has_first_order_elimination(model)
    model_new, model_state_new = update_model(model, model_state, 'ELIMINATION(MM)')
    assert has_michaelis_menten_elimination(model_new)

    model, model_state = create_model('oral')
    assert has_first_order_absorption(model)
    model_new, model_state_new = update_model(model, model_state, 'ABSORPTION(ZO)')
    assert has_zero_order_absorption(model_new)


def test_update_model_stepwise():
    model, model_state = create_model('iv')
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    model_new, model_state_new = update_model(model, model_state, 'ELIMINATION(MM)')
    model_new, model_state_new = update_model(model_new, model_state_new, set_additive_error_model)
    assert has_michaelis_menten_elimination(model_new)
    assert has_additive_error_model(model_new)


def test_update_model_error():
    model, model_state = create_model('iv')
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    model, model_state = update_model(model, model_state, set_additive_error_model)
    assert has_additive_error_model(model)
    model, model_state = update_model(model, model_state, set_iiv_on_ruv)
    assert 'ETA_RV1' in model.random_variables.names
    y_assignment = model.statements.find_assignment('Y')
    assert '+' in repr(y_assignment)
    model, model_state = update_model(
        model, model_state, partial(set_time_varying_error_model, cutoff=1.0)
    )
    assert 'ETA_RV1' in model.random_variables.names
    y_assignment = model.statements.find_assignment('Y')
    assert 'TIME' in [str(symb) for symb in y_assignment.free_symbols]


def test_update_model_nested():
    model, model_state = create_model('iv')
    assert has_first_order_elimination(model)
    model_new, model_state_new = update_model(model, model_state, 'ELIMINATION(MM)')
    assert has_michaelis_menten_elimination(model_new)
    model_new, model_state_new = update_model(model_new, model_state_new, 'ELIMINATION(FO)')
    assert has_first_order_elimination(model_new)
    model_new, model_state_new = update_model(model_new, model_state_new, 'ELIMINATION(MM)')
    assert has_michaelis_menten_elimination(model_new)
