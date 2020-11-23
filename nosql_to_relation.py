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
    date text NOT NULL,
    infec integer NOT NULL,
    incInfecPer float NOT NULL);'''

    create_table(database_conn, dist_infec_table)


def insert_dist_infec(insert_conn, insert_dist_infec_data):
    sql = 'INSERT INTO distInfec(distCode, distName, date, infec, incInfec) VALUES(?, ?, ?, ?, ?)'
    cur = conn.cursor()
    cur.execute(sql, insert_dist_infec_data)
    insert_conn.commit()
    return cur.lastrowid


def get_dist_infec(tx, dist_name, date):
    nodes = tx.run("MATCH (a:District) WHERE a.name=$name AND a.date=$date RETURN a AS distInfec",
                   name=dist_name, date=date)
    return [record for record in nodes.data()][0]['distInfec']


conn = create_connection(database)

with conn:
    create_database(conn)

    driver = GraphDatabase.driver(uri, auth=("neo4j", PASS_TO_DATABASE))
    with driver.session() as session:
        dist_infec_dat = session.read_transaction(get_dist_infec, 'Znojmo', '2020-09-09')

        code = dist_infec_dat.get('code')
        name = dist_infec_dat.get('name')
        date = dist_infec_dat.get('date')
        inc_infec = dist_infec_dat.get('incInfec')

        print(f"{code} - {type(code)}")
        print(f"{name} - {type(name)}")
        print(f"{date} - {type(date)}")
        print(f"{inc_infec} - {type(inc_infec)}")

        dist_infec_data = (code, name, date, inc_infec, inc_infec)
        dist_infec_data_id = insert_dist_infec(conn, dist_infec_data)
