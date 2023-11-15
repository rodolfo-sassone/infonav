'''
crea un json contenente un dizionario 
es. {"nome strada": [lista di tutti i nodi della strada], "nome della strada": [lista di tutti i nodi della strada], ...}
'''

import json
import googlemaps
import xml.etree.ElementTree as ET

API_key = '#YourAPI-Key'
gmaps = googlemaps.Client(key = API_key)

tree = ET.parse("InfoNav/src/data/Bari.osm")
root = tree.getroot()

ways = {}

for way in root.findall('way'):
    nodes_ID = []
    for tag in way.findall('tag'):
        if tag.attrib['k'] == 'name':
            name =  tag.attrib['v']
            print(name)
        break

    for nd in way.findall('nd'):
        nodes_ID.append(nd.attrib['ref'])


    if name not in ways:
        ways[name] = nodes_ID
    else:
        ways[name].append(nodes_ID)

with open("ways_dict.json","w") as file:
    json.dump(ways,file)
