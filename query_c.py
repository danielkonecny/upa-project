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


def select_outbreaks(s_conn, s_from_date='0000-00-00', s_to_date='9999-99-99', s_district=None):
    cur = s_conn.cursor()
    print(s_district)
    if s_district is None:
        cur.execute(f"""SELECT date, distName FROM dailyOutbreaks
        WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' ORDER BY date""")
    else:
        cur.execute(f"""SELECT date, distName FROM dailyOutbreaks
        WHERE date BETWEEN '{s_from_date}' AND '{s_to_date}' AND distName IN {tuple(s_district)} ORDER BY date""")
    return cur.fetchall()


def get_data_for_graph(from_date='2020-01-01', to_date='2050-01-01', districts=None):
    global dates_out, towns_out
    outbreaks = select_outbreaks(conn, from_date, to_date, districts)
    outbreaks = np.swapaxes(np.array(outbreaks), 0, 1)
    dates_out = outbreaks[0]
    towns_out = outbreaks[1]


def plot_outbreaks(from_date='2020-01-01', to_date='2050-01-01', districts=None):
    get_data_for_graph(from_date=from_date, to_date=to_date, districts=districts)

    global dates_out, towns_out
    town_font_size = 10
    if districts is None or len(districts) > 12:
        town_font_size = 6
    if districts is None or len(districts) > 60:
        town_font_size = 3

    fig, ax = plt.subplots()
    plt.grid(True, axis='y', color="lightgray", linewidth=0.5, zorder=0)
    plt.scatter(dates_out, towns_out, 1, "red", zorder=3)
    heading_size = 10

    step = 1
    if len(set(dates_out)) > 20:
        step = (len(set(dates_out)) // 20)

    ax.set_xlabel("Dates", fontsize=heading_size)
    ax.set_ylabel("Town", fontsize=heading_size)

    ax.set_xticks(range(0, len(list(set(dates_out))))[::step])
    plt.setp(ax.get_yticklabels(), fontsize=town_font_size)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", fontsize=6)

    fig.tight_layout()
    if districts is None:
        plt.title("Outbreaks in all districts of Czechia through time", fontsize=heading_size)
    else:
        plt.title("Outbreaks in specific districts of Czechia through time", fontsize=heading_size)

    ax.legend(["outbreak"], loc='best', fontsize=town_font_size+2)

    plt.savefig(f"images/Outbreaks_{districts}_{from_date}_{to_date}.png", bbox_inches='tight', dpi=600)
    plt.show()


conn = create_connection(database)
with conn:
    global dates_out, towns_out

    plot_outbreaks(from_date='2020-09-10', to_date='2021-08-30',
                   districts=["Brno-město", "Znojmo", "Břeclav", "Hodonín", "Brno-venkov",
                              "Vysočina", "Ústí nad Orlicí", "Litomyšl", "Liberec", "Pardubice"])

    plot_outbreaks(from_date='2019-04-01', to_date='2021-08-30')
