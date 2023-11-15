'''
Created on 13 ott 2023

@author: Rodolfo Pio Sassone
'''

import xml.etree.ElementTree as ET
import json

tree = ET.parse("Bari.osm")
root = tree.getroot()


incroci = []

for node in root.findall('node'):
    incrocio = {}
    incrocio['id'] = node.attrib['id']
    incrocio['lat'] = node.attrib['lat']
    incrocio['lng'] = node.attrib['lon']
    incrocio['ways'] = []
    
    for way in root.findall('way'):
        t = False 
        for nd in way.findall('nd'):
            if nd.attrib['ref'] == incrocio['id']:
                t = True 
                break
        if t:
            for tag in way.findall('tag'):
                if tag.attrib['k'] == 'name':
                    incrocio['ways'].append(tag.attrib['v'].lower())
                    break
            
    incroci.append(incrocio)
    
for i in incroci:
    if len(i['ways']) <= 1:
        incroci.remove(i)

with open("incroci2.json","w") as file:
    json.dump(incroci,file)