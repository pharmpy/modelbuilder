from .style_elements import (
    create_badge,
    create_checklist,
    create_col,
    create_container,
    create_input_group,
    create_options_list,
    create_radio,
)


def create_absorption_rate_component():
    abs_rate_label_dict = {
        'Zero order': 'ZO',
        'First order': 'FO',
        'Sequential ZO FO': 'seq_ZO_FO',
    }

    abs_rate_badge = create_badge("Absorption rate")
    abs_rate_options = create_options_list(abs_rate_label_dict)
    abs_rate_radio = create_radio('abs_rate-radio', options=abs_rate_options)

    return create_col([abs_rate_badge, abs_rate_radio])


def create_elimination_rate_component():
    elim_label_dict = {
        'First order': 'FO',
        'Michaelis-Menten': 'MM',
        'Mixed MM FO': 'mixed_MM_FO',
        'Zero order': 'ZO',
    }

    elim_badge = create_badge("Elimination rate")
    elim_options = create_options_list(elim_label_dict)
    elim_radio = create_radio('elim_radio', options=elim_options)

    return create_col([elim_badge, elim_radio])


def create_absorption_delay_component():
    abs_delay_badge = create_badge("Absorption delay")

    lag_options = create_options_list({'Lag time': True})
    lag_checklist = create_checklist("lag-toggle", lag_options)

    transits_input_group = create_input_group(
        "transit_input", "Transit compartments", default_value=0, type='number', min=0, step=1
    )

    bioavailability_options = create_options_list({'Bioavailability': True})
    bioavailability_checklist = create_checklist("bio_toggle", bioavailability_options)

    abs_delay_style = {"padding-top": "2em"}
    return create_col(
        [
            abs_delay_badge,
            transits_input_group,
            lag_checklist,
            bioavailability_checklist,
        ],
        style=abs_delay_style,
    )


def create_peripherals_component():
    peripherals_dict = {'0': 0, '1': 1, '2': 2}

    peripherals_badge = create_badge("Peripheral compartments")
    peripherals_options = create_options_list(peripherals_dict)
    peripherals_radio = create_radio('peripheral-radio', options=peripherals_options)

    peripherals_style = {"width": "70%", "padding-top": "2em"}
    return create_col([peripherals_badge, peripherals_radio], style=peripherals_style)


abs_rate_component = create_absorption_rate_component()
elim_component = create_elimination_rate_component()
abs_delay_component = create_absorption_delay_component()
peripherals_component = create_peripherals_component()

structural_tab = create_container(
    ([abs_rate_component, elim_component], [abs_delay_component, peripherals_component])
)
