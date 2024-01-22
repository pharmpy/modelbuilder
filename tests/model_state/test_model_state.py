from modelbuilder.internals.model_state import ModelState, create_model, update_model

from pharmpy.modeling import has_instantaneous_absorption, has_first_order_absorption, has_first_order_elimination, create_basic_pk_model, has_michaelis_menten_elimination


def test_model_state_init():
    model = create_basic_pk_model('iv')
    model_state = ModelState('iv', model)
    assert repr(model_state.mfl) == 'ABSORPTION(INST);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'


def test_create_model():
    model, model_state = create_model('iv')
    assert has_instantaneous_absorption(model)
    assert has_first_order_elimination(model)
    assert repr(model_state.mfl) == 'ABSORPTION(INST);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'

    model, model_state = create_model('oral')
    assert has_first_order_absorption(model)
    assert has_first_order_elimination(model)
    assert repr(model_state.mfl) == 'ABSORPTION(FO);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'


def test_update_model():
    model, model_state = create_model('iv')
    model_new, model_state_new = update_model(model, model_state, 'ELIMINATION(MM)')
    assert not has_first_order_elimination(model_new)
    assert has_michaelis_menten_elimination(model_new)

