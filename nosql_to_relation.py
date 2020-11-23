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
    dist_infec_table = '''CREATE TABLE IF NOT EXISTS distInfec (
    id integer PRIMARY KEY,
    distCode text NOT NULL,
    distName text NOT NULL,
    idate date NOT NULL,
    iperiod integer NOT NULL,
    incInfecAvg float NOT NULL,
    incInfecAvgPer float NOT NULL);'''

    create_table(database_conn, dist_infec_table)


def insert_dist_infec(insert_conn, insert_dist_infec_data):
    sql = '''INSERT INTO distInfec(distCode, distName, idate, iperiod, incInfecAvg, incInfecAvgPer)
    VALUES(?, ?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, insert_dist_infec_data)
    insert_conn.commit()
    return cur.lastrowid


def get_dist_infec(tx, dist_name, date, period):
    nodes = tx.run(f"""MATCH (:District {{name: $name, date: $date}})<-[:NEXT_DAY*0..{period-1}]-(a:District) 
                   RETURN AVG(a.incInfec) AS incInfecAvg, a.code AS code""", name=dist_name, date=date)
    return [record for record in nodes.data()][0]


conn = create_connection(database)

with conn:
    create_database(conn)

    driver = GraphDatabase.driver(uri, auth=("neo4j", PASS_TO_DATABASE))

    with driver.session() as session:
        name = 'Znojmo'
        date = '2020-09-09'
        period = 7
        dist_infec = session.read_transaction(get_dist_infec, name, date, period)

        code = dist_infec['code']
        inc_infec_avg = dist_infec['incInfecAvg']
        inc_infec_avg_per = 0.0

        print(f"{inc_infec_avg} - {type(inc_infec_avg)}")

        dist_infec_data = (code, name, date, period, inc_infec_avg, inc_infec_avg_per)
        dist_infec_data_id = insert_dist_infec(conn, dist_infec_data)
