# Guide

Guide for Neo4j database with COVID-19 data.

## Setup

1. Install required SW
	* [Neo4j](https://neo4j.com/download-v2/)
	* Python libraries
		* neo4j - `pip install neo4j`
		* matplotlib
		* numpy
		* urllib (built-in)
		* sqlite3 (built-in)
		* json (built-in)
		* datetime (built-in)

2.
	* Create new database
		* it can be done in Neo4j Desktop app
		* the password for database needs to be "admin" (or different password needs to be edited in the `import_tool.py` script)
	* Clear existing database
		* with this command in Neo4j Desktop console: `MATCH (p) DETACH DELETE p` 

3. Run the python script 'import_tool.py' to import or update the database
	* This script will import the data from Czech COVID-19 Open Dataset (online datasource).
	* It misses names of districts so the names and codes are in separate file - `districts_names_codes.json`.
	* Neighbors - the relations between districts are in another file - `districts_neighbors_relations.json`.
	* In the end the script will query all dates and add relations between all dates for the same districts.

4. Database is ready, you can test it with some of query examples below.

## Query examples

* graph of districts in one day (9th Sep 2020) - `MATCH (a:District) WHERE a.date='2020-09-09' RETURN a`
* graph of districts in two days (9th - 10th Sep 2020) - `MATCH (a:District), (b:District) WHERE a.date='2020-09-10' AND b.date='2020-09-09' RETURN a,b`
* graph of all dates for Brno-město district - `MATCH (a:District) WHERE a.name='Brno-město' RETURN a`
* graph of range of days (1st - 30th Sep 2020) for Znojmo district - `MATCH (a:District) WHERE a.name='Znojmo' AND a.date >= '2020-09-01' AND a.date <= '2020-09-30' RETURN a`
* table of date and number of infected people until this date in district 'Brno-venkov' for all dates - `MATCH (a:District) WHERE a.name='Brno-venkov' RETURN a.date, a.cumInfec`
* all neighbors of Příbram district - `MATCH (a:District)-[r:IS_NEIGHBOUR]-(b:District) WHERE a.name="Příbram" AND a.date="2020-09-09"  RETURN b`
