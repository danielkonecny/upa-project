import json
from neo4j import GraphDatabase

with open('CiselnikOkresu.json', encoding="utf8") as json_file:
    Districts = json.load(json_file)

with open('OkresyAVztahy.json', encoding="utf8") as json_file:
    DistrictsRelations = json.load(json_file)

with open('data.json', encoding="utf8") as json_file:
    CoronaData = json.load(json_file)
    # print(CoronaData)

uri = "neo4j://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "admin"))


def generate_districts(tx, iname, icode, idate, iincInf, iincDead, iincCured):
    tx.run("CREATE (:District {name: $name, code: $code, date: $date, incInf: $incInf, incDead: $incDead, incCured: "
           "$incCured})",
           name=iname, code=icode, date=idate, incInf=iincInf, incDead=iincDead, incCured=iincCured)


def generate_relations(tx, dist_1_code, dist_2_code):
    tx.run(
        "MATCH (a:District), (b:District) "
        "WHERE a.code = $dist1 AND b.code = $dist2 AND a.date = b.date "
        "CREATE (a)-[:IS_NEIGHBOUR]->(b)",
        dist1=dist_1_code, dist2=dist_2_code)


with driver.session() as session:
    for data in CoronaData["data"]:
        code = data['okres_lau_kod']
        name = "prdel"
        for district in Districts:
            if district['code'] == code:
                name = district['name']
                # print(name)
        date = data['datum']
        incInf = data['kumulativni_pocet_nakazenych']
        incDead = data['kumulativni_pocet_vylecenych']
        incCured = data['kumulativni_pocet_vylecenych']
        session.write_transaction(generate_districts, name, code, date, incInf, incDead, incCured)

    for relation in DistrictsRelations:
        dist1 = relation['dist1']
        dist2 = relation['dist2']
        session.write_transaction(generate_relations, dist1, dist2)


def create_friend_of(tx, name, friend):
    tx.run("CREATE (a:Person)-[:KNOWS]->(f:Person {name: $friend}) "
           "WHERE a.name = $name "
           "RETURN f.name AS friend", name=name, friend=friend)


# with driver.session() as session:
#     session.write_transaction(create_friend_of, "Alice", "Bob")

# with driver.session() as session:
#     session.write_transaction(create_friend_of, "Alice", "Carl")

driver.close()
