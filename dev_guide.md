## General
This is for anyone who want to contribute to **Pharmpy Modelbuilder**, but mainly aimed towards the developers at **Pharmpy**.

This app is built using a combination of **pharmpy** and **dash** in a fairly unique way. 

## File Structure

```app.py
config.py
designfile.py
assets/
└── datatable.css
callbacks/
├── allometry.py
├── base.py
├── covariates.py
├── datainfo.py
├── error_model.py
├── estimation.py
├── parameter_variability.py
└── structural.py
dataset/
```
**config.py** contains the **model** object which on boot is a **iv basic pk model** and in nonmem format. 
Almost all callbacks references and modifies this **model** object. 

The app is created, initialized and hosted in **app.py**. 

All structural components can be found in **designfile.py**.

In **callbacks**, individual callbacks for different tabs can be found. 

## Booting
The app is launched by running
 ```python app.py``` in the commandline and will then be hosted locally by default in debug mode on http://127.0.0.1:8050/.
To alternate mode, change ```app.run_server(debug=True)``` in **app.py**.
For future deployment **https://dash.plotly.com/deployment** is a good source. 

The structure of the app is constructed from **df.layout** (df referencing **designfile.py**). 
Then all callbacks that can be fired are fired in order of the file structure. 
## Layout
The layout of a page is built in a **dbc.container** with a set of **dbc.rows** and **dbc.columns**. 
In these rows and coulmns are individual components placed, such as buttons, textareas etc. 

Writing these generally follows the same principle, but some components have specific attributes connected to them. 

Lets take ``model_name`` as an example:
```
model_name = html.Div(children=[
    dbc.InputGroup([
    dbc.Badge("Model Name", color="success", style={"width":150, 'fontSize': 'medium'}),
    dbc.Input(id="model-name", placeholder= "Input model name", type="text")
    ],)
```
``model_name`` consists of a ``html.Div`` with the children ``dbc.InputGroup([dbc.Badge, dbc.Input])``.
The ``dbc.Badge`` is a style component, but ``dbc.Input`` is something used, hence the need to give it an id attribute. 
The id of an object is something that can be referenced in callbacks and are uniquely defined. 

You might notice ```style={"width":150, 'fontSize': 'medium'}```which is where specific css styling for that object can be applied. 

# Callbacks and callback structure
For full callback documentation, please see
:

-   https://dash.plotly.com/basic-callbacks 

-   https://dash.plotly.com/advanced-callbacks
## General callback
A general callback is written as following
```
@app.callback(
    Output("id_output", "parameter/children"),
    Input("id_input", "parameter/value"),
    #OPTIONAL
    State("id_state", "parameter/value")
)

def do_something(input_parameter, state_parameter):

    output = #do something with the parameters

    #return it to output component
    return output
    
```
The callback is triggered everytime the **Input** is changed, but not when **State** is changed. 

A dash callback **MUST** have both **Input** and **Output**, but often in **Modelbuilder** we only want to change something in the **model** object. This is circumvented by many callbacks having **data-dump** as output id, and **clear_data=True** as its parameter, which is a hidden component where you essentially do nothing but erase all its data (which is None from the beginning). 

## Chaining Callbacks

A callback is triggered when its **Input** is updated, and by setting the **Output** of one component as the input of another, you achive a chaining effect. 

```
@app.callback(
    Output("component_1", "value"),
    Input("input_0", "value")
)

def update_comp_1(value):
    return value #to component 1


@app.callback(
    Output("component_2", "value"),
    Input("component_1", "value")
)

def update_comp_2(value):
    return value #to component 2 
```

Here component_1 is updated when input_0 changes value, which in turn trigger the callbacks that updates component_2, so the value in input_0 is passed onto component_2 "through" component_1. 

The main takeaway is that input_0 has component_1 as output, and component_2 has component_1 as input, so any change in component_1 will trigger the callback to change component_2.

This is something that can be very useful but might also lead to never ending loops if you are not careful, especially if you have multiple inputs and outputs in multiple calbacks. 

## How to not trigger callbacks
### State, prevent_initial_call, and PreventUpdate
State is a part of ```@app.callback``` that can be very useful in many cases. 
A **State** is something that can be added as an additional parameter, but does not trigger the callback when changed.
Example update text when pressing button:
```
@app.callback(
    Output("text_id", "children"),
    Input("button_id", "n_clicks"),
    State("input_text", "value")
)
def update_on_click(n_clicks, value):
    return value
```
Since the callback is only triggered when the n_clicks of the button is updated, a change in the input text will **not trigger** the callback.

As soon as **n_clicks** changes, the value of "input_text" is returned to "text_id". 

### prevent_initial_call=True:
This is an addition to a callback, causing it to not trigger when the app is first launched. 
```
@app.callback(
    Output("text_id", "children"),
    Input("button_id", "n_clicks"),
    State("input_text", "value"),
    prevent_initial_call=True
)
def update_on_click(n_clicks, value):
    return value
```
This callback will not trigger when the app first launches. 

### PreventUpdate
This can be raised to catch errors or to not update components in certain conditions.
```
@app.callback(
    Output("text_id", "children"),
    Input("button_id", "n_clicks"),
    State("input_text", "value"),
    prevent_initial_call=True
)
def update_on_click(n_clicks, value):
    if n_clicks > 0:
        return value
    else:
        raise PreventUpdate
```