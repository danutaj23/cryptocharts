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
db_nbp_source = config[server_type]['db_nbp_source']  # path to DB file
img_folder = config[server_type]['img_source']
app = dash.Dash(__name__)

def usd_price():
    conn = sqlite3.connect(db_nbp_source)
    usd_price = pd.read_sql("SELECT * FROM usd_pln ORDER BY 1 DESC LIMIT 1", conn)
    conn.close()
    price = float(usd_price['value'])
    current_date = str(usd_price['date'][0])
    return price, current_date

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

app.layout = html.Div(children=[
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
             style={
                 'position': 'absolute',
                 'zIndex': '0',
                 'left': '0px,',
                 'top': '5px',
                 'width': '80px'
}),
    html.H2('Ceny kryptowalut',
            style={'textAlign': 'center', 'color': '#354B5E'}),
    html.Div([
        html.H3('Wybierz kryptowalutę '
                )],
            style={'width': '30%',
                'display': 'inline-block',
                'margin': '1% 1% 1% 1%',
                'text-align': 'right',
                'vertical-align': 'middle'
                }),

    html.Div([
        dcc.Dropdown(id='yaxis-column', options=[{'label': crypto, 'value': crypto} for crypto in available_crypto], value='bitcoin')
            ],
            style={'width': '30%',
                   'display': 'inline-block',
                   'vertical-align': 'middle'}),
    html.Div([html.H3(id='nbp_usd_price')],
             style={'width': '20%',
                    'display': 'inline-block',
                    'margin': '1% 1% 1% 2%',
                    'text-align': 'right',
                    'vertical-align': 'middle'
                    }),

    html.Div([
        dcc.Graph(id='live-graph', animate=False, config={'displayModeBar': False})
        ],),
    dcc.Interval(id='graph-update', interval=30*1000),
    html.Div([html.Div('Średnia cena dolara: '+ str(usd_price()[0]) +' PLN'),
              html.Div(' Według kursu NBP z dnia: ' +str(usd_price()[1]))],
        style={'text-align': 'center', 'font-weight': 'bold'}
             ),
    html.Div([
         html.H3("[Baza wiedzy] Abc kryptowalut"),
         html.P('Kryptowaluta jest środkiem wymiany jak normalne waluty typu dolar, jednak skonstruowana na potrzeby '
                'wymiany informacji poprzez proces używający określonych zasad z kryptografii. Kryptografia pozwala '
                'zabezpieczyć te transakcje i tworzenie nowych jednostek waluty. Pierwsza kryptowaluta czyli Bitcoin '
                'była stworzona w 2009 roku.',
               className='article',
               id='regulations'),
         html.A("Czytaj więcej",
                href='https://businessinsider.com.pl/finanse/kryptowaluty/czym-sa-bitcoiny-i-kryptowaluty/05f5ned',
                target='blank')
         ],
         style={"width": "25%",
                "margin": "2% 4%",
                "display": "inline-block"}),
     html.Div([
         html.H3("[Prawo] Legalne środowisko wokół Bitcoina"),
         html.P('Wraz z wzostem popytu na kryptowaluty, globalni regulatorzy są podzieleni jak za tym nadążyć. '
                'W Większości kryptowaluty nie są wspierane przez rządy, co znaczy, że każdy kraj ma inne standardy. '
                'W tym artykule przeczytasz jak w regulatorzy i rządy radzą sobie z tym problemem.',
               className='article',
               id='regulations'),
         html.A("Czytaj więcej po angielsku",
                href='https://www.cnbc.com/2018/03/27/a-complete-guide-to-cyprocurrency-regulations-around-the-world.html',
                target='blank')
         ],
         style={"width": "25%",
                "margin": "2% 4%",
                "display": "inline-block"}),
     html.Div([
         html.H3("[Opinie] W co inwestować?"),
         html.P('Rynek finansowy zmienia się, wielu ludzi uświadomiło to sobie w momencie gdy Bitcoin i inne '
                'kryptowaluty stały się gorącym tematem. Teraz gdy jesteśmy w roku 2018 możemy bezpiecznie powiedzieć, '
                'że kryptowaluty są mocniejsze niż kiedykolwiek. Pośród mniej znanych największymi zwycięzcami są m.in. '
                'Stellar Lumens, IOTA, EOS.',
               className='article',
               id='regulations'),
         html.A("Czytaj więcej po angielsku",
                href='https://www.mineweb.net/best-cryptocurrency-to-invest-in-2018',
                target='blank')
         ],
         style={"width": "25%",
                "margin": "2% 4%",
                "display": "inline-block",
                'vertical-align': 'top'}),

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
        all_currencies_data.sort_values('last_updated', inplace=True)   # sortowanie wg czasu ## TODO do sprawdzenia czy jest wymagane
        all_currencies_data['date'] = pd.to_datetime(all_currencies_data['last_updated'], unit='s', utc=True)  # zmiana timestampa na czas
        all_currencies_data['date'] = all_currencies_data['date'] + pd.Timedelta('02:00:00')
        #all_currencies_data['date'] = all_currencies_data['date'].tz_convert('Asia/Kolkata')
        all_currencies_data.set_index('date', inplace=True)
        X = all_currencies_data.index[-100:]
        Y = all_currencies_data.price_usd.values[-100:]
        data = plotly.graph_objs.Scatter(
            x=X,
            y=Y,
            name='Scatter',
            mode='lines+markers'
        )
        return{'data': [data], 'layout': go.Layout(xaxis={'range': [min(X), max(X)], 'title': 'Czas'},#, 'tickformat': '%m/%d:%H'},https://community.plot.ly/t/how-to-make-the-messy-date-ticks-organized/7477/3
                                                   yaxis={'range': [min(Y), max(Y)], 'title': 'Wartość w $'}), }
    except Exception as e:
        with open('errors.txt', 'a') as error_log:
            error_log.write(str(datetime.datetime.fromtimestamp(time.time())) + ': ' + str(e))
            error_log.write('\n')
            error_log.close()

@app.callback(
    Output(component_id='nbp_usd_price', component_property='children'),
    [Input(component_id='yaxis-column', component_property='value')]
)
def update_value(cryptocurrency):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT price_usd FROM " + cryptocurrency + " ORDER BY last_updated DESC limit 1")
    data = c.fetchall()
    c.close()
    conn.close()
    return 'Aktualny kurs: {} $, {} PLN'.format(round(data[0][0],3), round(data[0][0]*usd_price()[0], 3))

#### PROD ####
if server_type == 'PROD':
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
