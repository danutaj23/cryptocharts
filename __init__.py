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
import base64

###CONFIG PART
config = configparser.ConfigParser()
if config.read('config/config.conf'):
    ## DEV
    server_type = config['DEFAULT']['servertype']
elif config.read('/var/www/FlaskApp/FlaskApp/config/config.conf'):
    ## PROD
    server_type = config['DEFAULT']['servertype']
else:
    with open('errors.txt', 'a') as error_log:
        error_log.write(str(datetime.datetime.fromtimestamp(time.time())) + ': ' + "Can't open config.conf file!")
        error_log.write('\n')
        error_log.close()

db_file = config[server_type]['db_source']  # path to DB file
img_folder = config[server_type]['img_source']
app = dash.Dash(__name__)

conndb = sqlite3.connect(db_file)
currency_select = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1 ASC", conndb)
### Pytanie: czy potrzebne
bitcoin_quotes = pd.read_sql("SELECT * FROM bitcoin ORDER BY last_updated DESC", conndb)
available_crypto = currency_select['name'].unique()
### Pytanie: czy potrzebne
bitcoin_quotes['date'] = pd.to_datetime(bitcoin_quotes['last_updated'], unit='s', utc=True)



conndb.close()

image_filename = img_folder + 'logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.title = 'CryptoChart'

app.layout = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
             style={
                 'position': 'absolute',
                 'zIndex': '0',
                 'left': '0px,',
                 'top': '5px',
                 'width': '80px'
}),
    html.H2('Live Cryptocurrency Price',
            style={'textAlign': 'center', 'color': '#354B5E'}),
    html.Div([
        html.H3('Choose cryptocurrency to display: '
                )],
            style={'width': '40%',
                'display': 'inline-block',
                'margin': '1% 1% 1% 1%',
                'text-align': 'right',
                'vertical-align': 'middle'
                }),

    html.Div([
        dcc.Dropdown(id='yaxis-column', options=[{'label': crypto, 'value': crypto} for crypto in available_crypto], value='bitcoin')
            ],
            style={'width': '40%',
                   'display': 'inline-block',
                   'vertical-align': 'middle'}),


    dcc.Graph(id='live-graph', animate=False, config={'displayModeBar': False}),
    dcc.Interval(id='graph-update', interval=30*1000)

],
style={'backgroundColor': '#FFFEFE',
       'fontFamily': 'Calibri',
       'color': '#354B5E',
       'width': '84%',
       'marginLeft': 'auto',
       'marginRight': 'auto'}
)


@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='yaxis-column', component_property='value')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(selected_crypto):
    try:
        conndb = sqlite3.connect(db_file)
        query = 'SELECT * FROM ' + selected_crypto + ' ORDER BY last_updated DESC'
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
        return{'data': [data], 'layout': go.Layout(xaxis={'range': [min(X), max(X)], 'title': 'Time'},
                                                   yaxis={'range': [min(Y), max(Y)], 'title': 'Value in USD'}), }
    except Exception as e:
        with open('errors.txt', 'a') as error_log:
            error_log.write(str(datetime.datetime.fromtimestamp(time.time())) + ': ' + str(e))
            error_log.write('\n')
            error_log.close()



#### PROD ####
if server_type == 'PROD':
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
