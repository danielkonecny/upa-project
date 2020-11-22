# Guide

Guide for Neo4j database with COVID-19 data.

## Setup

1. Install required SW
	* [Neo4j](https://neo4j.com/download-v2/)
	* Python libraries
		* neo4j - `pip install neo4j`
		* json (built-in)
		* datetime (built-in)

2.
	* Create new database
		* it can be done in Neo4j Desktop app
		* the password for database needs to be "admin" (or different password needs to be edited in the `import_tool.py` script)
	* Clear existing database
		* with this command in Neo4j Desktop console: `MATCH (p) DETACH DELETE p` 

3. Run the python script 'import_tool.py'
	* this script will import the data from coronavirus data in json - `data.json`
	* this json does not include names of districts so the names and codes are in separe file - `districts_names_codes.json`
	* neighbors - the relations between districs are in another file - `districts_neighbors_relations.json`
	* in the end the script will query all dates and add relations between all dates for the same discrtrits

4. Database is ready - if you want to import data again you need to clear the database before with command from step 2.

## Query examples

* graph of districs in one day (9th Sep 2020) - `MATCH (a:District) WHERE a.date='2020-09-09' RETURN a`
* graph of districs in two days (9th - 10th Sep 2020) - `MATCH (a:District), (b:District) WHERE a.date='2020-09-10' AND b.date='2020-09-09' RETURN a,b`
* graph of all dates for Brno-město district - `MATCH (a:District) WHERE a.name='Brno-město' RETURN a`
* graph of range of days (1st - 30th Sep 2020) for Znojmo district - `MATCH (a:District) WHERE a.name='Znojmo' AND a.date >= '2020-09-01' AND a.date <= '2020-09-30' RETURN a`
* table of date and daily increase number of infected people in district 'Brno-venkov' for all dates - `MATCH (a:District) WHERE a.name='Brno-venkov' RETURN a.date, a.incInfec`