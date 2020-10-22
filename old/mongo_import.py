from pymongo import MongoClient
import urllib.request
import json

client = MongoClient('localhost', 27017)

db = client['covid-19']
collection = db['kraj-okres-nakazeni-vyleceni-umrti']

with urllib.request.urlopen('https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/kraj-okres-nakazeni-vyleceni-umrti'
                            '.json') as f:
    data = json.loads(f.read().decode('utf-8'))

x = collection.insert_many(data['data'])

for x in collection.find({}):
    print(x)


