import requests
from pprint import pprint
from datetime import datetime
import sqlite3


class ScheduleTransport():
    def __init__(self):
        tim = datetime.now()
        self.hour = tim.hour
        self.minute = tim.minute
        self.server = 'https://api.rasp.yandex.net/v3.0/search/?'
        self.params = {
            'apikey': '69878fa3-e234-46ad-99bd-31518986ee00',
            'from': '',
            'to': '',
            'transport_types': '',
            'date': f'{tim.year}-{tim.month}-{tim.day}'
        }

    def get_schedule_busAB(self, A, B):
        con = sqlite3.connect('db/codes_yandex_db.db')
        cur = con.cursor()
        A_code = cur.execute(f"""SELECT code FROM bus_towns_codes WHERE name = '{A}'""").fetchone()
        if A_code is None:
            A_code = cur.execute(f"""SELECT code FROM bus_stations_codes WHERE name = '{A}'""").fetchone()
        B_code = cur.execute(f"""SELECT code FROM bus_towns_codes WHERE name = '{B}'""").fetchone()
        if B_code is None:
            B_code = cur.execute(f"""SELECT code FROM bus_stations_codes WHERE name = '{B}'""").fetchone()
        con.commit()
        con.close()
        if A_code and B_code:
            self.params["from"] = A_code[0]
            self.params["to"] = B_code[0]
            self.params["transport_types"] = 'bus'
            response = requests.get(self.server, params=self.params).json()
            sp = []
            if len(response["segments"]) == 0:
                return False, 'Я не знаю такого маршрута'
            missed = True
            for elem in response["segments"]:
                departure = elem["departure"][:-3]
                arrival = elem["arrival"][:-3]
                nearest = ''
                departure_hour = departure[11:13]
                departure_minute = departure[14:16]
                arrival_hour = arrival[11:13]
                arrival_minute = arrival[14:16]
                if int(departure_hour) + 3 == self.hour and \
                        int(departure_minute) > int(self.minute) and missed is True:
                    missed = False
                    nearest = ' - ближайший'
                elif int(departure_hour) + 3 > int(self.hour) and missed is True:
                    missed = False
                    nearest = ' - ближайший'

                if int(departure_hour) + 3 < 24:
                    if int(arrival_hour) + 3 >= 24:
                        arrival_hour = 24 - int(arrival_hour) - 3
                        print(arrival_hour)
                    else:
                        arrival_hour = int(arrival_hour) + 3
                    sp.append(f'{int(departure_hour) + 3}:{departure_minute}'
                                f' - {arrival_hour}:{arrival_minute}{nearest}')
            return True, sp

        else:
            if A_code is None:
                return False, f'мне неизвестен город/станция {A}'
            elif B_code is None:
                return False, f'мне неизвестен город/станция {B}'

    def get_schedule_trainAB(self, A, B):
        con = sqlite3.connect('db/codes_yandex_db.db')
        cur = con.cursor()
        A_code = cur.execute(f"""SELECT code FROM train_towns_codes WHERE name = '{A}'""").fetchone()
        if A_code is None:
            A_code = cur.execute(f"""SELECT code FROM train_stations_codes WHERE name = '{A}'""").fetchone()
        B_code = cur.execute(f"""SELECT code FROM train_towns_codes WHERE name = '{B}'""").fetchone()
        if B_code is None:
            B_code = cur.execute(f"""SELECT code FROM train_stations_codes WHERE name = '{B}'""").fetchone()
        con.commit()
        con.close()
        if A_code and B_code:
            print('here')
            self.params["from"] = A_code[0]
            self.params["to"] = B_code[0]
            self.params["transport_types"] = 'suburban'
            response = requests.get(self.server, params=self.params).json()
            sp = []
            if len(response["segments"]) == 0:
                return False, 'Я не знаю такого маршрута'
            missed = True
            for elem in response["segments"]:
                departure = elem["departure"][:-3]
                arrival = elem["arrival"][:-3]
                nearest = ''
                departure_hour = departure[11:13]
                departure_minute = departure[14:16]
                arrival_hour = arrival[11:13]
                arrival_minute = arrival[14:16]
                if int(departure_hour) + 3 == self.hour and\
                        int(departure_minute) > int(self.minute) and missed is True:
                    missed = False
                    nearest = ' - ближайший'
                elif int(departure_hour) + 3 > int(self.hour) and missed is True:
                    missed = False
                    nearest = ' - ближайший'

                if int(departure_hour) + 3 < 24:
                    if int(arrival_hour) + 3 >= 24:
                        arrival_hour = 24 - int(arrival_hour) - 3
                    else:
                        arrival_hour = int(arrival_hour) + 3
                    sp.append(f'{int(departure_hour) + 3}:{departure_minute}'
                              f' - {arrival_hour}:{arrival_minute}{nearest}')
            return True, sp

        else:
            if A_code is None:
                return False, f'мне неизвестен город/станция {A}'
            elif B_code is None:
                return False, f'мне неизвестен город/станция {B}'






    def all_stations_kras(self):
        params = {
            'apikey': '69878fa3-e234-46ad-99bd-31518986ee00',

        }
