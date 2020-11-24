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


def select_inc_infec_abs(s_conn, s_from_date='0000-00-00', s_to_date='9999-99-99'):
    cur = s_conn.cursor()
    cur.execute(f"""SELECT date, SUM(incInfecAbs) FROM incInfecAbsPer
    WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' GROUP BY date""")
    return cur.fetchall()


def select_inc_infec_per(s_conn, s_from_date='0000-00-00', s_to_date='9999-99-99'):
    cur = s_conn.cursor()
    cur.execute(f"""SELECT date, AVG(incInfecPer) FROM incInfecAbsPer
    WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' GROUP BY date""")
    return cur.fetchall()


def select_inc_infec_mov_avg(s_conn, s_period=7, s_from_date='0000-00-00', s_to_date='9999-99-99'):
    cur = s_conn.cursor()
    cur.execute(f"""SELECT date, SUM(incInfecMovAvg) FROM incInfecMovAvg
    WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' AND period = {s_period} GROUP BY date""")
    return cur.fetchall()


conn = create_connection(database)

with conn:
    from_date = '1020-06-09'
    to_date = '3020-03-29'
    period = 7

    inc_infec_abs = select_inc_infec_abs(conn, from_date, to_date)
    print(inc_infec_abs)
    inc_infec_abs = np.swapaxes(np.array(inc_infec_abs), 0, 1)
    dates_abs = inc_infec_abs[0]
    data_abs = list(map(int, inc_infec_abs[1]))

    inc_infec_per = select_inc_infec_per(conn, from_date, to_date)
    print(inc_infec_per)
    inc_infec_per = np.swapaxes(np.array(inc_infec_per), 0, 1)
    dates_per = inc_infec_per[0]
    # data_per = list(map(float, inc_infec_per[1]))
    data_per = []
    for item in inc_infec_per[1]:
        if item is not None:
            data_per.append(float(item))
        else:
            data_per.append(0.0)
    print(data_per)

    inc_infec_mov_avg = select_inc_infec_mov_avg(conn, period, from_date, to_date)
    inc_infec_mov_avg = np.swapaxes(np.array(inc_infec_mov_avg), 0, 1)
    dates_mov_avg = inc_infec_mov_avg[0]
    # data_mov_avg = list(map(float, inc_infec_mov_avg[1]))
    data_mov_avg = []
    for item in inc_infec_mov_avg[1]:
        if item is not None:
            data_mov_avg.append(float(item))
        else:
            data_mov_avg.append(0.0)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax2.axhline(y=0, color='pink')

    ax1.bar(dates_abs, data_abs, color="grey", width=0.65)
    ax1.plot(dates_mov_avg, data_mov_avg, color="purple")
    if len(dates_abs) > 15:
        step = int(len(dates_abs) / 15)
    else:
        step = 1

    ax2.set_xticks(range(0, len(dates_abs))[::step])
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    ax2.margins(4)
    ax2.plot(dates_per, data_per, color="red", LineWidth=0.7)

    ax1.set_ylabel("Number of infected")
    ax2.set_ylabel("Percentage increase")
    ax1.set_xlabel("Dates")

    fig.tight_layout()
    plt.show()
