import ast
import builtins
from dataclasses import dataclass
from functools import partial

import pandas as pd
import pharmpy
from pharmpy.internals.immutable import Immutable
from pharmpy.mfl import ModelFeatures
from pharmpy.model import Parameter, Parameters
from pharmpy.modeling import (
    add_iov,
    convert_model,
    create_basic_pk_model,
    fix_parameters,
    get_individual_parameters,
    get_rv_parameters,
    has_additive_error_model,
    has_combined_error_model,
    has_proportional_error_model,
    set_additive_error_model,
    set_combined_error_model,
    set_dataset,
    set_description,
    set_iiv_on_ruv,
    set_initial_estimates,
    set_lower_bounds,
    set_name,
    set_power_on_ruv,
    set_proportional_error_model,
    set_time_varying_error_model,
    set_upper_bounds,
    unfix_parameters,
)
from pharmpy.modeling.mfl import generate_transformations, get_model_features

from pywrapr.docs_conversion import translate_python_row

ERROR_FUNCS = {
    'add': set_additive_error_model,
    'prop': set_proportional_error_model,
    'comb': set_combined_error_model,
    'iiv-on-ruv': set_iiv_on_ruv,
    'power': set_power_on_ruv,
    'time-varying': partial(set_time_varying_error_model, cutoff=1.0),
}
ERROR_FUNCS_DICT = {
    set_proportional_error_model: has_proportional_error_model,
    set_additive_error_model: has_additive_error_model,
    set_combined_error_model: has_combined_error_model,
}


@dataclass
class ModelState(Immutable):
    model_type: str
    model_format: str
    model_attrs: dict
    mfl: ModelFeatures
    error_funcs: list[str]
    parameters: Parameters
    col: list
    individual_parameters: list
    dataset: pd.DataFrame

    def __init__(
        self,
        model_type,
        model_format,
        model_attrs,
        mfl,
        error_funcs,
        parameters,
        iov=None,
        col=None,
        individual_parameters=None,
        dataset=None,
    ):
        self.model_type = model_type
        self.model_format = model_format
        self.model_attrs = model_attrs
        self.mfl = mfl
        self.error_funcs = error_funcs
        self.parameters = parameters
        self.iov = iov
        self.col = col
        self.individual_parameters = individual_parameters
        self.dataset = dataset

    def replace(self, **kwargs):
        model_format = kwargs.get('model_format', self.model_format)
        mfl = kwargs.get('mfl', self.mfl)
        model_attrs = kwargs.get('model_attrs', self.model_attrs)
        error_funcs = kwargs.get('error_funcs', self.error_funcs)
        parameters = kwargs.get('parameters', self.parameters)
        iov = kwargs.get('iov', self.iov)
        col = kwargs.get('col', self.col)
        individual_parameters = kwargs.get('individual_parameters', self.individual_parameters)
        dataset = kwargs.get('dataset', self.dataset)

        return ModelState(
            model_type=self.model_type,
            model_format=model_format,
            model_attrs=model_attrs,
            mfl=mfl,
            error_funcs=error_funcs,
            parameters=parameters,
            iov=iov,
            col=col,
            individual_parameters=individual_parameters,
            dataset=dataset,
        )

    @classmethod
    def create(cls, model_type):
        model = cls._create_base_model(model_type)
        mfl = get_model_features(model)
        error_funcs = {1: ['prop']}
        parameters = model.parameters
        col = model.datainfo.names
        iov = []
        individual_parameters = get_individual_parameters(model)
        dataset = None
        return cls(
            model_type,
            'nonmem',
            {},
            mfl,
            error_funcs,
            parameters,
            iov,
            col,
            individual_parameters,
            dataset,
        )

    @staticmethod
    def _create_base_model(model_type, dataset=None, datainfo=None):
        model = create_basic_pk_model(model_type)
        if dataset is not None and datainfo:
            model = model.replace(dataset=dataset, datainfo=datainfo)
        return model

    def list_functions(self, dataset=None, datainfo=None):
        funcs = []

        funcs.append(partial(create_basic_pk_model, administration=self.model_type))
        model = funcs[-1]()

        # FIXME: How to handle datainfo?
        if dataset is not None and datainfo is not None:
            funcs.append(partial(pharmpy.model.Model.replace, dataset=dataset, datainfo=datainfo))
            model = funcs[-1](model)
        elif self.dataset is not None:
            # FIXME: datatype has to be nonmem, if it is generic there will be an error
            funcs.append(partial(set_dataset, path_or_df=self.dataset, datatype='nonmem'))
            model = funcs[-1](model)

        if self.model_attrs:
            attrs = self.model_attrs.copy()
            if 'name' in attrs:
                funcs.append(partial(set_name, new_name=attrs['name']))
                model = funcs[-1](model)
            if 'description' in attrs:
                funcs.append(partial(set_description, new_description=attrs['description']))
                model = funcs[-1](model)

        mfl_funcs = self._get_mfl_funcs(model)
        is_pd_model = self._is_pd_model()

        if is_pd_model and self.model_format != "generic":
            funcs.append(partial(convert_model, to_format=self.model_format))
            model = funcs[-1](model)

        for func in mfl_funcs:
            funcs.append(func)
            model = funcs[-1](model)

        for dv, func_names in self.error_funcs.items():
            for func_name in func_names:
                if ERROR_FUNCS[func_name] not in ERROR_FUNCS_DICT.keys() or not ERROR_FUNCS_DICT[
                    ERROR_FUNCS[func_name]
                ](model, dv=dv):
                    funcs.append(partial(ERROR_FUNCS[func_name], dv=dv))
                    model = funcs[-1](model)

        variability_funcs = self._get_mfl_funcs_variability(model)
        for func in variability_funcs:
            funcs.append(func)
            model = funcs[-1](model)

        if self.iov:
            for rv in self.iov:
                if isinstance(rv['list_of_parameters'], str):
                    rv['list_of_parameters'] = ast.literal_eval(rv['list_of_parameters'])
                funcs.append(partial(add_iov, **rv))
                model = funcs[-1](model)

        if self.mfl.covariates:
            covariate_funcs = generate_transformations(self.mfl.covariates, include_remove=False)
            for func in covariate_funcs:
                funcs.append(func)
                model = funcs[-1](model)

        #  Update parameters when model parameters have changed
        if self.parameters != model.parameters:
            self.parameters, self.individual_parameters = _update_parameters_from_model(
                self.parameters, model
            )
        parameter_transformations = {'inits': {}, 'lower': {}, 'upper': {}, 'fix': [], 'unfix': []}
        for p in model.parameters:
            param = self.parameters[p.name]
            if param != p:
                if param.init != p.init:
                    parameter_transformations['inits'][param.name] = param.init
                for attr in ['lower', 'upper']:
                    if getattr(param, attr) != getattr(p, attr):
                        parameter_transformations[attr][param.name] = getattr(param, attr)
                if param.fix != p.fix:
                    (parameter_transformations['fix' if param.fix else 'unfix']).append(param.name)

        func_mapping = {
            'inits': (set_initial_estimates, 'inits'),
            'lower': (set_lower_bounds, 'bounds'),
            'upper': (set_upper_bounds, 'bounds'),
            'fix': (fix_parameters, 'parameter_names'),
            'unfix': (unfix_parameters, 'parameter_names'),
        }
        for attr, values in parameter_transformations.items():
            if values:
                func_name = func_mapping[attr]
                func = partial(func_name[0], **{func_name[1]: values})
                funcs.append(func)
                model = func(model)

        if not is_pd_model and self.model_format != "generic":
            funcs.append(partial(convert_model, to_format=self.model_format))
            model = funcs[-1](model)

        return funcs, model

    def generate_model(self, dataset=None, datainfo=None):
        funcs, model = self.list_functions(dataset, datainfo)
        return model

    def _get_mfl_funcs(self, model_base):
        # FIXME: assumes base model is PK, should detect PD as well
        mfl_start = get_model_features(model_base, type='pk')
        mfl_diff = self.mfl.filter(filter_on='pk') - mfl_start
        mfl_structural = mfl_diff + self._get_pd_features()
        return generate_transformations(mfl_structural)

    def _is_pd_model(self):
        return len(self._get_pd_features()) > 0

    def _get_pd_features(self):
        return self.mfl.direct_effects + self.mfl.indirect_effects + self.mfl.effect_compartments

    def _get_mfl_funcs_variability(self, model_base):
        potential_params = {symb.name for symb in model_base.statements.free_symbols}

        def _filter_iiv(iivs, params):
            return [iiv for iiv in iivs if iiv.parameter in params]

        iivs_start = get_model_features(model_base, type='iiv')

        to_remove = _filter_iiv(iivs_start - self.mfl.iiv, potential_params)
        to_add = _filter_iiv(self.mfl.iiv - iivs_start, potential_params)

        potential_params = potential_params - {iiv.parameter for iiv in to_remove}

        def _filter_cov(covs, params):
            return [cov for cov in covs if set(cov.parameters).issubset(params)]

        covs_start = get_model_features(model_base, type='covariance')
        if self.mfl.covariance - covs_start:
            to_add += _filter_cov(self.mfl.covariance, potential_params)
        to_remove += _filter_cov(covs_start - self.mfl.covariance, potential_params)
        variability_funcs = []

        if to_remove:
            variability_funcs += generate_transformations(
                to_remove, include_remove=True, include_add=False
            )
        if to_add:
            variability_funcs += generate_transformations(
                to_add, include_remove=False, include_add=True
            )

        return variability_funcs

    def __eq__(self, other):
        return (
            self.model_type == other.model_type
            and self.model_format == other.model_format
            and self.model_attrs == other.model_attrs
            and self.mfl == other.mfl
            and self.error_funcs == other.error_funcs
            and self.parameters == other.parameters
            and self.iov == other.iov
        )


def update_model_state(ms_old, mfl=None, type=None, **kwargs):
    model_attrs = kwargs.get('model_attrs')
    error = kwargs.get('error')
    parameters = kwargs.get('parameters')
    iov = kwargs.get('iov')
    individual_parameters = kwargs.get('individual_parameters')
    if not parameters:
        ms_old = ms_old.replace(parameters=Parameters())
    if mfl is not None:
        mfl_parsed = ModelFeatures.create(mfl)
        mfl_new = _update_mfl(ms_old.mfl, mfl_parsed, type)
        return ms_old.replace(mfl=mfl_new)
    if model_attrs:
        return ms_old.replace(model_attrs=model_attrs)
    if error is not None:
        error_funcs = _interpret_error_model(error, ms_old.error_funcs)
        return ms_old.replace(error_funcs=error_funcs)
    if parameters:
        params_new = [Parameter.from_dict(d) for d in parameters]
        return ms_old.replace(parameters=Parameters.create(params_new))
    if iov is not None:
        return ms_old.replace(iov=iov)
    if individual_parameters:
        return ms_old.replace(individual_parameters=individual_parameters)
    raise ValueError


def _update_mfl(mfl_old, mfl_parsed, type):
    if type == 'structural':
        feature_types = [builtins.type(feature) for feature in mfl_parsed]
        features_old = [feature for feature in mfl_old if builtins.type(feature) in feature_types]
        features_new = mfl_parsed
    elif type == 'variability':
        features_old = mfl_old.iiv + mfl_old.iov + mfl_old.covariance
        features_new = mfl_parsed.iiv + mfl_parsed.iov
        params = {var.parameter for var in features_new}
        covariances_new = [
            cov for cov in mfl_parsed.covariance if set(cov.parameters).issubset(params)
        ]
        features_new += covariances_new
    elif type == 'covariate':
        features_old = mfl_old.covariates
        features_new = mfl_parsed.covariates
    else:
        raise NotImplementedError

    mfl_new = ModelFeatures.create(mfl_old - features_old + features_new)
    return mfl_new


# FIXME: remove relevant functions when MFL supports that feature
def _interpret_error_model(error_funcs, error_old):
    mutex = ['add', 'prop', 'comb']
    addons = ['iiv-on-ruv', 'power', 'time-varying']

    base_error = {}
    for key, value in error_old.items():
        base = set(value).intersection(mutex).pop()
        base_error[key] = base

    err_f = {}
    for dv, error_func in error_funcs.items():
        base_err = base_error.get(dv)
        if error_func in mutex:
            if base_err:
                error_addons = error_old[dv].copy().remove(base_error[dv])
            else:
                error_addons = []
            if error_addons:
                err_f[dv] = [error_func] + error_addons
            else:
                err_f[dv] = [error_func]
        elif error_func == '':
            if base_err:
                err_f[dv] = [base_error[dv]]
        else:
            error_funcs = error_func.split(';')
            assert all(func in addons for func in error_funcs)
            if base_err:
                err_f[dv] = [base_error[dv]] + error_funcs
            else:
                err_f[dv] = error_funcs
    return err_f


def _update_parameters_from_model(ms_parameters, model):
    new_params = Parameters()
    for param in ms_parameters:
        if param.name in model.parameters.names:
            new_params += param
    for param in model.parameters:
        if param.name not in ms_parameters.names:
            new_params += param

    individual_parameters = get_individual_parameters(model)
    return new_params, individual_parameters


def _update_covariates(model, covariates):
    new_covariates = [
        cov for cov in covariates if cov.parameter in get_individual_parameters(model)
    ]
    return ModelFeatures.create(new_covariates)


def generate_code(funcs, language):
    string_out = ''
    for i, func in enumerate(funcs):
        if isinstance(func, partial):
            keyword_dict = func.keywords.copy()
            func_name = func.func.__name__
            if 'path_or_df' in keyword_dict.keys():
                keyword_dict['path_or_df'] = 'path/to/dataset'
            args = ', '.join('%s=%r' % x for x in keyword_dict.items())
            if i > 0 and language == 'python':
                args = 'model, ' + args
            func_call = f"{func_name}({args})"
            if language == 'r':
                func_call = translate_python_row(func_call)
        else:
            func_call = f"{func.__name__}(model)"
            if language == 'r':
                func_call = translate_python_row(func_call)
        if language == 'python':
            string_out += f"model = {func_call}\n"
        else:
            if i == 0:
                r_str = f"model <- {func_call}"
                spacing = ''
            else:
                r_str = func_call
                spacing = ' '
            r_str = f"{spacing}{r_str}"
            if i < len(funcs) - 1:
                r_str += ' %>%'
            string_out += f"{r_str}\n"
    return string_out


def _group_by_key(lst, key1, key2):
    # Group key1 by key2
    result = {}
    for d in lst:
        k = d[key2]
        if k not in result:
            result[k] = {key1: [], key2: k}
        result[k][key1].append(d[key1])
    return list(result.values())


def _get_params_with_iiv(model):
    params_with_iiv = {}
    for rv in model.random_variables.iiv.names:
        try:
            param = get_rv_parameters(model, rv)[0]
        except ValueError:
            continue
        else:
            params_with_iiv[param] = 'exp'
    return params_with_iiv
