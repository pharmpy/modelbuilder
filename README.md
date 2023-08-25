<img src="https://pharmpy.github.io/latest/_images/Pharmpy_logo.svg"> 

# PharmpyModelbuilder.Alpha 

**WARNING** 

This app is in early **alpha** stages and everything is subject to change.

Please open issues so they can be resolved and the **ModelBuilder** can be improved.

**WARNING**

---
## INFO

**PharmpyModelbuilder** is a **user interface** with the aim to provide a more graphical approach to using most of [Pharmpy](https://pharmpy.github.io/latest/index.html)'s functionality.
A user can thus create a basic model, make changes in it and **live** see how it affects the model code. 

Current functionality is:
- Creating a basic PK model
    - Specifying its route, name, description
- Simultaneous update and switching between model code in formats:
    - **nonmem**
    - **rxode2**
    - **nlmixr**
- Modify the **DataInfo** file from a dataset
- Make changes to model parameters, distributions, elimination
- Write the model to path 

## Installation

To setup, clone this repository into a folder.
This can be run directly on top of your `python` client or in a `venv`.

To create a `venv` with the name ``pharmpy_ui`` run the following command:
```
python -m venv pharmpy_ui
```
Then activate it using:

**Windows**
```
cd /path/modelbuilder/pharmpy_ui
scripts/activate.ps1
```

**Linux**
```
cd /path/modelbuilder/pharmpy_ui
source bin/activate
```

Once done, navigate to the `/modelbuilder` folder and install necessary packages from **requirements.txt** using

`pip install -r requirements.txt`

## Run the app
To start the app:

`python app.py`

It should look something like
```
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://127.0.0.1:8050 (Press CTRL+C to quit)
```

The app will then be hosted on `http://127.0.0.1:8050/`, navigate to that in your browser and you should see the app. 

