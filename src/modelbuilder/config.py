from pharmpy.modeling import convert_model, create_basic_pk_model

model = create_basic_pk_model('iv')
model = convert_model(model, "nonmem")


def make_label_value(key, value):
    return {"label": key, "value": value}
