import sqlite3
from sqlite3 import Error
from neo4j import GraphDatabase

database = r"relation.db"
uri = "neo4j://localhost:7687"
PASS_TO_DATABASE = 'admin'


def create_connection(db_file=':memory:'):
    connect_conn = None
    try:
        connect_conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return connect_conn


def create_table(create_conn, create_table_sql):
    try:
        c = create_conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_database(database_conn):
    infec_inc_table = '''CREATE TABLE IF NOT EXISTS infec (
    id integer PRIMARY KEY,
    distCode text NOT NULL,
    distName text NOT NULL,
    idate date NOT NULL,
    infecAbs integer NOT NULL,
    infecPer float);'''

    infec_ma_table = '''CREATE TABLE IF NOT EXISTS infecIncMA (
    id integer PRIMARY KEY,
    distCode text NOT NULL,
    distName text NOT NULL,
    idate date NOT NULL,
    iperiod integer NOT NULL,
    incInfecAvg float NOT NULL);'''

    create_table(database_conn, infec_inc_table)
    create_table(database_conn, infec_ma_table)


def insert_infec_inc(insert_conn, insert_infec_data):
    sql = 'INSERT INTO infec(distCode, distName, idate, infecAbs, infecPer) VALUES(?, ?, ?, ?, ?)'
    cur = conn.cursor()
    cur.execute(sql, insert_infec_data)
    insert_conn.commit()
    return cur.lastrowid


def insert_infec_ma(insert_conn, insert_infec_data):
    sql = 'INSERT INTO infecIncMA(distCode, distName, idate, iperiod, incInfecAvg) VALUES(?, ?, ?, ?, ?)'
    cur = conn.cursor()
    cur.execute(sql, insert_infec_data)
    insert_conn.commit()
    return cur.lastrowid


def get_dates_of_dist(tx):
    result = tx.run(f"""MATCH (a:District) RETURN DISTINCT a.date AS dates""")
    dates = []
    for ix, record in enumerate(result):
        dates.append(record.values())
    return dates


def get_infec(tx, date):
    nodes = tx.run("""MATCH (a:District {date: $date})<-[:NEXT_DAY]-(b:District) WHERE (b.incInfec > 0)
    RETURN ((toFloat(a.incInfec) / b.incInfec)-1) AS infecPer, (a.incInfec - b.incInfec) AS infecAbs,
    a.code AS code, a.name AS name""", date=date)
    return [record for record in nodes.data()]


def get_dist_infec(tx, date, period):
    nodes = tx.run(f"""MATCH (a:District {{date: $date}})<-[:NEXT_DAY*{period}]-(b:District) 
    RETURN (a.incInfec - b.incInfec)/{period}.0 AS incInfecAvg, a.code AS code, a.name AS name""", date=date)
    return [record for record in nodes.data()]


conn = create_connection(database)

with conn:
    create_database(conn)

    driver = GraphDatabase.driver(uri, auth=("neo4j", PASS_TO_DATABASE))

    with driver.session() as session:
        periods = [3, 7, 14, 28]
        dates = session.read_transaction(get_dates_of_dist)
        for date_arr in dates:
            date = date_arr[0]

            districts = session.read_transaction(get_infec, date)
            for district in districts:
                name = district['name']
                code = district['code']
                infec_abs = district['infecAbs']
                infec_per = district['infecPer']
                inc_infec = (code, name, date, infec_abs, infec_per)
                insert_infec_inc(conn, inc_infec)

            for period in periods:
                district_incs = session.read_transaction(get_dist_infec, date, period)
                for district_inc in district_incs:
                    name = district_inc['name']
                    code = district_inc['code']
                    inc_infec_avg = district_inc['incInfecAvg']
                    dist_infec_data = (code, name, date, period, inc_infec_avg)
                    insert_infec_ma(conn, dist_infec_data)
