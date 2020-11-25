import json
import datetime
import urllib.request
from neo4j import GraphDatabase

uri = "neo4j://localhost:7687"
PASS_TO_DATABASE = 'admin'


def generate_districts(tx, i_name, i_code, i_date, i_cum_infec, i_cum_dead, i_cum_cured):
    tx.run("CREATE (:District {name: $name, code: $code, date: $date, "
           "cumInfec: $cumInfec, cumDead: $cumDead, cumCured: $cumCured})",
           name=i_name, code=i_code, date=i_date, cumInfec=i_cum_infec, cumDead=i_cum_dead, cumCured=i_cum_cured)


def generate_relations_between_districts(tx, dist_1_code, dist_2_code):
    tx.run(
        "MATCH (a:District), (b:District) "
        "WHERE a.code = $dist1 AND b.code = $dist2 AND a.date = b.date "
        "CREATE (a)-[:IS_NEIGHBOR]->(b)",
        dist1=dist_1_code, dist2=dist_2_code)


def generate_relations_between_districts2(tx, dist_1_code, dist_2_code, update_date):
    tx.run(
        "MATCH (a:District), (b:District) "
        "WHERE a.code = $dist1 AND b.code = $dist2 AND a.date = b.date AND a.date >= $date_from "
        "CREATE (a)-[:IS_NEIGHBOR]->(b)",
        dist1=dist_1_code, dist2=dist_2_code, date_from=update_date)


def generate_relations_between_dates_in_district(tx, dist_1_code, date1, date2):
    tx.run(
        "MATCH (a:District), (b:District) "
        "WHERE a.code = $dist AND a.date = $date_1 AND b.code = $dist AND b.date = $date_2 "
        "CREATE (a)-[:NEXT_DAY]->(b)",
        dist=dist_1_code, date_1=date1, date_2=date2)


def get_all_dates(tx):
    result = tx.run("MATCH (n:District) RETURN DISTINCT n.date")
    g_dates = []
    for ix, record in enumerate(result):
        g_dates.append(record.values())
    return g_dates


def get_dates_after(tx, g_date):
    result = tx.run("MATCH (n:District) WHERE n.date >= $date RETURN DISTINCT n.date", date=g_date)
    g_dates = []
    for ix, record in enumerate(result):
        g_dates.append(record.values())
    return g_dates


def get_last_date(tx):
    result = tx.run("MATCH (n:District) RETURN max(n.date)")
    i_dates = []
    for ix, record in enumerate(result):
        i_dates.append(record.values())
    return i_dates[0][0]


def generate_next_day_relations(g_dates, districts_file):
    g_dates = sorted(g_dates, key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d'))
    for district in districts_file:
        # noinspection PyRedeclaration
        previous_date = -1
        for g_date in g_dates:
            if previous_date != -1:
                session.write_transaction(generate_relations_between_dates_in_district, district['code'],
                                          previous_date[0], g_date[0])
            previous_date = g_date


def import_data(i_covid_data):
    for data in i_covid_data:
        code = data['okres_lau_kod']
        name = None
        for district in Districts:
            if district['code'] == code:
                name = district['name']
        date = data['datum']
        cum_infec = data['kumulativni_pocet_nakazenych']
        cum_dead = data['kumulativni_pocet_umrti']
        cum_cured = data['kumulativni_pocet_vylecenych']
        session.write_transaction(generate_districts, name, code, date, cum_infec, cum_dead, cum_cured)

    for relation in DistrictsRelations:
        dist1 = relation['dist1']
        dist2 = relation['dist2']
        session.write_transaction(generate_relations_between_districts, dist1, dist2)


def update_data(u_covid_data):
    latest_date = "9999-99-99"
    for data in u_covid_data:
        code = data['okres_lau_kod']
        name = None
        for district in Districts:
            if district['code'] == code:
                name = district['name']
        date = data['datum']
        if date < latest_date:
            latest_date = date
        cum_infec = data['kumulativni_pocet_nakazenych']
        cum_dead = data['kumulativni_pocet_umrti']
        cum_cured = data['kumulativni_pocet_vylecenych']
        session.write_transaction(generate_districts, name, code, date, cum_infec, cum_dead, cum_cured)

    for relation in DistrictsRelations:
        dist1 = relation['dist1']
        dist2 = relation['dist2']
        session.write_transaction(generate_relations_between_districts2, dist1, dist2, latest_date)


with open('districts_names_codes.json', encoding="utf8") as json_file:
    Districts = json.load(json_file)

with open('districts_neighbors_relations.json', encoding="utf8") as json_file:
    DistrictsRelations = json.load(json_file)

with urllib.request.urlopen(
        'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/kraj-okres-nakazeni-vyleceni-umrti.json') as f:
    covid_file = json.loads(f.read().decode('utf-8'))

driver = GraphDatabase.driver(uri, auth=("neo4j", PASS_TO_DATABASE))

with driver.session() as session:
    latest_date_in_db = session.read_transaction(get_last_date)
    print(f"Last date: {latest_date_in_db}")
    if latest_date_in_db is None:
        covid_data = covid_file['data']
        print("Importing data...")
        import_data(covid_data)
        dates = session.read_transaction(get_all_dates)
    else:
        print("Filtering data...")
        covid_data = list(filter(lambda i: i['datum'] > latest_date_in_db, covid_file['data']))
        print("Updating data...")
        update_data(covid_data)
        dates = session.read_transaction(get_dates_after, latest_date_in_db)
    generate_next_day_relations(dates, Districts)

driver.close()
