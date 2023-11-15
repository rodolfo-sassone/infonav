'''
crea un file json conetnente una lista di dizioanri
es. [{ "name":"nome strada", "nodes": [lista di tutti i nodi della strada]}, ...]
'''

import json
import googlemaps
import xml.etree.ElementTree as ET

API_key = '#YourAPI-Key'
gmaps = googlemaps.Client(key = API_key)

tree = ET.parse("InfoNav/src/data/Bari.osm")
root = tree.getroot()

ways = []
names = []

for way in root.findall('way'):
    nodes_ID = []
    for tag in way.findall('tag'):
        if tag.attrib['k'] == 'name':
            name =  tag.attrib['v']
            print(name)
        break

    for nd in way.findall('nd'):
        nodes_ID.append(nd.attrib['ref'])

    if name not in names:
        way['name'] = name
        way['nodes'] = nodes_ID
        ways.append(way)
        names.append(name)
    else:
        for way in ways:
            if way['name'] == name:
                way['nodes'].append(nodes_ID)

with open("ways.json","w") as file:
    json.dump(ways,file)

