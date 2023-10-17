#Design file containing all boxes

from pharmpy.modeling import *
from pharmpy.model import *
from dash import Dash, html, dcc,  callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

btn_color = "info"
badge_color ="info"
refreshtime = 1 #How often the model-code refreshes seconds

#Model types, add more if you want more buttons available
typeoptions = [
    {"label":"PK", "value":"PK" },
    ]

#The supported model formats
modelformats = [
    {"label":"generic", "value":"generic" },
    {"label":"nlmixr", "value":"nlmixr" },
    {"label":"nonmem", "value":"nonmem" },
    {"label":"rxode2", "value":"rxode" },
    ]

admin_route = [
    {"label":"IV", "value" : "iv"},
    {"label":"Oral", "value" : "oral"}
]

absorptionoptions = [
    {"label":"Rate", "value":"Rate" },
    {"label":"Delay", "value":"Delay" },
    ]

absorptionrates = [
    {"label":"Zero Order", "value" : "ZO", "disabled":"False"},
    {"label":"First Order", "value" : "FO", "disabled":"False"},
    {"label":"Sequential ZO FO", "value" : "seq_ZO_FO", "disabled":"False"},
    ]

covariate_effect = [
    {"label":"linear", "value":"lin" },
    {"label":"categorical", "value":"cat" },
    {"label":"piece linear", "value":"piece_lin" },
    {"label":"exponential", "value":"exp" },
    {"label":"power", "value":"pow" },
    ]

elimination_rates = [
    {"label":"First Order", "value":"FO" },
    {"label":"Michaelis-Menten", "value":"MM" },
    {"label":"Mixed MM FO", "value":"mixed_MM_FO" },
    {"label":"Zero Order", "value": "ZO"}
    ]



error_model = [
    {"label":"Additive", "value":"add"},
    {"label":"Combined", "value":"comb" },
    {"label":"Proportional", "value":"prop" },
    {"label":"Time Varying", "value":"time" },
    {"label":"Weighted", "value":"wgt" },
    ]

estimation_methods = [
    {"label":"FO", "value":"FO" },
    {"label":"FOCE", "value":"FOCE"},
    {"label":"ITS", "value":"ITS" },
    {"label":"IMPMAP", "value":"IMPMAP" },
    {"label":"IMP", "value":"IMP" },
    {"label":"SAEM", "value":"SAEM" },
    {"label":"BAYES", "value":"BAYES" },
    ]

#OPTIONS FOR DATAINFO
cols = [
        {'name': 'name', 'id': 'name', },
        {'name': 'type', 'id': 'type', 'presentation': 'dropdown'},
        {'name': 'scale', 'id': 'scale', 'presentation': 'dropdown'},
        {'name': 'continuous', 'id': 'continuous', 'presentation': 'dropdown'},
        {'name': 'categories', 'id': 'categories', 'presentation': 'dropdown'},
        {'name': 'unit', 'id': 'unit', 'presentation': 'dropdown'},
        {'name': 'datatype', 'id': 'datatype', 'presentation': 'dropdown'},
        {'name': 'drop', 'id': 'drop', 'presentation': 'dropdown'},
        {'name': 'descriptor', 'id': 'descriptor', 'presentation': 'dropdown'}
        ]

dd = {
    'type' : {
        'options' : [
            {'label':  "id", 'value': "id"},
            {'label':  "dv", 'value': "dv"},
            {'label':  "idv", 'value': "idv"},
            {'label':  "unknown", 'value': "unknown"},
            {'label':  "dose", 'value': "dose"},
            {'label':  "ii", 'value': "ii"},
            {'label':  "ss", 'value': "ss"},
            {'label':  "event", 'value': "event"},
            {'label':  "covariate", 'value':"covariate"},
            {'label':  "mdv", 'value':"mdv"},
            {'label':  "nmtran_date", 'value':"nmtran_date"},

        ]
    },
    'scale' : {
        'options' : [
            {'label':  "nominal", 'value':"nominal"},
            {'label':  "ordinal", 'value':"ordinal"},
            {'label':  "interval", 'value':"interval"},
            {'label':  "ratio", 'value':"ratio"},
        ]
    },
    'continuous' : {
        'options' : [
            {'label': 'continuous' , 'value': True},
            {'label': 'discrete' , 'value': False}
        ]
    },

    'unit' : {
        'options' : [
            {'label':  "1", 'value':1},
            {'label':  "ml", 'value':"ml"},
            {'label':  "mg", 'value':"mg"},
            {'label':  "h", 'value':"h"},
            {'label':  "kg", 'value':"kg"},
            {'label':  "mg/l", 'value':"mg/l"},
        ]
    },
    'datatype' : {
        'options' : [
            {'label': "int8" , 'value': "int8"},
            {'label': "int16" , 'value': "int16"},
            {'label': "int32" , 'value': "int32"},
            {'label': "int64" , 'value': "int64"},
            {'label': "uint8" , 'value': "uint8"},
            {'label': "uint16" , 'value': "uint16"},
            {'label': "uint32" , 'value': "uint32"},
            {'label': "uint64" , 'value': "uint64"},
            {'label': "float16" , 'value': "float16"},
            {'label': "float32" , 'value': "float32"},
            {'label': "float64" , 'value': "float64"},
            {'label': "float128" , 'value': "float128"},
            {'label': "nmtran-time" , 'value': "nmtran-time"},
            {'label': "nmtran-date" , 'value': "nmtran-date"},
        ]
    },
    'drop' : {
        'options' : [
            {'label': 'True' , 'value': True},
            {'label': 'False' , 'value': False}
        ]
    },
    'descriptor' : {
        'options': [
              {'label': 'age' , 'value': 'age'},
              {'label': 'body weight' , 'value': 'body weight'},
              {'label': 'lean body mass' , 'value': 'lean body mass'},
              {'label': 'fat free mass' , 'value': 'fat free mass'},
        ]
    }
}






#Navbar
navbar = dbc.Navbar(dbc.Container(
    [html.A(
        dbc.Row([
            dbc.Col(html.Img(src="https://pharmpy.github.io/latest/_images/Pharmpy_logo.svg"
            , height="40px")),
            ]),href="https://pharmpy.github.io"),
            dbc.Col(dbc.NavbarBrand("Pharmpy Model Builder", className="ms-5", style={"font-size" : "25px", "font-weight":"bold"}))
           ]
            ))



#TOGGLES
fix_all_toggle = html.Div(
    [
        dbc.Checklist(
            options=[
                {"label": "Fix all parameters", "value" : True, "disabled":False},
            ],
            id ="fix_all_toggle",
            value=[],
            switch=True
        )
    ],
)

PK_IIV_toggle = html.Div(
    [   dbc.InputGroup(children=[
        dbc.Checklist(
            options=[
                {"label": "", "value" : "True", "disabled":False},
            ],
            id ="pk_iiv_toggle",
            value=[],
        ),
        dbc.Badge("PK IIV", color="success", style={"font-size":"medium"})]
    )
    ],
)

lag_toggle = html.Div(
    [
        dbc.Checklist(
            options=[
                {"label": "Lag Time", "value" : True, "disabled":False},
            ],
            id ="lag-toggle",
            value=[],
        )
    ],
)

peripheral_toggle = html.Div(
    [
        dbc.Checklist(
            options=[
                {"label": "Peripheral Compartments", "value" : False, "disabled":False},
            ],
            id ="peripheral-toggle",
            value=[],
            switch=True,

        )
    ],
)

transit_toggle = html.Div(
    [
        dbc.Checklist(
            options=[
                {"label": "Transit Compartments", "value" : True, "disabled":False},
            ],
            id ="transit-toggle",
            value=[],
            switch=True,

        )
    ],
)
bioavailability_toggle = html.Div(
    [
        dbc.Checklist(
            options=[{
                "label" : "Bioavailability", "value" : 1
            }],
            value=[],
            id = "bio_toggle",
        )
    ]
)
covar_toggle = html.Div([
    dbc.Checklist(
        options=[
                {"label": "Covariance effect", "value" : False, "disabled":False},
            ],
            id ="covar-toggle",
            value=[],
            ###switch=True
    )
])

#TEXTFIELDS
model_covariate_list = html.Div(id="covar_div")

pop_parameters = dbc.Container([
    dbc.Badge("Population Parameter",
                            color="success", style={"font-size":"medium"}),
                    dbc.InputGroup(id="pop_param", children=[
                        dbc.Input(id="pop-param-name", placeholder="Name"),
                        dbc.Input(id="pop-param-init", placeholder="init"),
                        dbc.Input(id="pop-param-upper", placeholder="upper=None"),
                        dbc.Input(id="pop-param-lower", placeholder="lower=None"),
                        dbc.Select(id="pop-param-fix",
                                options=[{"label":"fix=False", "value":"False"},
                                {"label":"fix=True", "value":"True"}], placeholder="fix=False"),
                        dbc.Button("Create Population Parameter", id="pop-param-btn", color=btn_color, n_clicks=0),
                        ])
])

covariate_options =dbc.Container([
                    dbc.Badge("Specify Covariate",
                            color="success", style={"width":150, "font-size":"medium"}),
                    dbc.InputGroup(id="covar", children=[
                        dbc.Select(id="covar-param-name", placeholder="Parameter Name"),
                        dbc.Select(id="covar-name", placeholder="Covariate Name"),
                        dbc.Select(id="covariate-effect", options=covariate_effect, placeholder="Effect"),
                        dbc.Input(id="covar-custom-eff", placeholder="Custom Effect"),
                        dbc.Select(id="covar-operation", options=[
                            {"label":"operation= +", "value":"+"},
                            {"label":"operation= *", "value":"*"},
                        ], placeholder="operation, defeault *"),
                        dbc.Select(id="covar-allow-nestle", options=[
                            {"label":"allow-nestle=False", "value":"False"},
                            {"label":"allow-nestle=True", "value":"True"},
                        ], placeholder="allow-nestle=False"),
                        dbc.Button("Add Covariate", id="covar-btn", color=btn_color, n_clicks=0),
                    ])
])

distribution_compartments = dbc.Container([
    dbc.Badge("Specify Covariate",
            color="success", style={"width":150, "font-size":"medium"}),

])

allometry_multi_input=dbc.Container([
    dbc.ListGroup([
        dbc.ListGroupItem(
            dbc.Badge("Allometric Scaling", color="success", style={"width":150, "font-size":"medium"})),
        dbc.ListGroupItem(
            dbc.InputGroup(children=[
                dcc.Dropdown(id="allo_variable", placeholder="select variable",
                              multi=True, style={"flex":2}),
                dbc.Input(id="allo_custom",placeholder="custom variable", type="text")])),
        dbc.ListGroupItem(
            dbc.Input(id="allo_ref_val", placeholder="reference_value=70 (opt)", type="numeric")),
        dbc.ListGroupItem(
            dcc.Dropdown(id="allometry_dropdown", placeholder="parameters(opt)",multi=True)),
        dbc.ListGroupItem(
            dbc.Input(id="allo_inits", placeholder="intials (opt)")),
        dbc.ListGroupItem(
            dbc.Input(id="allo_lower", placeholder="lower (opt)",)),
        dbc.ListGroupItem(
            dbc.Input(id="allo_upper", placeholder="upper (opt)")),
        dbc.ListGroupItem(
            dbc.Select(id="allo_fix", placeholder="fixed=True (opt)",
                   options=[{"label":"True", "value":True},{"label":"False", "value":False}])),
        dbc.ListGroupItem(
            dbc.Button("Set Scaling",id="allo_btn", n_clicks=0, color=btn_color)
        )
    ]),

], style={"width":"50%"})

estimation_multi_input = dbc.Container([
    dbc.ListGroup([
        dbc.ListGroupItem(
            dbc.Badge("Estimation Step", color="success",
                      style={"width":150, "fontSize": "medium"})),
        dbc.ListGroupItem(
            dbc.Select(id="estimation_method", placeholder="select method",
                       options=estimation_methods)),
        dbc.ListGroupItem(
            dbc.Input(id="estimation_index", placeholder="index=None", type="number")),
        dbc.ListGroupItem(
            dbc.Select(id="estimation_covs", placeholder="cov", options=['SANDWICH', 'CPG', 'OFIM'])
        ),
        dbc.ListGroupItem(
            dbc.Checklist(id='int_eval_lapl',
                options=[
                    "interaction","evaluation","laplace"
                ],
                inline=True
            )) ,
        dbc.ListGroupItem(
            dbc.InputGroup(children=(
                dbc.Select(id="solver",placeholder="solver", options=[
                    'CVODES', 'DGEAR', 'DVERK', 'IDA', 'LSODA', 'LSODI'
                    ]),
                dbc.Input(id="solver_abstol", placeholder="absolute solver tolerance"),
                dbc.Input(id="solver_reltol", placeholder="relative solver tolerance")
            ))
        ),
        dbc.ListGroupItem(
            dbc.InputGroup(children=[
                dbc.Input(id="estimation_keywords", placeholder="tool option keywords"),
                dbc.Input(id="estimation_arguments", placeholder="tool option arguments")
                ])
                ),

        dbc.ListGroupItem(
            dbc.Button("Set Estimation Step", id="estimation_btn", n_clicks=0, color=btn_color,
            )),
        ]),
])

eval_multi_input = dbc.Container([
        dbc.ListGroup([
            dbc.ListGroupItem(
                dbc.Badge("Evaluation Step", color="success", style={"width":150, "fontSize": "medium"})
            ),
            dbc.ListGroupItem(
                dbc.Input(id="evaluation_index", placeholder="index", type='number'),
            ),
            dbc.ListGroupItem(
                dbc.Button("Set Evaluation", id="eval_btn", n_clicks=0, color=btn_color)
            ),
            ])
        ])


covariance_estimation = dbc.Container([
    dbc.ListGroup([
        dbc.ListGroupItem([
            dbc.Checkbox(
                id="covariance_check",
                label=dbc.Badge(
                    "Covariance on final estimation",
                    color="success",
                    style={"font-size": "medium"}
                )
            )
        ])
    ])
])



estimation_remove_multi = dbc.Container([
    dbc.ListGroup([
        dbc.ListGroupItem(
            dbc.Badge("Remove estimation", style={"width":150, "fontSize": "medium"}, color="success" )),
        dbc.ListGroupItem(
        dbc.InputGroup(children=[
            dbc.Input(id="remove_estimation", placeholder="index", type="number"),
            dbc.Button("Remove", id="remove_est_btn", n_clicks=0, color=btn_color)
        ]))
    ])
])


error_multi_input = dbc.Container([
    dbc.ListGroup([
        dbc.ListGroupItem(
            dbc.InputGroup(children=[
                            dbc.Checkbox(id="add_check", label =
                                        dbc.Badge("Additive",
                                                color="success", style={"width":150, "font-size":"medium"}),
                                                value = False ,
                                    style={"size": "md"}),
                            dbc.Input(id="add_dv", placeholder="dv=None", style={"width": "0.2"}),
                            dbc.Input(id="add_data_trans", placeholder="data_trans=None",style={"width": "0.2"}),
                            dbc.Input(id="add_series_terms", placeholder="series_terms=2",style={}),

                        ])
        ),

        dbc.ListGroupItem(
            dbc.InputGroup(children=[
                            dbc.Checkbox(id="comb_check", label =
                                        dbc.Badge("Combined",
                                                color="success", style={"width":150, "font-size":"medium"}),
                                                value = False,
                                        style={"size": "md"}),
                            dbc.Input(id="comb_dv", placeholder="dv=None",style={"width": "0.2"}),
                            dbc.Input(id="comb_data_trans", placeholder="data_trans=None",style={"width": "0.2"}),

                        ]),
        ),
        dbc.ListGroupItem(
            dbc.InputGroup(children=[
                            dbc.Checkbox(id="prop_check", label =
                                        dbc.Badge("Proportional",
                                                color="success", style={"width":150, "font-size":"medium"}),
                                                value = False,

                                        style={"size": "md"}),
                            dbc.Input(id="prop_dv", placeholder="dv=None",style={"width": "0.2"}),
                            dbc.Input(id="prop_data_trans", placeholder="data_trans=None", style={"width": "0.2"}),
                            dbc.Input(id="prop_zero_prot", placeholder="zero_protection=True",style={} )

                        ]),
        ),
        dbc.ListGroupItem(
            dbc.InputGroup(children=[
                            dbc.Checkbox(id="time_check", label =
                                        dbc.Badge("Time varying",
                                                color="success", style={"width":150, "font-size":"medium"}),
                                        style={"size": "md"}),
                            dbc.Input(id="time_cutoff", placeholder="cutoff", style={"width": "33%"}, type="number"),
                            dbc.Input(id="data_idv", placeholder= "idv='TIME'", style={"width": "33%"}),

                        ]),
        ),
        dbc.ListGroupItem(
            dbc.InputGroup(children=[
                            dbc.Checkbox(id="wgt_check", label =
                                        dbc.Badge("Weighted",
                                                color="success", style={"width":150, "font-size":"medium"}),
                            style={"size": "md"}),
                        ]),
        ),
    ])
])


model_output_text = html.Div([
    dcc.Clipboard(target_id= "output-model", title="copy",
                        style={"position": "relative", "top": "5vh", "right":"-25vw",
                               'width':'5vw', 'cursor':'pointer'}
                        ),
    dbc.Textarea(id = "output-model",
                readOnly = True,
                style={'font-family': 'Consolas', 'resize': 'None', 'width': '100%', 'height': '70vh', 'fontSize': '12px', "backgroundColor": '#fffff'},
                className = "text-success"),
    #Update interval value to change how often refresh happens
    dcc.Interval(id="text-refresh", interval=refreshtime*1000, n_intervals=0)
])
model_name = html.Div(children=[
    dbc.InputGroup([
    dbc.Badge("Model Name", color="success", style={"width":150, 'fontSize': 'medium'}),
    dbc.Input(id="model-name", placeholder= "Input model name", type="text")
    ],)

],)

model_description = html.Div(children=[
    dbc.InputGroup([
    dbc.Badge("Model Description", color="success", style={"width":150, 'fontSize': 'medium', } ),
    dbc.Input(id="model-description", placeholder="Input model description",type="text"),
    ], style={'marginTop':'5px'}),
], )


dataset = html.Div(children=[
    dbc.InputGroup([
        dcc.Upload(dbc.Button('Select Dataset', color=btn_color), id="upload-dataset"),
        dbc.Input(id="dataset-path", placeholder="No Dataset",type="text", disabled=True),

    ], style={"width":"50%"})
])

peripherals = dbc.InputGroup(children=[
                dbc.InputGroupText("Peripheral Compartments"),
                dbc.Input(id="peripheral_input", placeholder=0, type="number", min=0, step=1)
], style={"width":"70%"})

transits = dbc.InputGroup(children=[
                dbc.InputGroupText("Transit Compartments"),
                dbc.Input(id="transit_input", placeholder=0, type="number", min=0, step=1)
], style={"width":"70%"})

#RADIOBUTTONS

model_type_radio = dbc.Col(children=[
    dbc.Badge("Model Type", color = "success", style={"font-size": "large"}),
    dcc.RadioItems(typeoptions, "PK", id="model_type", style={"font-size": "large"})
    ])

model_format_radio = dbc.Col(children=[
    dbc.Badge("Model Format", color = "success", style={"font-size": "large"}),
    dcc.RadioItems(modelformats, 'nonmem', id='modelformat',
                   inputStyle={"font-size": "large", "margin":"10px" }, inline=True)
])

elimination_radio  = dbc.Col(children=[
    dbc.Badge("Elimination Rate", color = "success", style={"font-size": "large"}),
    dcc.RadioItems(elimination_rates, value="FO", id="elim_radio", style={"font-size": "large"})
])

route_radio = dbc.Col(children=[
    dbc.Badge("Administration Route", color = "success", style={"font-size": "large"}),
    dcc.RadioItems(admin_route, value='iv', id= "route-radio", style={"font-size": "large"})
])

abs_rates_radio = dbc.Col(children=[
    dbc.Badge("Absorption Rate", color = "success", style={"font-size": "large"}),
    dcc.RadioItems(options=absorptionrates,id = "abs_rate-radio", style={"font-size": "large"})
])
#DROPDOWNS

elim_dropdown = dcc.Dropdown(elimination_rates, id="elim-dropdown")

abs_rate_dropdown = dcc.Dropdown(absorptionrates, id="abs-dropdown")

error_dropdown = dcc.Dropdown(error_model, multi=True)

estimation_dropdown = dcc.Dropdown(estimation_methods)

#BUTTONS
error_button = dbc.Button(
    "Error Model",
    id = "err-btn",
    color=btn_color,
    n_clicks= 0,
)

abs_button = dbc.Button(
    "Absorption Rate",
    id = "abs-btn",
    color=btn_color,
    n_clicks= 0,
)

elim_button = dbc.Button(
    "Elimination Rate",
    id="elim-btn",
    color = btn_color,
    n_clicks= 0,
    size = "md"
)
download_model = dbc.Container([
    dbc.InputGroup([
        dbc.Button("Write model", id="download-btn", color=btn_color, style={"fontSize":"medium"}),
        dbc.Input(id="model_path", placeholder="model path")
        ]),
    html.Div(id="model_confirm")

])

model_format_button = dbc.Button(
    "Model Format",
    id="format-button",
    color=btn_color,
    n_clicks=0,
    size="md"
)

model_type_button = dbc.Button(
    "Model Type",
    id="type-button",
    color=btn_color,
            n_clicks=0,
    size="md"
)

route_button = dbc.Button(
    "Route",
    id = "route-button", color=btn_color, n_clicks=0, size="md"
)

#NOTE: not that good if used in collapse
button_group = dbc.ButtonGroup([
    model_format_button, model_type_button, route_button
]
)



#COLLAPSABLES
collapse_err = dbc.Collapse(
    error_dropdown, id = "collapse_err", is_open=True
)

collapse_elimination = dbc.Collapse(
    elim_dropdown, id="collapse_elim", is_open=True
)

collpasable_button_group = dbc.Collapse(
    button_group, id = "collapse_bg", is_open=True
)

collapsable_pk = dbc.Collapse(
    model_type_radio, id = "collapse_pk", is_open=True
)

collapsable_model = dbc.Collapse(
    model_format_radio, id= "collapse_model", is_open=True
)

collapsable_route = dbc.Collapse(
    route_radio, id = "collapse_route", is_open=True
)

abs_rate_collapse = dbc.Collapse(
                        dbc.Col(children=[
                            abs_rate_dropdown, lag_toggle,
                        ]),
                        id = "collapse_abs", is_open=True
)

collapse_PK_IIV = dbc.Row([
    dbc.Col(
        dbc.Collapse(children=[
            html.Br(),
            dbc.InputGroup(
                [
                dbc.Checkbox(id="pk_iiv_init_checkbox"),
                dbc.Input(id="pk_iiv_inp", placeholder="Change init_est (=0.09)?", type="number", style={"width":"50%"})
                ]
            )],
        id="PK_IIV-collapse",
        is_open=False,
        dimension="width"
        ),
    )

],
)

collapse_transit = dbc.Row([
    dbc.Col(
        dbc.Collapse([

            #dbc.Input(id="transit_input", placeholder=0, type="number", min=0, step=1),


            ],
        id="transit-collapse",
        is_open=True,
        dimension="width"
        ),
    )

],
)

collapse_peripheral = dbc.Row([
    dbc.Col(
        dbc.Collapse([

            #dbc.Input(id="peripheral_input", placeholder=0, type="number", min=0, step=1),


            ],
        id="peripheral-collapse",
        is_open=True,
        dimension="width"
        ),
    )

],
)
#Complete buttons

abs_rates = dbc.Col(children=[
    abs_button, abs_rate_collapse
])

elim_rates = dbc.Col(children=[
    elim_button, collapse_elimination
])

error_rates = dbc.Col(children=[
    error_button, collapse_err
])

iiv_inp_grp = dbc.ButtonGroup([
    dbc.Input(),
    dbc.Input(),
    dbc.Input(),
])

iov_table = dash_table.DataTable(
    id='iov_table',
    columns=[
    {'name': 'Parameter', 'id': 'parameter'},
    {'name': 'Occasion Column', 'id': 'occasion', 'presentation' : 'dropdown'},
    {'name': 'ETA Name', 'id':'eta_names'},
    {'name': 'Distribution', 'id': 'distribution', 'presentation':'dropdown' },
    ],
    dropdown= {

        'occasion': {
             'options' : []
        },

        'distribution' : {
        'options' : []
    },
       },

    editable=True,
    row_selectable='multi',

)

iiv_table = dash_table.DataTable(
    id='iiv_table',
    columns=[
    {'name': 'Parameter', 'id': 'parameter',},
    {'name': 'Expression', 'id': 'expression', 'presentation':'dropdown' },
    {'name': 'Custom', 'id':'custom'},
    {'name': 'Operation', 'id': 'operation', 'presentation':'dropdown' },
    {'name': 'Initial Estimate', 'id': 'initial_estimate', },
    {'name': 'ETA Name', 'id': 'eta_names'},
    ],
    dropdown= {
        'expression' : {
        'options' : [
            {'label': 'Additive' , 'value': 'add'},
            {'label': 'Proportional' , 'value': 'prop'},
            {'label': 'Exponential' , 'value': 'exp'},
            {'label': 'Logit' , 'value': 'log'},
            {'label':'Custom', 'value':'custom'},
        ]
    },
     'operation': {
         'options':[
             {'label': '+' , 'value': '+'},
            {'label': '*' , 'value': '*'},
         ]
     }
       },
    editable=True,

    row_selectable='multi',

)

covariance_matrix = dbc.Container([
    dash_table.DataTable(id="covariance_matrix")
    ])

all_parameters_table = dash_table.DataTable(
    id='parameter-table',
    columns=[
        {'name': 'Name', 'id': 'name', 'type': 'text', 'editable':False},
        {'name': 'Init', 'id': 'init', 'type': 'numeric'},
        {'name': 'Lower', 'id': 'lower', 'type': 'numeric'},
        {'name': 'Upper', 'id': 'upper', 'type': 'numeric' },
        {'name': 'Fix', 'id': 'fix', 'type': 'any' , 'presentation': 'dropdown'},
    ],
    editable=True,
    row_deletable=True,
    dropdown= {
        'fix' : {
        'options' : [
            {'label': 'true' , 'value': True},
            {'label': 'false' , 'value': False}
        ]
    } },

)

data_info_table = dash_table.DataTable(
    id='datainfo-table',
    style_cell={
        'whiteSpace': 'normal',
        'textAlign': 'left',
        #'font-family': 'Arial',
        'font-size': '16px',
        'padding': '12px'
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    },)


model_format_div = html.Div(children=[
                html.Hr(),
                model_format_radio,
                model_output_text,
                download_model,
                ])


allometry_tab = dbc.Container([
    dbc.Row([
        allometry_multi_input,


    ], justify="start")
]

)

structural_tab = dbc.Container([
    html.Hr(),
    dbc.Row([
        dbc.Col(children=[abs_rates_radio, ]),
        dbc.Col(elimination_radio)
    ]),
    dbc.Row([
        dbc.Col(children=[dbc.Badge("Absorption Delay", color="success", style={"font-size": "large"}),

            transits, lag_toggle, bioavailability_toggle]),
        dbc.Col(children=[dbc.Badge("Distribution", color="success", style={"font-size": "large"}),
            peripherals])
  ]),


])

par_var_tab = dbc.Container([
    dbc.Row(children=[
    dbc.Col([dbc.Badge("Model IIVs", color="success", style={"font-size": "large"}),
             iiv_table,
             ])
    ]),
    dbc.Row(children=[
    dbc.Col([dbc.Badge("Model IOVs", color="success", style={"font-size": "large"}),
            iov_table,
            ])
]),
    dbc.Row(children=[
    dbc.Col([
        dbc.Badge("Model Covariance Matrix", color="success", style={"font-size": "large"}),
        covariance_matrix,
        ])
    ])

])

parameter_tab = dbc.Container(
    [
        html.P("Parameters"),
        fix_all_toggle, html.Hr(), pop_parameters, html.Hr(),
        all_parameters_table,
    ],
    className="mt-4"
)

base_tab = dbc.Container([
       dbc.Col(children=[
            html.Hr(),
            html.P("Base Model Options"),
            dbc.Row([
                dbc.Col(model_type_radio),
                dbc.Col(route_radio)],
                style={"height":"20vh"}),
            dbc.Row([
                dbc.Col(children=[model_name, model_description
                                  ], style={},),
                dbc.Col(children=[

                    ], style={"height":"20vh"}),
                ], style={}),
            dbc.Row([
                dbc.Col(dataset)
                ], style={}),
        ])



],
style={
    "display": "flex",
}
    )

error_tab = dbc.Container([

    dbc.Col(children=[
        html.Hr(),
        html.P("Error Model"),
    error_multi_input,
    html.Div(id="error_div")
    ]),

])


covariate_tab = dbc.Container([
    html.Hr(),
    html.P("Covariates"),
    dbc.Row(covariate_options),
    html.Hr(),
    html.P("Covariates"),
    model_covariate_list

])

datainfo_tab = dbc.Container([
    html.Hr(),
    html.P("Model DataInfo"),
    dash_table.DataTable(id="datatable",
    columns=cols,
    editable=True,
    dropdown = dd,),

    dbc.Container([
        dbc.Button("Download DataInfo", id="makedatainf", n_clicks = 0, color=btn_color),
        dcc.Download("download_dtainf")]),




])

estimation_tab = dbc.Container([
    dbc.Row([
    dbc.Col([estimation_multi_input, covariance_estimation]),
    dbc.Col([eval_multi_input, estimation_remove_multi])
    ]),

])


all_tabs = html.Div(dcc.Tabs(id="all-tabs", value='base-tab',
                    children=[dcc.Tab(label = "Base", value = 'base-tab', children=base_tab),
                              dcc.Tab(label= "DataInfo", value = 'data-info-tab', children = datainfo_tab),
                              dcc.Tab(label = "Structural", value = 'structural-tab', children=structural_tab),
                              dcc.Tab(label ='Parameters', value='parameters-tab', children=parameter_tab),
                              dcc.Tab(label='Parameter Variability', value='par-var-tab', children=par_var_tab),
                              dcc.Tab(label="Error Model", value="error-tab", children=error_tab),
                              dcc.Tab(label="Covariates", value="covariate-tab", children=covariate_tab),
                              dcc.Tab(label="Allometry",value="allometry-tab", children=allometry_tab),
                              dcc.Tab(label="Estimation", value="estimation-tab", children=estimation_tab)
                              ], className='nav-link active')


), html.Div(id='tab-content', children=[])


layout = dbc.Container([
    dcc.Store(id="data-dump"),
    navbar,
    dbc.Row([
        dbc.Col(children=[
            model_format_div
            ],
            width=4),
        dbc.Col(all_tabs, width=8)
        ], style={'width':'100vw', }),
    ],style={'height': '100vh', 'width': '100vw', "margin-bottom": "0%", }, fluid=True)
