from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['test-database']
collection = db['test-collection']

print(client.list_database_names())
