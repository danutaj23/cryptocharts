#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import sqlite3
import pandas as pd
import datetime
import time
import configparser

###CONFIG PART
config = configparser.ConfigParser()
if config.read('config/config.conf'):
    ##DEV
    server_type = config['DEFAULT']['servertype']
elif config.read('/var/www/FlaskApp/FlaskApp/config/config.conf'):
    ## PROD
    server_type = config['DEFAULT']['servertype']
else:
    pass ## TODO dorobić obsługę błędu

db_file = config[server_type]['db_source'] # path to file
app = dash.Dash(__name__)

app.layout = html.Div([
        html.H2('test')
])


####  PROD ####
if server_type == 'PROD':
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
