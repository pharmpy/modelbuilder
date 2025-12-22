from pharmpy.modeling import (
    create_basic_pk_model,
    has_additive_error_model,
    has_covariate_effect,
    has_first_order_absorption,
    has_first_order_elimination,
    has_instantaneous_absorption,
    has_michaelis_menten_elimination,
    has_proportional_error_model,
    has_zero_order_absorption,
    load_example_model,
)
from pharmpy.tools.mfl.parse import get_model_features, parse

from modelbuilder.internals.model_state import ModelState, update_model_state


def test_model_state_init():
    model = create_basic_pk_model('iv')
    mfl_str = get_model_features(model)
    mfl = parse(mfl_str, mfl_class=True)
    model_state = ModelState('iv', 'nonmem', {}, mfl, ['prop'], model.parameters)
    assert (
        repr(model_state.mfl)
        == 'ABSORPTION(INST);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'
    )
    assert model_state.error_funcs == ['prop']
    assert len(model_state.parameters) == 6


def test_create_model():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert has_instantaneous_absorption(model)
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    assert (
        repr(model_state.mfl)
        == 'ABSORPTION(INST);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'
    )
    assert model_state.error_funcs == {1: ['prop']}
    assert len(model_state.parameters) == 6
    assert len(model_state.parameters) == len(model.parameters)

    model_state = ModelState.create('oral')
    model = model_state.generate_model()
    assert has_first_order_absorption(model)
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    assert (
        repr(model_state.mfl)
        == 'ABSORPTION(FO);ELIMINATION(FO);TRANSITS(0);PERIPHERALS(0);LAGTIME(OFF)'
    )
    assert model_state.error_funcs == {1: ['prop']}
    assert len(model_state.parameters) == len(model.parameters)


def test_update_model():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert has_first_order_elimination(model)
    model_state_new = update_model_state(model_state, 'ELIMINATION(MM)')
    model_new = model_state_new.generate_model()
    assert has_michaelis_menten_elimination(model_new)

    model_state = ModelState.create('oral')
    model = model_state.generate_model()
    assert has_first_order_absorption(model)
    model_state_new = update_model_state(model_state, 'ABSORPTION(ZO)')
    model_new = model_state_new.generate_model()
    assert has_zero_order_absorption(model_new)

    example_model = load_example_model('pheno')
    dataset, datainfo = example_model.dataset, example_model.datainfo
    model_state = ModelState.create('oral')
    model = model_state.generate_model(dataset, datainfo)
    assert has_first_order_absorption(model)
    model_state_new = update_model_state(model_state, 'COVARIATE(CL,WGT,exp)')
    model_new = model_state_new.generate_model(dataset, datainfo)
    assert has_covariate_effect(model_new, 'CL', 'WGT')


def test_update_model_stepwise():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    model_state_new = update_model_state(model_state, 'ELIMINATION(MM)')
    model_state_new = update_model_state(model_state_new, error={1: 'add'})
    model_new = model_state_new.generate_model()
    assert has_michaelis_menten_elimination(model_new)
    assert has_additive_error_model(model_new)


def test_update_model_structural():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert has_first_order_elimination(model)
    model_state_new = update_model_state(model_state, 'ELIMINATION(MM)')
    model_new = model_state_new.generate_model()
    assert has_michaelis_menten_elimination(model_new)
    model_state_new = update_model_state(model_state_new, 'ELIMINATION(FO)')
    model_new = model_state_new.generate_model()
    assert has_first_order_elimination(model_new)
    model_state_new = update_model_state(model_state_new, 'ELIMINATION(MM)')
    model_new = model_state_new.generate_model()
    assert has_michaelis_menten_elimination(model_new)


def test_update_model_error():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    model_state = update_model_state(model_state, error={1: 'add'})
    model = model_state.generate_model()
    assert has_additive_error_model(model)
    model_state = update_model_state(model_state, error={1: 'iiv-on-ruv'})
    model = model_state.generate_model()
    assert 'ETA_RV1' in model.random_variables.names
    y_assignment = model.statements.find_assignment('Y')
    assert '+' in repr(y_assignment)
    model_state = update_model_state(model_state, error={1: 'iiv-on-ruv;time-varying'})
    model = model_state.generate_model()
    assert 'ETA_RV1' in model.random_variables.names
    y_assignment = model.statements.find_assignment('Y')
    assert 'TIME' in [str(symb) for symb in y_assignment.free_symbols]
    model_state = update_model_state(model_state, error={1: ''})
    model = model_state.generate_model()
    assert has_additive_error_model(model)
    assert 'ETA_RV1' not in model.random_variables.names

    model_state = ModelState.create('iv')
    model_state = update_model_state(model_state, 'DIRECTEFFECT(LINEAR)')
    model_state = update_model_state(model_state, error={1: 'add', 2: 'add'})
    model = model_state.generate_model()
    assert has_additive_error_model(model, dv=1)
    assert has_additive_error_model(model, dv=2)
    model_state = update_model_state(model_state, error={1: 'prop', 2: 'add'})
    model = model_state.generate_model()
    assert has_proportional_error_model(model, dv=1)
    assert has_additive_error_model(model, dv=2)


def test_update_model_parameters():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    parameters = (
        {'name': 'POP_CL', 'init': 10.0, 'upper': 0.0, 'lower': 12.0, 'fix': False},
    ) + model_state.parameters[1:].to_dict()['parameters']
    model_state_new = update_model_state(model_state, parameters=parameters)
    model_new = model_state_new.generate_model()
    assert len(model_new.parameters) == 6
    assert model_new.parameters['POP_CL'].init != model.parameters['POP_CL'].init


def test_update_model_attrs():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert model.name == 'start'
    model_state_new = update_model_state(model_state, model_attrs={'name': 'new_name'})
    model_new = model_state_new.generate_model()
    assert model_new.name == 'new_name'
    model_state_new = update_model_state(model_state, model_attrs={'description': 'something'})
    model_new = model_state_new.generate_model()
    assert model_new.description != model.description


def test_update_model_rvs():
    model_state = ModelState.create('iv')
    rvs = {'iiv': [{'list_of_parameters': 'CL', 'expression': 'add'}], 'iov': []}
    model_state_new = update_model_state(model_state, rvs=rvs)
    model_state_new = update_model_state(model_state_new, block=[['CL']])
    model_new = model_state_new.generate_model()
    assert model_new.random_variables.iiv.names == ('ETA_CL',)


def test_update_model_block():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert len(model.random_variables.iiv[0].names) == 2
    model_state_new = update_model_state(model_state, block=[['CL']])
    model_new = model_state_new.generate_model()
    assert len(model_new.random_variables.iiv[0].names) == 1
    model_state_new = update_model_state(model_state, block=[['CL'], ['VC']])
    model_new = model_state_new.generate_model()
    assert len(model_new.random_variables.iiv[0].names) == 1
    model_state_new = update_model_state(model_state, block=[['CL', 'VC']])
    model_new = model_state_new.generate_model()
    assert len(model_new.random_variables.iiv[0].names) == 2


def test_update_model_covariates():
    example_model = load_example_model('pheno')
    dataset, datainfo = example_model.dataset, example_model.datainfo
    model_state = ModelState.create('iv')
    covariate = [{'parameter': 'CL', 'covariate': 'AMT', 'effect': 'exp', 'operation': '*'}]
    model_state_new = update_model_state(model_state, covariates=covariate)
    model_new = model_state_new.generate_model(dataset, datainfo)
    assert has_covariate_effect(model_new, 'CL', 'AMT')
