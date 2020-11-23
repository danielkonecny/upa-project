import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import numpy as np

database = r"relation.db"


def create_connection(db_file=':memory:'):
    connect_conn = None
    try:
        connect_conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return connect_conn


def select_abs(conn, from_date='0000-00-00', to_date='9999-99-99'):
    cur = conn.cursor()
    cur.execute(f"SELECT idate, SUM(infecAbs) FROM infec WHERE idate BETWEEN '{from_date}' AND '{to_date}' GROUP BY idate")
    return cur.fetchall()


def select_per(conn, from_date='0000-00-00', to_date='9999-99-99'):
    cur = conn.cursor()
    cur.execute(f"SELECT idate, SUM(infecPer) FROM infec WHERE idate BETWEEN '{from_date}' AND '{to_date}' GROUP BY idate")
    return cur.fetchall()


def select_ma(conn, iperiod=7, from_date='0000-00-00', to_date='9999-99-99'):
    cur = conn.cursor()
    cur.execute(f"SELECT idate, SUM(incInfecAvg) FROM infecIncMA WHERE idate BETWEEN '{from_date}' AND '{to_date}' AND iperiod = {iperiod} GROUP BY idate")
    return cur.fetchall()


conn = create_connection(database)

with conn:
    from_date = '2020-10-01'
    to_date = '3020-03-29'
    iperiod = 7

    abs = select_abs(conn, from_date, to_date)
    print(abs)
    abs = np.swapaxes(np.array(abs), 0, 1)
    dates_abs = abs[0]
    infec_abs = list(map(int, abs[1]))

    per = select_per(conn, from_date, to_date)
    print(per)
    per = np.swapaxes(np.array(per), 0, 1)
    dates_per = per[0]
    infec_per = list(map(float, per[1]))

    avg = select_ma(conn, iperiod, from_date, to_date)
    avg = np.swapaxes(np.array(avg), 0, 1)
    dates_avg = avg[0]
    infec_avg = list(map(float, avg[1]))

    plt.bar(dates_abs, infec_abs, color="grey", width=0.5)
    plt.plot(dates_avg, infec_avg, color="purple")
    if len(dates_abs) > 15:
        step = int(len(dates_abs) / 15)
    else:
        step = 1
    plt.xticks(dates_abs[::step], rotation=90)
    plt.xlabel('Dates')
    plt.show()


