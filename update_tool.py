import json
import datetime
from neo4j import GraphDatabase

uri = "neo4j://localhost:7687"
PASS_TO_DATABASE = 'admin'


def generate_districts(tx, i_name, i_code, i_date, i_cum_infec, i_cum_dead, i_cum_cured):
    tx.run("CREATE (:District {name: $name, code: $code, date: $date, "
           "cumInfec: $cumInfec, cumDead: $cumDead, cumCured: $cumCured})",
           name=i_name, code=i_code, date=i_date, cumInfec=i_cum_infec, cumDead=i_cum_dead, cumCured=i_cum_cured)


def generate_relations_between_districts(tx, dist_1_code, dist_2_code, update_date):
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


def get_dates_after(tx, i_date):
    result = tx.run("MATCH (n:District) WHERE n.date >= $date RETURN DISTINCT n.date", date=i_date)
    i_dates = []
    for ix, record in enumerate(result):
        i_dates.append(record.values())
    return i_dates


def get_last_date(tx):
    result = tx.run("MATCH (n:District) RETURN max(n.date)")
    i_dates = []
    for ix, record in enumerate(result):
        i_dates.append(record.values())
    return i_dates[0][0]


with open('districts_names_codes.json', encoding="utf8") as json_file:
    Districts = json.load(json_file)

with open('districts_neighbors_relations.json', encoding="utf8") as json_file:
    DistrictsRelations = json.load(json_file)

with open('update.json', encoding="utf8") as json_file:
    CoronaData = json.load(json_file)

driver = GraphDatabase.driver(uri, auth=("neo4j", PASS_TO_DATABASE))

latestDateInDb = None
with driver.session() as session:
    # noinspection PyRedeclaration
    latestDateInDb = session.read_transaction(get_last_date)

earliestDate = "2222-10-06"
with driver.session() as session:
    for data in CoronaData['data']:
        code = data['okres_lau_kod']
        name = 'null'
        for district in Districts:
            if district['code'] == code:
                name = district['name']
        date = data['datum']
        if date < earliestDate:
            earliestDate = date
        incInf = data['kumulativni_pocet_nakazenych']
        incDead = data['kumulativni_pocet_umrti']
        incCured = data['kumulativni_pocet_vylecenych']
        session.write_transaction(generate_districts, name, code, date, incInf, incDead, incCured)

    for relation in DistrictsRelations:
        dist1 = relation['dist1']
        dist2 = relation['dist2']
        session.write_transaction(generate_relations_between_districts, dist1, dist2, earliestDate)

with driver.session() as session:
    dates = session.read_transaction(get_dates_after, latestDateInDb)
    dates = sorted(dates, key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d'))
    for district in Districts:
        # noinspection PyRedeclaration
        previous_date = -1
        for date in dates:
            if previous_date != -1:
                session.write_transaction(generate_relations_between_dates_in_district, district['code'],
                                          previous_date[0], date[0])
            previous_date = date

driver.close()
