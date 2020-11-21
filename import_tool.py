import json
import datetime
from neo4j import GraphDatabase

PASS_TO_DATABASE = 'admin'

with open('districts_names_codes.json', encoding="utf8") as json_file:
    Districts = json.load(json_file)

with open('districts_negborows_relations.json', encoding="utf8") as json_file:
    DistrictsRelations = json.load(json_file)

with open('data.json', encoding="utf8") as json_file:
    CoronaData = json.load(json_file)
    # print(CoronaData)

uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", PASS_TO_DATABASE))


def generate_districts(tx, iname, icode, idate, iincInf, iincDead, iincCured):
    tx.run("CREATE (:District {name: $name, code: $code, date: $date, incInf: $incInf, incDead: $incDead, incCured: "
           "$incCured})",
           name=iname, code=icode, date=idate, incInf=iincInf, incDead=iincDead, incCured=iincCured)


def generate_relations_between_districts(tx, dist_1_code, dist_2_code):
    tx.run(
        "MATCH (a:District), (b:District) "
        "WHERE a.code = $dist1 AND b.code = $dist2 AND a.date = b.date "
        "CREATE (a)-[:IS_NEIGHBOUR]->(b)",
        dist1=dist_1_code, dist2=dist_2_code)


def generate_relations_between_dates_in_district(tx, dist_1_code, date1, date2):
    tx.run(
        "MATCH (a:District), (b:District) "
        "WHERE a.code = $dist AND a.date = $date_1 AND b.code = $dist AND b.date = $date_2 "
        "CREATE (a)-[:NEXT_DAY]->(b)",
        dist=dist_1_code, date_1=date1, date_2=date2)


with driver.session() as session:
    for data in CoronaData["data"]:
        code = data['okres_lau_kod']
        name = "prdel"
        for district in Districts:
            if district['code'] == code:
                name = district['name']
        date = data['datum']
        incInf = data['kumulativni_pocet_nakazenych']
        incDead = data['kumulativni_pocet_vylecenych']
        incCured = data['kumulativni_pocet_vylecenych']
        session.write_transaction(generate_districts, name, code, date, incInf, incDead, incCured)

    for relation in DistrictsRelations:
        dist1 = relation['dist1']
        dist2 = relation['dist2']
        session.write_transaction(generate_relations_between_districts, dist1, dist2)


def get_all_dates(tx):
    result = tx.run("MATCH (n:District) RETURN DISTINCT n.date")
    dates = []
    for ix, record in enumerate(result):
        dates.append(record.values())
    return dates


with driver.session() as session:
    all_dates = session.read_transaction(get_all_dates)
    all_dates = sorted(all_dates, key=lambda x: datetime.datetime.strptime(x[0], '%Y-%m-%d'))
    for district in Districts:
        previous_date = -1
        for date in all_dates:
            if previous_date != -1:
                session.write_transaction(generate_relations_between_dates_in_district, district['code'], previous_date[0], date[0])
            previous_date = date

driver.close()
