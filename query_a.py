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


def select_inc_infec_abs(s_conn, s_from_date='0000-00-00', s_to_date='9999-99-99', s_district='all'):
    cur = s_conn.cursor()
    if s_district == 'all':
        cur.execute(f"""SELECT date, SUM(incInfecAbs) FROM incInfecAbsPer
        WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' GROUP BY date""")
    else:
        cur.execute(f"""SELECT date, SUM(incInfecAbs) FROM incInfecAbsPer
        WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' AND distName = '{s_district}' 
        GROUP BY date""")
    return cur.fetchall()


def select_inc_infec_per(s_conn, s_from_date='0000-00-00', s_to_date='9999-99-99', s_district='all'):
    cur = s_conn.cursor()
    if s_district == 'all':
        cur.execute(f"""SELECT date, AVG(incInfecPer) FROM incInfecAbsPer
        WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' GROUP BY date""")
    else:
        cur.execute(f"""SELECT date, AVG(incInfecPer) FROM incInfecAbsPer
        WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' AND distName = '{s_district}'  
        GROUP BY date""")
    return cur.fetchall()


def select_inc_infec_mov_avg(s_conn, s_period=7, s_from_date='0000-00-00', s_to_date='9999-99-99', s_district='all'):
    cur = s_conn.cursor()
    if s_district == 'all':
        cur.execute(f"""SELECT date, SUM(incInfecMovAvg) FROM incInfecMovAvg
        WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' AND period = {s_period} GROUP BY date""")
    else:
        cur.execute(f"""SELECT date, SUM(incInfecMovAvg) FROM incInfecMovAvg 
        WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' AND period = {s_period} AND distName = '{s_district}' 
        GROUP BY date""")
    return cur.fetchall()


def plot_increase_percentage(from_date, to_date, period, district='all'):
    calculate_data_for_graph(from_date=from_date, to_date=to_date, period=period, district=district)

    global dates_abs, data_abs, dates_per, data_per, dates_mov_avg, data_mov_avg
    assert period == 3 or period == 7 or period == 14 or period == 28

    plt.rcParams.update({'font.size': 6})

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    # change of infected
    change_line = ax1.bar(dates_abs, data_abs, color="grey", width=0.65)
    # moving average
    average_line, = ax1.plot(dates_mov_avg, data_mov_avg, color="#A346A3", linewidth=0.6)

    # zero line for change of infected
    ax1.axhline(y=0, color='black', linewidth=0.3)

    step = 1
    if len(dates_abs) > 13:
        step = int(len(dates_abs) / 13)

    ax2.set_xticks(range(0, len(dates_abs))[::step])
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # zero line for percentage
    ax2.axhline(y=0, color='#FFA5C5', linewidth=0.3)

    # percentage change
    percentage_line, = ax2.plot(dates_per, data_per, color="red", linewidth=0.5)
    ax2.set_ymargin(0.25)

    ax1.set_ylabel("Change in the number of infected ")
    ax2.set_ylabel("Percentage change of infected")
    ax1.set_xlabel("Date")
    ax1.legend([change_line, average_line],
               [f"{period}-day step moving average", 'change of infected'], loc='upper left')
    ax2.legend([percentage_line], ['percentage infected change'], loc='upper right')

    fig.tight_layout()
    if district == 'all':
        plt.title("Increase/decrease of infected in Czechia")
    else:
        plt.title(f"Increase/decrease of infected in {district}")

    plt.savefig(f"images/Changes_{district}_{from_date}_{to_date}_{period}.svg", bbox_inches='tight')
    plt.show()


def get_formatted_float_data(unformatted_data, data_type):
    unformatted_data = np.swapaxes(np.array(unformatted_data), 0, 1)
    dates = unformatted_data[0]
    data = list(map(data_type, unformatted_data[1]))
    return data, dates


def calculate_data_for_graph(from_date, to_date, period, district='all'):
    global dates_abs, data_abs, dates_per, data_per, dates_mov_avg, data_mov_avg
    assert period == 3 or period == 7 or period == 14 or period == 28

    inc_infec_abs = select_inc_infec_abs(conn, from_date, to_date, district)
    data_abs, dates_abs = get_formatted_float_data(inc_infec_abs, data_type=int)

    inc_infec_per = select_inc_infec_per(conn, from_date, to_date, district)
    data_per, dates_per = get_formatted_float_data(inc_infec_per, data_type=float)

    inc_infec_mov_avg = select_inc_infec_mov_avg(conn, period, from_date, to_date, district)
    data_mov_avg, dates_mov_avg = get_formatted_float_data(inc_infec_mov_avg, data_type=float)


conn = create_connection(database)
with conn:
    global dates_abs, data_abs, dates_per, data_per, dates_mov_avg, data_mov_avg
    # periods = [3, 7, 14, 28]

    plot_increase_percentage(from_date='2019-03-01', to_date='2021-04-11', period=14)

    plot_increase_percentage(from_date='2020-04-01', to_date='2020-08-30', period=7, district="Brno-město")

    plot_increase_percentage(from_date='2020-04-01', to_date='2020-08-30', period=7, district="Znojmo")

    plot_increase_percentage(from_date='2020-04-01', to_date='2020-08-30', period=7, district="Brno-venkov")
