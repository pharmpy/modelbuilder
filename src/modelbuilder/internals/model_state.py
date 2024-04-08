import inspect
from dataclasses import dataclass
from functools import partial
from typing import List

from pharmpy.internals.immutable import Immutable
from pharmpy.modeling import (
    convert_model,
    create_basic_pk_model,
    set_additive_error_model,
    set_combined_error_model,
    set_iiv_on_ruv,
    set_proportional_error_model,
    set_time_varying_error_model,
)
from pharmpy.tools.mfl.parse import ModelFeatures, get_model_features


@dataclass
class ModelState(Immutable):
    model_type: str
    mfl: ModelFeatures
    error_funcs: List[callable]

    def __init__(self, model_type, mfl, error_funcs):
        self.model_type = model_type
        self.mfl = mfl
        self.error_funcs = error_funcs

    def replace(self, **kwargs):
        if 'mfl' in kwargs:
            mfl = kwargs['mfl']
        else:
            mfl = self.mfl
        if 'error_funcs' in kwargs:
            error_funcs = kwargs['error_funcs']
        else:
            error_funcs = self.error_funcs
        return ModelState(model_type=self.model_type, mfl=mfl, error_funcs=error_funcs)

    @classmethod
    def create(cls, model_type):
        model = cls._create_base_model(model_type)
        mfl_str = get_model_features(model)
        mfl = ModelFeatures.create_from_mfl_string(mfl_str)
        error_funcs = [set_proportional_error_model]
        return cls(model_type, mfl, error_funcs)

    @staticmethod
    def _create_base_model(model_type, dataset=None, datainfo=None):
        model = create_basic_pk_model(model_type)
        if dataset and datainfo:
            model = model.replace(dataset=dataset, datainfo=datainfo)
        return model

    def generate_model(self, dataset=None, datainfo=None):
        model = self._create_base_model(self.model_type, dataset, datainfo)
        struct_funcs = self._get_mfl_funcs(model)

        model_new = model
        for func in struct_funcs + self.error_funcs:
            model_new = func(model_new)

        return convert_model(model_new, "nonmem")

    def _get_mfl_funcs(self, model_base):
        mfl_str_start = get_model_features(model_base)
        mfl_start = ModelFeatures.create_from_mfl_string(mfl_str_start)
        lnt = mfl_start.least_number_of_transformations(self.mfl, tool="modelsearch")
        return list(lnt.values())


def update_model_state(ms_old, mfl_str_or_func):
    kwargs = dict()

    if isinstance(mfl_str_or_func, str):
        mfl_new = ms_old.mfl.replace_features(mfl_str_or_func)
        kwargs['mfl'] = mfl_new
    elif callable(mfl_str_or_func):
        func = mfl_str_or_func
        module_name = inspect.getmodule(_get_func_if_partial(func)).__name__
        if module_name == 'pharmpy.modeling.error':
            error_funcs = _interpret_error_model(func, ms_old.error_funcs)
            kwargs['error_funcs'] = error_funcs
        else:
            raise ValueError(f'Function not supported: `{mfl_str_or_func}`')
    else:
        raise TypeError(f'Type not supported for `{mfl_str_or_func}`: {type(mfl_str_or_func)}')

    ms_new = ms_old.replace(**kwargs)

    return ms_new


def _get_func_if_partial(func):
    return func.func if isinstance(func, partial) else func


# FIXME: remove relevant functions when MFL supports that feature
def _interpret_error_model(error_func, error_old):
    mutex = [set_additive_error_model, set_proportional_error_model, set_combined_error_model]
    addons = [set_iiv_on_ruv, set_time_varying_error_model]

    if _get_func_if_partial(error_func) in mutex:
        error_addons = [
            error_func_addon for error_func_addon in error_old if error_func_addon not in mutex
        ]
        error_new = [error_func] + error_addons
    elif _get_func_if_partial(error_func) in addons:
        if error_func in error_old:
            raise ValueError
        error_new = error_old + [error_func]
    else:
        raise ValueError

    return error_new
