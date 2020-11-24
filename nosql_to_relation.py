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
    inc_infec_abs_per_table = '''CREATE TABLE IF NOT EXISTS incInfecAbsPer (
    id integer PRIMARY KEY,
    distCode text NOT NULL,
    distName text NOT NULL,
    date date NOT NULL,
    incInfecAbs integer NOT NULL,
    incInfecPer float);'''

    inc_infec_mov_avg_table = '''CREATE TABLE IF NOT EXISTS incInfecMovAvg (
    id integer PRIMARY KEY,
    distCode text NOT NULL,
    distName text NOT NULL,
    date date NOT NULL,
    period integer NOT NULL,
    incInfecMovAvg float NOT NULL);'''

    daily_outbreaks_table = '''CREATE TABLE IF NOT EXISTS dailyOutbreaks (
    id integer PRIMARY KEY,
    distCode text NOT NULL,
    distName text NOT NULL,
    date date NOT NULL,
    outbreakInc integer NOT NULL,
    diffToSecond float NOT NULL);'''

    create_table(database_conn, inc_infec_abs_per_table)
    create_table(database_conn, inc_infec_mov_avg_table)
    create_table(database_conn, daily_outbreaks_table)


def insert_inc_infec_abs_per(insert_conn, inc_infec_abs_per_data):
    sql = 'INSERT INTO incInfecAbsPer(distCode, distName, date, incInfecAbs, incInfecPer) VALUES(?, ?, ?, ?, ?)'
    cur = conn.cursor()
    cur.execute(sql, inc_infec_abs_per_data)
    insert_conn.commit()
    return cur.lastrowid


def insert_inc_infec_mov_avg(insert_conn, inc_infec_mov_avg_data):
    sql = 'INSERT INTO incInfecMovAvg(distCode, distName, date, period, incInfecMovAvg) VALUES(?, ?, ?, ?, ?)'
    cur = conn.cursor()
    cur.execute(sql, inc_infec_mov_avg_data)
    insert_conn.commit()
    return cur.lastrowid

def insert_daily_outbreak(insert_conn, outbreak_data):
    sql = 'INSERT INTO dailyOutbreaks(distCode, distName, date, outbreakInc, diffToSecond) VALUES(?, ?, ?, ?, ?)'
    cur = conn.cursor()
    cur.execute(sql, outbreak_data)
    insert_conn.commit()
    return cur.lastrowid

def match_dates_of_dist(tx):
    result = tx.run(f"""MATCH (a:District) RETURN DISTINCT a.date AS dates""")
    m_dates = []
    for ix, record in enumerate(result):
        m_dates.append(record.values())
    return m_dates

def match_names_of_dist(tx):
    result = tx.run(f"""MATCH (a:District) RETURN DISTINCT a.name AS dates""")
    m_dates = []
    for ix, record in enumerate(result):
        m_dates.append(record.values())
    return m_dates


def match_inc_infec_abs_per(tx, m_date):
    nodes = tx.run("""MATCH (a:District {date: $date})<-[:NEXT_DAY]-(b:District) WHERE (b.cumInfec > 0) RETURN
    (toFloat(a.cumInfec) - toFloat(a.cumCured) - toFloat(a.cumDead) - 
    toFloat(b.cumInfec) + toFloat(b.cumCured) + toFloat(b.cumDead)) AS incInfecAbs,
    ((toFloat(a.cumInfec) - toFloat(a.cumCured) - toFloat(a.cumDead) - 
    toFloat(b.cumInfec) + toFloat(b.cumCured) + toFloat(b.cumDead)) / 
    (toFloat(b.cumInfec) - toFloat(b.cumCured) - toFloat(b.cumDead))) AS incInfecPer,
    a.code AS code,
    a.name AS name""", date=m_date)
    return [record for record in nodes.data()]


def match_inc_infec_mov_avg(tx, m_date, m_period):
    nodes = tx.run(f"""MATCH (a:District {{date: $date}})<-[:NEXT_DAY*{m_period}]-(b:District) RETURN
    ((toFloat(a.cumInfec) - toFloat(a.cumCured) - toFloat(a.cumDead) - 
    toFloat(b.cumInfec) + toFloat(b.cumCured) + toFloat(b.cumDead)) / {m_period}.0) AS incInfecMovAvg,
    a.code AS code,
    a.name AS name""", date=m_date)
    return [record for record in nodes.data()]


def match_daily_outbreaks(tx, m_date, m_name):
    nodes = tx.run(f"""MATCH (a:District {{date: $date, name: $name}})<-[:NEXT_DAY]-(b:District) 
MATCH (a)-[:IS_NEIGHBOR]-(c) 
MATCH (c:District)<-[:NEXT_DAY]-(d:District)
WITH max((c.cumInfec - c.cumCured - c.cumDead)-(d.cumInfec - d.cumCured - d.cumDead)) as maxNeigh,
(a.cumInfec - a.cumCured - a.cumDead)-(b.cumInfec - b.cumCured - b.cumDead) as maxLocal, a as a
MATCH (e:District)
WHERE ((maxLocal > maxNeigh) AND a.code = e.code AND a.date = e.date)
RETURN e as OutbreakNode, maxLocal as OutbreakInc,
((toFloat(maxLocal)/toFloat(maxNeigh)) - 1) as DiffToSecond""", date=m_date, name=m_name)
    return [record for record in nodes.data()]


conn = create_connection(database)

with conn:
    create_database(conn)

    driver = GraphDatabase.driver(uri, auth=("neo4j", PASS_TO_DATABASE))

    with driver.session() as session:
        periods = [3, 7, 14, 28]
        dates = session.read_transaction(match_dates_of_dist)
        for date_arr in dates:
            date = date_arr[0]

            #outbreaks
            names = session.read_transaction(match_names_of_dist)
            for name_arr in names:
                name = name_arr[0]
                outbreak = session.read_transaction(match_daily_outbreaks, date, name)
                if outbreak:
                    outbreak_data = (outbreak[0]['OutbreakNode']['code'], outbreak[0]['OutbreakNode']['name'],
                                     outbreak[0]['OutbreakNode']['date'], outbreak[0]['OutbreakInc'],
                                     outbreak[0]['DiffToSecond'])
                    insert_daily_outbreak(conn, outbreak_data)
            #outbreaks end

            # districts = session.read_transaction(match_inc_infec_abs_per, date)
            # for district in districts:
            #     name = district['name']
            #     code = district['code']
            #     inc_infec_abs = district['incInfecAbs']
            #     inc_infec_per = district['incInfecPer']
            #     inc_infec = (code, name, date, inc_infec_abs, inc_infec_per)
            #     insert_inc_infec_abs_per(conn, inc_infec)
            #
            # for period in periods:
            #     district_incs = session.read_transaction(match_inc_infec_mov_avg, date, period)
            #     for district_inc in district_incs:
            #         name = district_inc['name']
            #         code = district_inc['code']
            #         inc_infec_mov_avg = district_inc['incInfecMovAvg']
            #         dist_inc_infec = (code, name, date, period, inc_infec_mov_avg)
            #         insert_inc_infec_mov_avg(conn, dist_inc_infec)

