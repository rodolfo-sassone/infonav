'''
crea un json contenente un dizionario con tutti i nodi e relativa lat e lng
es. {"id_nodo":{"lat":lat_nodo, "lng":lng_nodo}, "id_nodo":{"lat":lat_nodo, "lng":lng_nodo}, ...} utilizzato per accesso diretto nel metodo start_end_coord()
'''

import xml.etree.ElementTree as ET
import json

tree = ET.parse("InfoNav/src/data/Bari.osm")
root = tree.getroot()

nodes = {}

for node in root.findall('node'):
    nodes[node.attrib['id']] = {'lat': node.attrib['lat'], 'lng': node.attrib['lon']}

with open("nodes.json","w") as file:
    json.dump(nodes,file)