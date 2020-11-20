import json



with open('data.txt') as json_file:
    CoronaData = json.load(json_file)
print(CoronaData)
for i in range(23):
    print(i)