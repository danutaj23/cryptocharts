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
    ## DEV
    server_type = config['DEFAULT']['servertype']
elif config.read('/var/www/FlaskApp/FlaskApp/config/config.conf'):
    ## PROD
    server_type = config['DEFAULT']['servertype']
else:
    pass ## TODO dorobić obsługę błędu

db_file = config[server_type]['db_source'] # path to file
app = dash.Dash(__name__)

conndb = sqlite3.connect(db_file)
test = pd.read_sql('SELECT * FROM bitcoin ORDER BY last_updated DESC', conndb)
conndb.close()

app.layout = html.Div([
        html.H2('Live Cryptocurrency Price',
                style={'textAlign': 'center', 'color': '#354B5E'}),

    dcc.Graph(id='live-graph', animate=True),
    dcc.Interval(id='graph-update', interval=10*1000)
])


@app.callback(Output('live-graph', 'figure'),
              events=[Event('graph-update', 'interval')])
def update_graph_scatter():
    conndb = sqlite3.connect(db_file)
    query = 'SELECT * FROM bitcoin ORDER BY last_updated DESC'
    all_currencies_data = pd.read_sql(query, conndb)
    all_currencies_data.sort_values('last_updated', inplace=True)   # sortowanie wg czasu
    all_currencies_data['date'] = pd.to_datetime(all_currencies_data['last_updated'], unit='s', utc=True)  # zmiana timestampa na czas
    all_currencies_data.set_index('date', inplace=True)
    X = all_currencies_data.index[-100:]
    Y = all_currencies_data.price_usd.values[-100:]
    data = plotly.graph_objs.Scatter(
        x=X,
        y=Y,
        name='Scatter',
        mode='lines+markers'
    )
    return{'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]),
                                               yaxis=dict(range=[min(Y), max(Y)]),)}


#### PROD ####
if server_type == 'PROD':
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
