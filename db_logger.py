from datetime import datetime, timedelta
import psycopg2


class Logger:
    def __init__(self):
        self._conn = psycopg2.connect("dbname=simulator user=postgres password=root host=localhost")
        self._cur = self._conn.cursor()

    def __del__(self):
        self._cur.close()
        self._conn.close()

    def __insert_train_data(self, info: dict, time: datetime):
        arrival_date = time
        departure_date = time + timedelta(hours=info['cargo_time'])
        self._cur.execute("""INSERT INTO train (train_name, station_name, arrival_date, departure_date) 
                          VALUES (%s, %s, %s, %s);""",
                          (info['train_name'], info['station_name'], arrival_date, departure_date))
        self._conn.commit()

    def __insert_entrepot_data(self, info: dict, time: datetime):
        self._cur.execute("""INSERT INTO polarnii (date, entrepot_oil, 
                          track1_train_name, track1_oil_collected, track1_train_oil, 
                          track2_train_name, track2_oil_collected, track2_train_oil, 
                          track3_train_name, track3_oil_collected, track3_train_oil) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                          (time, info['oil_amt'],
                           info['tracks'][0]['train_name'], info['tracks'][0]['oil_collected'], info['tracks'][0]['storage'],
                           info['tracks'][1]['train_name'], info['tracks'][1]['oil_collected'], info['tracks'][1]['storage'],
                           info['tracks'][2]['train_name'], info['tracks'][2]['oil_collected'], info['tracks'][2]['storage']))
        self._conn.commit()

    def __insert_radugnii_data(self, info: dict, time: datetime):
        self._cur.execute("""INSERT INTO radugnii (date, terminal_oil, oil_mined, train_name, oil_collected, train_oil) 
                          VALUES (%s, %s, %s, %s, %s, %s);""",
                          (time, info['oil_amt'], info['oil_mined'],
                           info['train_name'], info['oil_collected'], info['train_storage']))
        self._conn.commit()

    def __insert_zvezda_data(self, info: dict, time: datetime):
        self._cur.execute("""INSERT INTO zvezda (date, terminal_oil, oil_mined, train_name, oil_collected, train_oil) 
                          VALUES (%s, %s, %s, %s, %s, %s);""",
                          (time, info['oil_amt'], info['oil_mined'],
                           info['train_name'], info['oil_collected'], info['train_storage']))
        self._conn.commit()

    def insert_data(self, station_data: list[dict], train_data: list[dict], time: datetime):
        for info in station_data:
            if list(info.keys())[0] != 'Полярный':
                if list(info.keys())[0] == 'Радужный':
                    self.__insert_radugnii_data(info['Радужный'], time)
                else:
                    self.__insert_zvezda_data(info['Звезда'], time)
            else:
                self.__insert_entrepot_data(info['Полярный'], time)

        for info in train_data:
            self.__insert_train_data(info, time)
