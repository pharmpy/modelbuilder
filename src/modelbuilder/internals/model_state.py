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
    set_power_on_ruv,
    set_proportional_error_model,
    set_time_varying_error_model,
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
    error_funcs: List[str]

    def __init__(self, model_type, model_format, model_attrs, mfl, error_funcs):
        self.model_type = model_type
        self.model_format = model_format
        self.model_attrs = model_attrs
        self.mfl = mfl
        self.error_funcs = error_funcs

    def replace(self, **kwargs):
        if 'model_format' in kwargs:
            model_format = kwargs['model_format']
        else:
            model_format = self.model_format
        if 'mfl' in kwargs:
            mfl = kwargs['mfl']
        else:
            mfl = self.mfl
        if 'model_attrs' in kwargs:
            model_attrs = kwargs['model_attrs']
        else:
            model_attrs = self.model_attrs
        if 'error_funcs' in kwargs:
            error_funcs = kwargs['error_funcs']
        else:
            error_funcs = self.error_funcs
        return ModelState(
            model_type=self.model_type,
            model_format=model_format,
            model_attrs=model_attrs,
            mfl=mfl,
            error_funcs=error_funcs,
        )

    @classmethod
    def create(cls, model_type):
        model = cls._create_base_model(model_type)
        mfl_str = get_model_features(model)
        mfl = ModelFeatures.create_from_mfl_string(mfl_str)
        error_funcs = ['prop']
        return cls(model_type, 'nonmem', {'name': 'start'}, mfl, error_funcs)

    @staticmethod
    def _create_base_model(model_type, dataset=None, datainfo=None):
        model = create_basic_pk_model(model_type)
        if dataset is not None and datainfo:
            model = model.replace(dataset=dataset, datainfo=datainfo)
        return model

    def generate_model(self, dataset=None, datainfo=None):
        model = self._create_base_model(self.model_type, dataset, datainfo)
        if self.model_attrs:
            model = model.replace(**self.model_attrs)

        mfl_funcs = self._get_mfl_funcs(model)

        model_new = model
        for func in mfl_funcs:
            model_new = func(model_new)
        for func_name in self.error_funcs:
            model_new = ERROR_FUNCS[func_name](model_new)

        return convert_model(model_new, self.model_format)

    def _get_mfl_funcs(self, model_base):
        mfl_str_start = get_model_features(model_base)
        mfl_start = ModelFeatures.create_from_mfl_string(mfl_str_start)
        lnt = mfl_start.least_number_of_transformations(self.mfl, model_base)
        funcs = list(lnt.values())
        return funcs


def update_model_state(ms_old, mfl=None, **kwargs):
    model_attrs = kwargs.get('model_attrs')
    error = kwargs.get('error')

    if mfl:
        mfl_new = ms_old.mfl.replace_features(mfl)
        return ms_old.replace(mfl=mfl_new)
    if model_attrs:
        return ms_old.replace(model_attrs=model_attrs)
    if error is not None:
        error_funcs = _interpret_error_model(error, ms_old.error_funcs)
        return ms_old.replace(error_funcs=error_funcs)
    raise ValueError


# FIXME: remove relevant functions when MFL supports that feature
def _interpret_error_model(error_func, error_old):
    mutex = ['add', 'prop', 'comb']
    addons = ['iiv-on-ruv', 'power', 'time-varying']

    base_error = set(error_old).intersection(mutex).pop()

    if error_func in mutex:
        error_addons = error_old.copy().remove(base_error)
        if error_addons:
            return [error_func] + error_addons
        else:
            return [error_func]
    elif error_func == '':
        return [base_error]
    else:
        error_funcs = error_func.split(';')
        assert all(func in addons for func in error_funcs)
        return [base_error] + error_funcs
