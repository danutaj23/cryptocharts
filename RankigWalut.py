import sqlite3
import configparser

class ranking_cc:

    CurrencyList = []

    def __init__(self, currencylist) -> object:
       config = configparser.ConfigParser()
       self.db_file = "cryptocurrency.db"
       self.CurrencyList = currencylist
       # ##       if config.read('config/config.conf'):
          ## DEV
##           self.server_type = config['DEFAULT']['servertype']
##       elif config.read('/var/www/FlaskApp/FlaskApp/config/config.conf'):
           ## PROD
##           self.server_type = config['DEFAULT']['servertype']
##       else:
##          pass  ##TODO dorobić obsługę błędu
##       self.db_file = config[server_type]['db_source']


    def initTable(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("drop table if exists ranking")
        c.execute("CREATE TABLE ranking (id	TEXT, symbol TEXT, rank INTEGER, last_updated INTEGER);")
        conn.commit()
        c.close()
        conn.close()

        def createCurrencyList(self):
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            self.CurrencyList = c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' and name<>'ranking' ORDER BY name")
            conn.commit()
            c.close()
            conn.close()

    def createRankingTable(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        self.CurrencyList = c.execute("SELECT name FROM sqlite_master WHERE type='table' and name<>'ranking' ORDER BY name")
        for nn in self.CurrencyList:
            d = conn.cursor()
            table_name = ''.join(nn)
            sql_command = 'INSERT INTO ranking (id, symbol, rank, last_updated) SELECT DISTINCT id, symbol, rank, max(last_updated) as l_upd FROM ' + table_name + ' GROUP BY symbol'
        ##    print(nn)
        ##    print(table_name)
            print(sql_command)
         ##   d.execute(sql_command)
            conn.commit()
            d.close()
        c.close()
        conn.close()


def main():
    rank = ranking_cc([])
    rank.initTable()
    rank.createRankingTable()

if __name__ == '__main__':
    main()

