import ast
from dataclasses import dataclass
from functools import partial
from typing import Union
import pandas as pd

from pharmpy.internals.immutable import Immutable
from pharmpy.model import Parameter, Parameters, RandomVariables
from pharmpy.modeling import (
    add_covariate_effect,
    add_iiv,
    add_iov,
    convert_model,
    create_basic_pk_model,
    create_joint_distribution,
    get_parameter_rv,
    get_rv_parameters,
    set_additive_error_model,
    set_combined_error_model,
    set_iiv_on_ruv,
    set_power_on_ruv,
    set_proportional_error_model,
    set_time_varying_error_model,
    get_individual_parameters,
    remove_iiv,
    remove_iov,
    split_joint_distribution,
)
from pharmpy.tools.mfl.parse import ModelFeatures, get_model_features

ERROR_FUNCS = {
    'add': set_additive_error_model,
    'prop': set_proportional_error_model,
    'comb': set_combined_error_model,
    'iiv-on-ruv': set_iiv_on_ruv,
    'power': set_power_on_ruv,
    'time-varying': partial(set_time_varying_error_model, cutoff=1.0),
}


@dataclass
class ModelState(Immutable):
    model_type: str
    model_format: str
    model_attrs: dict
    mfl: ModelFeatures
    error_funcs: list[str]
    parameters: Parameters
    rvs: dict
    occ: list
    individual_parameters: list
    dataset: pd.DataFrame
    block: list
    covariates: list

    def __init__(
        self,
        model_type,
        model_format,
        model_attrs,
        mfl,
        error_funcs,
        parameters,
        rvs=None,
        occ=None,
        individual_parameters=None,
        dataset=None,
        block=None,
        covariates=None,
    ):
        self.model_type = model_type
        self.model_format = model_format
        self.model_attrs = model_attrs
        self.mfl = mfl
        self.error_funcs = error_funcs
        self.parameters = parameters
        self.rvs = rvs
        self.occ = occ
        self.individual_parameters = individual_parameters
        self.dataset = dataset
        self.block = block
        self.covariates = covariates

    def replace(self, **kwargs):
        model_format = kwargs.get('model_format', self.model_format)
        mfl = kwargs.get('mfl', self.mfl)
        model_attrs = kwargs.get('model_attrs', self.model_attrs)
        error_funcs = kwargs.get('error_funcs', self.error_funcs)
        parameters = kwargs.get('parameters', self.parameters)
        rvs = kwargs.get('rvs', self.rvs)
        occ = kwargs.get('occ', self.occ)
        individual_parameters = kwargs.get('individual_parameters', self.individual_parameters)
        dataset = kwargs.get('dataset', self.dataset)
        block = kwargs.get('block', self.block)
        covariates = kwargs.get('covariates', self.covariates)

        return ModelState(
            model_type=self.model_type,
            model_format=model_format,
            model_attrs=model_attrs,
            mfl=mfl,
            error_funcs=error_funcs,
            parameters=parameters,
            rvs=rvs,
            occ=occ,
            individual_parameters=individual_parameters,
            dataset=dataset,
            block=block,
            covariates=covariates,
        )

    @classmethod
    def create(cls, model_type):
        model = cls._create_base_model(model_type)
        mfl_str = get_model_features(model)
        mfl = ModelFeatures.create_from_mfl_string(mfl_str)
        error_funcs = {1: ['prop']}
        parameters = model.parameters
        iiv_rvs = _update_rvs_from_model(model)
        rvs = {'iiv': iiv_rvs, 'iov': {}}
        occ = model.datainfo.names
        individual_parameters = get_individual_parameters(model)
        dataset = None
        block = [['CL', 'VC']]
        covariates = None
        return cls(
            model_type,
            'nonmem',
            {'name': 'start'},
            mfl,
            error_funcs,
            parameters,
            rvs,
            occ,
            individual_parameters,
            dataset,
            block,
            covariates,
        )

    @staticmethod
    def _create_base_model(model_type, dataset=None, datainfo=None):
        model = create_basic_pk_model(model_type)
        if dataset is not None and datainfo:
            model = model.replace(dataset=dataset, datainfo=datainfo)
        return model

    def generate_model(self, dataset=None, datainfo=None, dv=None):
        model = self._create_base_model(self.model_type, dataset, datainfo)
        if self.model_attrs:
            model = model.replace(**self.model_attrs)

        mfl_funcs = self._get_mfl_funcs(model)

        model_new = model
        model_new = remove_iiv(model_new)

        for func in mfl_funcs:
            model_new = func(model_new)
        for dv, func_names in self.error_funcs.items():
            for func_name in func_names:
                model_new = ERROR_FUNCS[func_name](model_new, dv=dv)

        if self.rvs['iiv']:
            for iiv_func in self.rvs['iiv']:
                model_new = add_iiv(model_new, **iiv_func)

        if self.rvs['iov']:
            model_new = model_new.replace(dataset=self.dataset)
            for rv in self.rvs['iov']:
                rv['list_of_parameters'] = ast.literal_eval(rv['list_of_parameters'])
                model_new = add_iov(model_new, **rv)

        if self.block:
            model_new = split_joint_distribution(model_new)
            for bl in self.block:
                params = [get_parameter_rv(model_new, param)[0] for param in bl]
                if len(params) > 1:
                    model_new = create_joint_distribution(model_new, params)

        if self.covariates:
            model_new = model_new.replace(dataset=self.dataset)
            for cov in self.covariates:
                model_new = add_covariate_effect(model_new, **cov)

        # FIXME: This is needed since new parameters may have been added when e.g.
        #  changing the structural model. Ideally this should be done in
        #  ModelState.replace()
        parameters = self.parameters
        for p in model_new.parameters:
            if p.name not in parameters.names:
                parameters += p
        # Delete parameters that are not in model
        new_params = Parameters()
        for p in parameters:
            if p.name in model_new.parameters:
                new_params += p

        model_new = model_new.replace(parameters=new_params)
        return convert_model(model_new, self.model_format)

    def _get_mfl_funcs(self, model_base):
        mfl_str_start = get_model_features(model_base)
        mfl_start = ModelFeatures.create_from_mfl_string(mfl_str_start)
        if mfl_start.filter('pd') is None:
            lnt = mfl_start.least_number_of_transformations(self.mfl, model_base)
            funcs = list(lnt.values())
        else:
            pk_mfl = self.mfl.filter('pk')
            lnt = mfl_start.least_number_of_transformations(pk_mfl, model_base)
            funcs = list(lnt.values())
            pd_funcs = self.mfl.convert_to_funcs(model=model_base, subset_features='pd')
            funcs += list(pd_funcs.values())
        return funcs

    def __eq__(self, other):
        return (
            self.model_type == other.model_type
            and self.model_format == other.model_format
            and self.model_attrs == other.model_attrs
            and self.mfl == other.mfl
            and self.error_funcs == other.error_funcs
            and self.parameters == other.parameters
            and self.rvs == other.rvs
        )


def update_model_state(ms_old, mfl=None, **kwargs):
    model_attrs = kwargs.get('model_attrs')
    error = kwargs.get('error')
    parameters = kwargs.get('parameters')
    rvs = kwargs.get('rvs')
    individual_parameters = kwargs.get('individual_parameters')
    block = kwargs.get('block')
    covariates = kwargs.get('covariates')

    if mfl:
        mfl_new = ms_old.mfl.replace_features(mfl)
        return ms_old.replace(mfl=mfl_new)
    if model_attrs:
        return ms_old.replace(model_attrs=model_attrs)
    if error is not None:
        error_funcs = _interpret_error_model(error, ms_old.error_funcs)
        return ms_old.replace(error_funcs=error_funcs)
    if parameters:
        params_new = [Parameter.from_dict(d) for d in parameters]
        return ms_old.replace(parameters=Parameters.create(params_new))
    if rvs:
        return ms_old.replace(rvs=rvs)
    if individual_parameters:
        return ms_old.replace(individual_parameters=individual_parameters)
    if block is not None:
        return ms_old.replace(block=block)
    if covariates is not None:
        return ms_old.replace(covariates=covariates)
    raise ValueError


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


def update_ms_from_model(model, ms):
    parameters = model.parameters
    individual_parameters = get_individual_parameters(model)
    new_ms = ms.replace(parameters=parameters, individual_parameters=individual_parameters)
    return new_ms


def _update_rvs_from_model(model):
    rvs_names = model.random_variables.iiv.names
    if rvs_names:
        param_names = [get_rv_parameters(model, param)[0] for param in rvs_names]
        return [{'list_of_parameters': param, 'expression': 'exp'} for param in param_names]
    else:
        return []
