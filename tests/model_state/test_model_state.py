import pytest
from pharmpy.mfl import IIV, Covariance, Covariate, ModelFeatures
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
from pharmpy.modeling.mfl import get_model_features

from modelbuilder.internals.model_state import ModelState, generate_code, update_model_state


def test_model_state_init():
    model = create_basic_pk_model('iv')
    mfl = get_model_features(model, type='pk')
    model_state = ModelState('iv', 'nonmem', {}, mfl, ['prop'], model.parameters)
    assert repr(model_state.mfl) == 'ELIMINATION(FO);PERIPHERALS(0)'
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
        == 'ELIMINATION(FO);PERIPHERALS(0);IIV([CL,VC],EXP);COVARIANCE(IIV,[CL,VC])'
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
        == 'ABSORPTION(FO);TRANSITS(0);LAGTIME(OFF);ELIMINATION(FO);PERIPHERALS(0);IIV([CL,MAT,VC],EXP);COVARIANCE(IIV,[CL,VC])'
    )
    assert model_state.error_funcs == {1: ['prop']}
    assert len(model_state.parameters) == len(model.parameters)


def test_update_model():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert has_first_order_elimination(model)
    model_state_new = update_model_state(model_state, 'ELIMINATION(MM)', type='structural')
    model_new = model_state_new.generate_model()
    assert has_michaelis_menten_elimination(model_new)

    model_state = ModelState.create('oral')
    model = model_state.generate_model()
    assert has_first_order_absorption(model)
    model_state_new = update_model_state(model_state, 'ABSORPTION(ZO)', type='structural')
    model_new = model_state_new.generate_model()
    assert has_zero_order_absorption(model_new)

    example_model = load_example_model('pheno')
    dataset, datainfo = example_model.dataset, example_model.datainfo
    model_state = ModelState.create('oral')
    model = model_state.generate_model(dataset, datainfo)
    assert has_first_order_absorption(model)
    model_state_new = update_model_state(model_state, 'COVARIATE(CL,WGT,exp)', type='covariate')
    model_new = model_state_new.generate_model(dataset, datainfo)
    assert has_covariate_effect(model_new, 'CL', 'WGT')


def test_update_model_stepwise():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert has_first_order_elimination(model)
    assert has_proportional_error_model(model)
    model_state_new = update_model_state(model_state, 'ELIMINATION(MM)', type='structural')
    model_state_new = update_model_state(model_state_new, error={1: 'add'})
    model_new = model_state_new.generate_model()
    assert has_michaelis_menten_elimination(model_new)
    assert has_additive_error_model(model_new)


def test_update_model_structural():
    model_state = ModelState.create('iv')
    model = model_state.generate_model()
    assert has_first_order_elimination(model)
    model_state_new = update_model_state(model_state, 'ELIMINATION(MM)', type='structural')
    assert len(model_state.mfl) == len(model_state_new.mfl)
    model_new = model_state_new.generate_model()
    assert has_michaelis_menten_elimination(model_new)
    model_state_new = update_model_state(model_state_new, 'ELIMINATION(FO)', type='structural')
    model_new = model_state_new.generate_model()
    assert has_first_order_elimination(model_new)
    model_state_new = update_model_state(model_state_new, 'ELIMINATION(MM)', type='structural')
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
    model_state = update_model_state(model_state, 'DIRECTEFFECT(LINEAR)', type='structural')
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
    mfl_new = model_state.mfl - model_state.mfl.iiv
    model_state_new = update_model_state(model_state, mfl=mfl_new, type='variability')
    model_new = model_state_new.generate_model()
    assert model_new.random_variables.iiv.names == ('eta_dummy',)
    assert len(model_state_new.mfl.covariance) == 0
    iiv1 = IIV.create(parameter='CL', fp='exp', optional=False)
    iiv2 = IIV.create(parameter='VC', fp='exp', optional=False)
    mfl_new = ModelFeatures.create([iiv1, iiv2])
    model_state_new = update_model_state(model_state_new, mfl=mfl_new, type='variability')
    model_new = model_state_new.generate_model()
    assert len(model_new.random_variables.iiv.names) == 2


def test_update_model_block():
    model_state = ModelState.create('oral')
    model = model_state.generate_model()
    assert len(model.random_variables.iiv) == 2
    cov1 = Covariance.create(type='iiv', parameters=['CL', 'MAT'])
    cov2 = Covariance.create(type='iiv', parameters=['CL', 'VC'])
    cov3 = Covariance.create(type='iiv', parameters=['MAT', 'VC'])
    mfl_new = ModelFeatures.create([cov1, cov2, cov3])
    model_state_new = update_model_state(
        model_state, mfl=model_state.mfl.iiv + mfl_new, type='variability'
    )
    model_new = model_state_new.generate_model()
    assert len(model_new.random_variables.iiv) == 1


def test_update_model_covariates():
    example_model = load_example_model('pheno')
    dataset, datainfo = example_model.dataset, example_model.datainfo
    model_state = ModelState.create('iv')
    covariate = Covariate.create('CL', 'AMT', 'exp', '*', optional=False)
    mfl_new = ModelFeatures.create([covariate])
    model_state_new = update_model_state(model_state, mfl_new, type='covariate')
    model_new = model_state_new.generate_model(dataset, datainfo)
    assert has_covariate_effect(model_new, 'CL', 'AMT')


@pytest.mark.parametrize(
    'language, expected',
    [
        (
            'python',
            'model = create_basic_pk_model(administration=\'iv\')\n'
            'model = convert_model(model, to_format=\'nonmem\')\n',
        ),
        (
            'r',
            'model <- create_basic_pk_model(administration=\'iv\') %>%\n'
            ' convert_model(to_format=\'nonmem\')\n',
        ),
    ],
)
def test_generate_code(language, expected):
    model_state = ModelState.create('iv')
    funcs, _ = model_state.list_functions()
    assert generate_code(funcs, language) == expected
