import json
from urllib import request
import pandas as pd
import datetime
import time
import sqlite3
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
    pass ##TODO dorobić obsługę błędu

dataLink = config['DEFAULT']['dataLink']
db_file = config[server_type]['db_source'] #path to db file
db_log =  config[server_type]['log_db'] #path to db log file
sleep_time = int(config['DEFAULT']['sleep_time']) #czas pomiędzy odczytami danych

db_data_types = {'24h_volume_usd': 'REAL', 'available_supply': 'REAL', 'id': 'TEXT', 'last_updated': 'REAL',
              'market_cap_usd': 'REAL', 'max_supply': 'REAL', 'name': 'TEXT', 'percent_change_1h': 'REAL',
              'percent_change_24h': 'REAL', 'percent_change_7d': 'REAL', 'price_btc': 'REAL', 'price_usd': 'REAL',
              'rank': 'INTEGER', 'symbol': 'TEXT', 'total_supply': 'REAL'}

def main():

    #TODO dodać inkrementację indexu
    #ids = data[data['id'] == 'bitcoin']




    # TODO dodać obsługe przerwania pętli
    #########################################################
    ###DEV
    if server_type == 'DEV':
        while True:
            data = request.urlopen(dataLink)
            data = data.read().decode("utf-8")
            data = json.loads(data)
            data = pd.DataFrame(data)
            continiousreading(data) #nieskończona pętla, która zczytuje dane
    ##PROD################################################### umieszczone w cron
    elif server_type == 'PROD':
        data = request.urlopen(dataLink)
        data = data.read().decode("utf-8")
        data = json.loads(data)
        data = pd.DataFrame(data)
        continiousreading(data)
    else:
        pass #TODO dodać obsługę błedu

def timestamp2time(ts):
    #jeśli ts nie jest INT to konwertuj na INT
    #TODO dodać obsługe błędu
    if not isinstance(ts,int):
        ts = int(ts)
    _time = datetime.datetime.fromtimestamp(ts)  #konwersja z linux timestamp na datę
    return _time

def replace_str(str_to_fix):
    corected = {'0':'O', '-':'_'}
    for i in corected.keys():
        str_fixed = str_to_fix.replace(i,corected[i])
        str_to_fix = str_fixed
    return str_fixed

def continiousreading(data):
    #TODO dodać sprawdznie czy dane się zmieniły, jeśli nie to nic nie robić
    conn = sqlite3.connect(db_file)
    datafile = open(db_log, 'a')
    kolumna_danych = data.loc[:, 'id']   #bierzemy z DataFrame tylko kolumnę z 'id'
    datafile.write(str(timestamp2time(time.time()))+ ' : Zaczynam zapis danych')
    for k in range(0,len(kolumna_danych)):  #przechodzimy przez wszystkie zczytane dane -k jest od 0 do długości zmiennej: kolumna_danych
        str_data = data[data['id'] == kolumna_danych[k]]    #czytamy wiersz w którym 'id' równe jest wartości kalumna danych[k]
        table_name = str(kolumna_danych[k]) #zminna przechowująca nazwę tabeli
        table_name = replace_str(table_name)
        #print(table_name)
        # c.execute('CREATE TABLE IF NOT EXISTS table_name("24h_volume_usd" REAL, available_supply REAL, id TEXT, last_updated REAL, market_cap_usd REAL, max_supply REAL, name TEXT, percent_change_1h REAL, percent_change_24h REAL, percent_change_7d REAL, price_btc REAL, price_usd REAL, rank INTEGER, symbol TEXT, total_supply REAL)')
        #str_data.drop(axis=0)
        if table_name.startswith('0'):
            table_name = 'O'+ table_name
            str_data.to_sql(table_name, conn, if_exists='append', index=False, dtype=db_data_types)
        else:
            str_data.to_sql(table_name, conn, if_exists='append', index=False, dtype=db_data_types)

        #if os.stat(nazwa_pliku).st_size == 0:   #sprawdzmy czy plik jest pusty -jeśli tak to zapisujemy nazwy indeksów, jeśli nie tylko dane
        #    datafile.write(str_data.to_string() + '\n')
        #else:
        #    datafile.write(str_data.to_string().split('\n')[1] + '\n')
        #print('Data write down to file ', nazwa_pliku)  #pomocnicze drukowanie -do usunięcia
        datafile.write('*')



    conn.close()
    datafile.write('\n' + str(timestamp2time(time.time())) + ' : Dane zapisono. Czekam '+ str(sleep_time) +' sekund\n')
    datafile.close()  # zamykamy strumień pliku
    #time.sleep(sleep_time)  #czekamy sleep_time sekund


if __name__ == '__main__': main()


