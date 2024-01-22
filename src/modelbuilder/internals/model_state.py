from dataclasses import dataclass

from pharmpy.modeling import convert_model, create_basic_pk_model
from pharmpy.tools.mfl.parse import ModelFeatures, get_model_features, parse


@dataclass
class ModelState:
    model_type: str
    mfl: ModelFeatures

    def __init__(self, model_type, model):
        self.model_type = model_type
        mfl_str = get_model_features(model)
        self.mfl = ModelFeatures.create_from_mfl_string(mfl_str)


def create_model(model_type):
    model = create_basic_pk_model(model_type)
    model = convert_model(model, "nonmem")
    model_state = ModelState('iv', model)
    return model, model_state


def update_model(model_old, ms_old, mfl_str_func):
    feat_mfl_list = parse(mfl_str_func)
    mfl_new = ms_old.mfl.replace_features(feat_mfl_list)
    lnt = ms_old.mfl.least_number_of_transformations(mfl_new, tool="modelsearch")

    model_new = create_basic_pk_model(ms_old.model_type)
    model_new = model_new.replace(dataset=model_old.dataset, datainfo=model_old.datainfo)
    for name, func in lnt.items():
        model_new = func(model_new)
    model_new = convert_model(model_new, "nonmem")
    ms_new = ModelState(ms_old.model_type, model_new)
    return model_new, ms_new
