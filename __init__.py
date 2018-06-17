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
offsets = {'hour': 3600, '4hours': 14400, 'day': 86400, 'week': 604800, 'month': 2592000}
offset = 'day'
date_marks = {}

### Pytanie: czy potrzebne
bitcoin_quotes['date'] = pd.to_datetime(bitcoin_quotes['last_updated'], unit='s', utc=True)



conndb.close()

image_filename = img_folder + 'logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.title = 'CryptoCharts'

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
            style={'width': '20%',
                'display': 'inline-block',
                'margin': '1% 1% 1% 1%',
                'text-align': 'right',
                'vertical-align': 'middle'
                }),

    html.Div([
        dcc.Dropdown(id='yaxis-column', options=[{'label': crypto, 'value': crypto} for crypto in available_crypto],
                     value='bitcoin', clearable=False,)
            ],
            style={'width': '20%',
                   'display': 'inline-block',
                   'vertical-align': 'middle'}),
    html.Div([
        html.H3('Wybierz kryptowalutę do porównania '
                )],
        style={'width': '20%',
               'display': 'inline-block',
               'margin': '1% 1% 1% 1%',
               'text-align': 'right',
               'vertical-align': 'middle'
               }),
    html.Div([
        dcc.Dropdown(
            id='yaxis1-column',
            options=[{'label': crypto, 'value': crypto} for crypto in available_crypto],
            value='',
            placeholder="Wybierz kryptowalutę"
        )
    ],
        style={"width": "20%",
               "display": "inline-block",
               'vertical-align': 'middle'}),

    html.Div([html.H4(id='nbp_usd_price1')],
             style={'width': '35%',
                    'margin': '-3% 1% 1% 2%',
                    'text-align': 'right',
                    'vertical-align': 'text-top',
                    "display": "inline-block"
                    }),
    html.Div([html.H4(id='nbp_usd_price2')],
             style={'width': '35%',
                    'margin': '-3% 1% 1% 2%',
                    'text-align': 'right',
                    'vertical-align': 'text-top',
                    "display": "inline-block"
                    }),

    html.Div([
        dcc.Graph(id='live-graph', animate=False, config={'displayModeBar': False})
        ],),
    dcc.Interval(id='graph-update', interval=30*1000),
    html.Div([
        html.H3('Wybierz okres '
                )],
        style={'width': '35%',
               'display': 'inline-block',
               'margin': '1% 1% 1% 1%',
               'text-align': 'right',
               'vertical-align': 'middle'
               }),
    html.Div([
        dcc.Dropdown(
            id='time-offset',
            options=[
                {'label': '1 godzina', 'value': 'hour'},
                {'label': '4 godziny', 'value': '4hours'},
                {'label': '1 dzień', 'value': 'day'},
                {'label': '1 tydzień', 'value': 'week'},
                {'label': '1 miesiąc', 'value': 'month'},
            ],
            value='day',
            clearable=False,
        )
    ],
        style={"width": "35%",
               "display": "inline-block",
               'vertical-align': 'middle'}),
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

    html.Br(),
    html.Br(),
    html.Div([
        'Strona korzysta z danych udostępnianych przez: ',
        html.A('Narodowy Bank Polski',
               href='http://www.nbp.pl/',
               target='blank'),
        ', ',
        html.A('CoinMarketCap',
               href='https://coinmarketcap.com/',
               target='blank'),
        '.'
    ],
        style={'text-align': 'center'}
    ),
    html.Br(),
    html.Div([
        html.Div('Copyrights 2018 by CryptoChartsTeam (SPIO 2018)'),
        html.A('GitHub',
               href='https://github.com/spio2018/cryptocharts',
               target='blank'),
    ],
        style={'text-align': 'center'}
    )

],
style={'backgroundColor': '#FFFEFE',
       'fontFamily': 'Calibri',
       'color': '#354B5E',
       'width': '95%',
       'marginLeft': 'auto',
       'marginRight': 'auto'}
)


@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='yaxis-column', component_property='value'),
               Input(component_id='yaxis1-column', component_property='value'),
               Input(component_id='time-offset', component_property='value')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(selected_crypto1, selected_crypto2, date_scope):
    offset = offsets[date_scope]
    conn = sqlite3.connect(db_file)
    if (selected_crypto1):
        query1 = "SELECT * FROM " + selected_crypto1 + " ORDER BY last_updated DESC"
        query_name1 = "SELECT name FROM " + selected_crypto1 + " LIMIT 1"
        all_currencies_data1 = pd.read_sql(query1, conn)
        currency_name1 = pd.read_sql(query_name1, conn)
        all_currencies_data1.sort_values('last_updated', inplace=True)  # sortowanie danych wg. czasu
        updates_times1 = all_currencies_data1['last_updated']
        oldest_record1 = updates_times1.max() - offset if updates_times1.max() - offset > updates_times1.min() else updates_times1.min()
        scoped_currencies1 = all_currencies_data1.loc[all_currencies_data1['last_updated'] > oldest_record1]
        scoped_currencies1['date'] = pd.to_datetime(updates_times1, unit='s', utc=True)  # zamiana unix_na datę-czas
        scoped_currencies1.set_index('date', inplace=True)  # dodanie lidexu na datę-czas
        X1 = scoped_currencies1.index
        Y1 = scoped_currencies1.price_usd.values
        data1 = plotly.graph_objs.Scatter(
            x=X1,
            y=Y1,
            name=str(currency_name1['name'][0]),
            mode='lines'
        )
    if (selected_crypto2):
        query2 = "SELECT * FROM " + selected_crypto2 + " ORDER BY last_updated DESC"
        query_name2 = "SELECT name FROM " + selected_crypto2 + " LIMIT 1"
        all_currencies_data2 = pd.read_sql(query2, conn)
        currency_name2 = pd.read_sql(query_name2, conn)
        all_currencies_data2.sort_values('last_updated', inplace=True) # sortowanie danych wg. czasu
        updates_times2 = all_currencies_data2['last_updated']
        oldest_record2 = updates_times2.max() - offset if updates_times2.max() - offset > updates_times2.min() else updates_times2.min()
        scoped_currencies2 = all_currencies_data2.loc[all_currencies_data2['last_updated'] > oldest_record2]
        scoped_currencies2['date'] = pd.to_datetime(updates_times2, unit='s', utc=True) #zamiana unix_na datę-czas
        scoped_currencies2.set_index('date', inplace=True) #dodanie lidexu na datę-czas
        X2 = scoped_currencies2.index
        Y2 = scoped_currencies2.price_usd.values
        data2 = plotly.graph_objs.Scatter(
            x=X2,
            y=Y2,
            name=str(currency_name2['name'][0]),
            mode='lines',
            yaxis='y2'
        )
    conn.close()
    if (selected_crypto1 and selected_crypto2):
        return {'data': [data1, data2], 'layout': go.Layout(
            xaxis=dict(range=[min(X1), max(X1)]),
            yaxis=dict(range=[min(Y1), max(Y1)], title='Cena ' + str(currency_name1['name'][0])),
            yaxis2=dict(range=[min(Y2), max(Y2)], title='Cena ' + str(currency_name2['name'][0]), overlaying='y', side='right'),
            margin={'l': 60, 'b': 45, 't': 45, 'r': 60, 'pad': 13},
            legend={'orientation': 'h', 'x': 0.40, 'y': 1.1, 'xanchor': 'left', 'yanchor': 'top'}
        )}
    elif (selected_crypto1 and not selected_crypto2):
        return {'data': [data1], 'layout': go.Layout(
            xaxis=dict(range=[min(X1), max(X1)]),
            yaxis=dict(range=[min(Y1), max(Y1)], title='Cena ' + str(currency_name1['name'][0])),
            margin={'l': 60, 'b': 45, 't': 45, 'r': 60, 'pad': 13},
            legend={'orientation': 'h', 'x': 0.40, 'y': 1.1, 'xanchor': 'left', 'yanchor': 'top'}
        )}

@app.callback(
    Output(component_id='nbp_usd_price1', component_property='children'),
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

@app.callback(
    Output(component_id='nbp_usd_price2', component_property='children'),
    [Input(component_id='yaxis1-column', component_property='value')]
)
def update_value2(cryptocurrency):
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("SELECT price_usd FROM " + cryptocurrency + " ORDER BY last_updated DESC limit 1")
        data = c.fetchall()
        c.close()
        conn.close()
        return 'Aktualny kurs: {} $, {} PLN'.format(round(data[0][0],3), round(data[0][0]*usd_price()[0], 3))
    except:
        pass

#### PROD ####
if server_type == 'PROD':
    server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
