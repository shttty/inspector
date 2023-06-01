import json

with open("server_list/server_list.json",'r') as f:
    nodeList=json.load(f)

print(nodeList)
