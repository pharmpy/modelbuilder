from .style_elements import (
    create_badge,
    create_col,
    create_container,
    create_options_list,
    create_radio,
)


def create_pk_badge():
    pk_badge = create_badge("PK")
    return create_col([pk_badge])


def create_pd_badge():
    pd_badge = create_badge("PD")
    return create_col([pd_badge])


def create_absorption_rate_component():
    abs_rate_label_dict = {
        'Zero order': 'ZO',
        'First order': 'FO',
        'Sequential ZO FO': 'SEQ-ZO-FO',
    }

    abs_rate_badge = create_badge("Absorption rate")
    abs_rate_options = create_options_list(abs_rate_label_dict)
    abs_rate_radio = create_radio('abs_rate-radio', options=abs_rate_options)

    return create_col([abs_rate_badge, abs_rate_radio])


def create_elimination_rate_component():
    elim_label_dict = {
        'First order': 'FO',
        'Michaelis-Menten': 'MM',
        'Mixed MM FO': 'MIX-FO-MM',
        'Zero order': 'ZO',
    }

    elim_badge = create_badge("Elimination rate")
    elim_options = create_options_list(elim_label_dict)
    elim_radio = create_radio('elim_radio', options=elim_options)

    return create_col([elim_badge, elim_radio])


def create_absorption_delay_component():
    abs_delay_label_dict = {
        'No absorption delay': 'LAGTIME(OFF);TRANSITS(0)',
        'Lag time': 'LAGTIME(ON);TRANSITS(0)',
        'Transits': 'LAGTIME(OFF);TRANSITS(1)',
    }

    abs_delay_badge = create_badge("Absorption delay")
    abs_delay_options = create_options_list(abs_delay_label_dict)
    abs_delay_radio = create_radio('abs_delay_radio', options=abs_delay_options)

    return create_col([abs_delay_badge, abs_delay_radio])


def create_peripherals_component():
    peripherals_dict = {'0': 0, '1': 1, '2': 2}

    peripherals_badge = create_badge("Peripheral compartments")
    peripherals_options = create_options_list(peripherals_dict)
    peripherals_radio = create_radio('peripheral-radio', options=peripherals_options)

    peripherals_style = {"width": "70%", "padding-top": "2em"}
    return create_col([peripherals_badge, peripherals_radio], style=peripherals_style)


def create_pd_effect():
    pd_effect_label_dict = {
        'Direct Effect': 'DIRECTEFFECT',
        'Effect Compartment': 'EFFECTCOMP',
        'Indirect Effect': 'INDIRECTEFFECT',
    }

    pd_effect_badge = create_badge("Effect")
    pd_effect_options = create_options_list(pd_effect_label_dict)
    pd_effect_radio = create_radio('pd_effect_radio', options=pd_effect_options)

    return create_col([pd_effect_badge, pd_effect_radio])


def create_pd_expression():
    pd_expr_label_dict = {
        'Linear': 'LINEAR',
        'Emax': 'EMAX',
        'Sigmoid': 'SIGMOID',
        'Step': 'STEP',
    }

    pd_expr_badge = create_badge("Expression")
    pd_expr_options = create_options_list(pd_expr_label_dict)
    pd_expr_radio = create_radio('pd_expression_radio', options=pd_expr_options)

    return create_col([pd_expr_badge, pd_expr_radio])


def create_pd_production():
    pd_prod_label_dict = {
        'True': 'True',
        'False': 'False',
    }

    pd_prod_badge = create_badge("Production")
    pd_prod_options = create_options_list(pd_prod_label_dict)
    pd_prod_radio = create_radio('pd_production_radio', options=pd_prod_options, value='True')

    return create_col([pd_prod_badge, pd_prod_radio])


abs_rate_component = create_absorption_rate_component()
elim_component = create_elimination_rate_component()
abs_delay_component = create_absorption_delay_component()
peripherals_component = create_peripherals_component()
pk_badge = create_pk_badge()
pd_badge = create_pd_badge()
pd_effect = create_pd_effect()
pd_expression = create_pd_expression()
pd_production = create_pd_production()

structural_tab = create_container(
    (
        [pk_badge],
        [abs_rate_component, elim_component],
        [abs_delay_component, peripherals_component],
        [pd_badge],
        [pd_effect, pd_expression, pd_production],
    )
)
