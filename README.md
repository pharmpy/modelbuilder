<img src="https://pharmpy.github.io/latest/_images/Pharmpy_logo.svg"> 

# Pharmpy Model Builder

## Overview

The Pharmpy model builder is a **graphical user interface** for the creation of pharmacometric models.
A user can create a basic model, make changes to it and **live** see how it affects the model code in different
modeling languages.

## Installation

Install the modelbuilder GUI, either globally or in a virtual environment, using pip:

```
pip install git+https://github.com/pharmpy/modelbuilder.git
```

## Run the app

To start the app:

`pharmpy-modelbuilder`

In the command line this should look something like:

```
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:8050 (Press CTRL+C to quit)
```

and a tab with the GUI should open in your browser. If not you could try to navigate to `http://127.0.0.1:8050/` in the browser.

## Development

Developers needs to have the python tox package installed and can start the app with `tox -e serve`
