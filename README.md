# Guide

How to setup this project to work.

## Setup

1. Install required SW
	* [Neo4j](https://neo4j.com/download-v2/)
	* Python libraries
		* neo4j - `pip install neo4j`
		* matplotlib - `pip install matplotlib`
		* numpy - `pip install numpy`
		* urllib (built-in)
		* sqlite3 (built-in)
		* json (built-in)
		* datetime (built-in)

2. Create new database and start it in Neo4j Desktop app
	* Database name can be any.
	* Database password needs to be "admin" (or different password needs to be set in the `import_tool.py` script).
	* If something goes wrong, delete the Neo4j database in Neo4j Desktop console with: `MATCH (p) DETACH DELETE p` 

3. Run the python script `import_tool.py` to import or update the database. It will either import all new data if Neo4j database is empty or it will only import new days from dataset.
	* This script will import the data from Czech COVID-19 Open Dataset ([online datasource](https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19)).
	* It misses names of districts so the names and codes are in separate file - `districts_names_codes.json`.
	* Neighbors - the relations between districts are in another file - `districts_neighbors_relations.json`.
	* In the end the script will query all dates and add relations between all dates for the same districts.

4. Neo4j database is ready, you can test it with some of query examples below.

5. Run `nosql_to_relation.py` to convert all the necessary data from Neo4j database to SQLite database `relation.db`. For another launch of `nosql_to_relation.py` to update `relation.db`, delete the file (or drop tables) of the SQLite database.

6. Run `query_a.py` or `query_c.py` to generate plots. Edit these queries to adjust displayed data.

## Neo4j Query Examples

* graph of districts in one day (9th Sep 2020) - `MATCH (a:District) WHERE a.date='2020-09-09' RETURN a`
* graph of districts in two days (9th - 10th Sep 2020) - `MATCH (a:District), (b:District) WHERE a.date='2020-09-10' AND b.date='2020-09-09' RETURN a,b`
* graph of all nodes for Brno-město district - `MATCH (a:District) WHERE a.name='Brno-město' RETURN a`
* graph of range of days (1st - 30th Sep 2020) for Znojmo district - `MATCH (a:District) WHERE a.name='Znojmo' AND a.date >= '2020-09-01' AND a.date <= '2020-09-30' RETURN a`
* table of dates and numbers of infected people until this date in district 'Brno-venkov' for all dates - `MATCH (a:District) WHERE a.name='Brno-venkov' RETURN a.date, a.cumInfec`
* all neighbors of Příbram district - `MATCH (a:District)-[r:IS_NEIGHBOUR]-(b:District) WHERE a.name="Příbram" AND a.date="2020-09-09"  RETURN b`
