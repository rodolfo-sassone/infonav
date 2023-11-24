'''
Created on 19 set 2023

@author: Rodolfo Pio Sassone
'''
import json
import xml.etree.ElementTree as ET
import requests
from flask import Flask, render_template
from scraping import scraperBL, scraperBT
from way import way, way
from page_template import template
from datetime import datetime
import threading
import numpy as np

app = Flask(__name__)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))



def scraping(topic, min_pages = 10):
    BTscraper = scraperBT(topic)
    BLscraper = scraperBL(topic)

    list_addressesBT = BTscraper.scrape(min_pages)

    list_addressesBL = BLscraper.scrape(min_pages)
    
    for item in list_addressesBL:
        if item not in list_addressesBT:
            list_addressesBT.append(item)

    for addresses in list_addressesBT:
        print(addresses)

    return list_addressesBT


def crime_counter(list_addresses):
    intersections = []
    list_addr = []

    for item in list_addresses:
        if len(item['addresses']) > 1:
            c = list_addresses.count(item)
            inters = {'address':item['addresses'], 'count':c, 'year':item['year']}
            if inters not in intersections:
                intersections.append(inters)
        else:
            c = list_addresses.count(item)
            addr = {'address':item['addresses'][0], 'count':c, 'year':item['year']}
            if addr not in list_addr:
                list_addr.append(addr)

    return list_addr, intersections


def geocoding(location):
    data = []

    for l in location:
        string = ''
        for address in l['address']:
            string = string + ' ' + address
            string = string.replace(' ','%20')
                
        r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+string+'&components=administrative_area:bari&key=#YourAPI-Key')
        r.raise_for_status()
        
        d = r.json()
        print(d["status"])
        
        if d["status"] == "OK":
            inters = {'lat':d['results'][0]["geometry"]["location"]['lat'], 'lng':d['results'][0]["geometry"]["location"]['lng'], 'count':l['count'], 'address':l['address']}
            data.append(inters)
    
    return(data)

#Data il nome di una via ci restituisce il punto d'inizio e il punto di fine
def start_end_coord(list_addr):
    no_coord = []
    tree = ET.parse("InfoNav/src/data/Bari.osm")
    root = tree.getroot()

    for item in list_addr:
        nodes_ID = []

        for way in root.findall('way'):
            for tag in way.findall('tag'):
                if tag.attrib['k'] == 'name' and tag.attrib['v'].lower() == item['address'].lower():
                    for nd in way.findall('nd'):
                        nodes_ID.append(nd.attrib['ref'])

        nodes = json.load(open("InfoNav/src/data/nodes.json"))

        massimo = 0
        n1 = {}
        n2 = {}

        if len(nodes_ID) == 0:
            print(item['address'] + " non trovata")
            no_coord.append(item)
        else:
            for id1 in nodes_ID:
                for id2 in nodes_ID:        
                    distance = abs(float(nodes[id1]['lat']) - float(nodes[id2]['lat']) + float(nodes[id1]['lng']) - float(nodes[id2]['lng']))

                    if distance > massimo:
                        massimo = distance
                        n1 = {'lat':nodes[id1]['lat'], 'lng':nodes[id1]['lng']}
                        n2 = {'lat':nodes[id2]['lat'], 'lng':nodes[id2]['lng']}
        
            if item['address'].upper() == 'CORSO CAVOUR' or item['address'].upper() ==  'VIA PRINCIPE AMEDEO' or item['address'].upper() ==  'VIA BRIGATA REGINA':
                item['start'] = n2
                item['end'] = n1
            else:
                item['start'] = n1
                item['end'] = n2
                
    for item in no_coord:
        list_addr.remove(item)

    return list_addr


def crime_index(way_fur = None, way_drug = None, way_rap = None, way_kill = None, way_agg = None, way_spa = None, way_fire = None):
    crimes = {} #{'anno':{'nome_via': way_object, 'nome_via1': way_object1, ...}, 'anno1':{'nome_via': way_object, 'nome_via1': way_object1, ...}, ...}

    crimes = add_crime(way_fur, 'fur', crimes)
    crimes = add_crime(way_drug, 'drug', crimes)
    crimes = add_crime(way_rap, 'rap', crimes)
    crimes = add_crime(way_kill, 'kill', crimes)
    crimes = add_crime(way_agg, 'agg', crimes)
    crimes = add_crime(way_spa, 'spa', crimes)
    crimes = add_crime(way_fire, 'fire', crimes)

    ways = []
    last_year = way()
    all = way()
    current = datetime.now()
    past_y = str(current.year - 1)
    year_in_all = 0
    for year in crimes:
            year_in_all = year_in_all + 1
            for _, wayy in crimes[year].items():
                if year == past_y:
                    last_year.update_crimes(wayy)
                all.update_crimes(wayy)

    print('****************************** 2022 ******************************************')
    print(last_year.get_crimes())
    print('****************************** 2023 ******************************************')
    cy = current.strftime('%Y')
    print(crimes[cy])
    for name, wayy in crimes[cy].items():
        ci = 0
        for k, v in wayy.get_crimes().items():
            if last_year.get_crime(k) != 0:
                sub_index = v / last_year.get_crime(k)
            else:
                sub_index = v / (all.get_crime(k)/ year_in_all) #se nell'anno passato non abbiamo dati su un crimine utilizziamo la media della città come 'massimo'
            ci = ci + sub_index

        ways.append({'ci':sigmoid(ci), 'address':name, 'fur':wayy.get_crime('fur'), 'drug':wayy.get_crime('drug'), 'rap':wayy.get_crime('rap'), 'kill':wayy.get_crime('kill'), 'agg':wayy.get_crime('agg'), 'spa':wayy.get_crime('spa'), 'fire':wayy.get_crime('fire')})

    return ways


def add_crime(ways, crime, crimes):
    if ways != None:
        for wayy in ways:
            if wayy['year'] in crimes and  wayy['address'] in crimes[wayy['year']]:
                crimes[wayy['year']][wayy['address']].set_crime(crime,wayy['count'])
            else:
                if wayy['year'] not in crimes:
                    crimes[wayy['year']] = {}
                crimes[wayy['year']][wayy['address']] = way()
                crimes[wayy['year']][wayy['address']].set_crime(crime, wayy['count'])
    
    return crimes

#TODO da cambiare per togliere lat e lng
def rate_acc(ways = None, ints = None):
    rate = []
    done = []
    if ways != None and ints == None:
        print('************************************RATE ACC***************************************************')
        for way in ways:
            name = way['name']
            print(name)
            print(done)
            if name not in done:
                print('not done')
                sum_num = 0
                sum_den = 24198 + 2023    #somma dei numeri nell'intervallo [2011, 2022]
                for w in ways:
                    if w['name'] == name:
                        sum_num = sum_num + (int(w['count']) * int(w['year']))
                        #sum_den = sum_den + int(w['year'])

                avg = sum_num/sum_den

                nw = {'start':way['start'], 'end':way['end'], 'count': avg, 'name': name}
                rate.append(nw)
                print('done' + name)
                done.append(name)
    elif ints != None and ways == None:
        for inter in ints:
            lat_lng = {'lat':inter['lat'], 'lng':inter['lng']}
            if lat_lng not in done:
                sum_num = 0
                sum_den = 24198 + 2023    #somma dei numeri nell'intervallo [2011, 2022]
                for i in ints:
                    if i['lat'] == lat_lng['lat'] and i['lng'] == lat_lng['lng']:
                        sum_num = sum_num + (int(i['count']) * int(i['year']))
                        #sum_den = sum_den + int(i['year'])

                avg = sum_num/sum_den

                w = {'lat':inter['lat'], 'lng':inter['lng'], 'count':avg}
                rate.append(w)
                done.append(lat_lng)
    else:   
        print("error only one parameter between ways and ints")

    return rate

#somma per tutti gli anni in una via, utilizzata per gli incidenti
def sum_per_loc(location):
    done = []
    summed = []
    for loc in location:
        address = loc['address']
        if address not in done:
            sum = 0
            for w in location:
                if w['address'] == address:
                    sum = sum + w['count']

            nl = {'count': sum, 'address': address}
            summed.append(nl)
            done.append(address)
    
    return summed


acc_template = template()
cri_template = template() 


def render_acc_template(template = acc_template):
    with app.app_context():
        print('Started')

        list_addresses = scraping('inc', min_pages = 35)

        list_addr, intersections = crime_counter(list_addresses)

        acc_per_way = sum_per_loc(list_addr)
        acc_per_int = sum_per_loc(intersections)

        way_inc = start_end_coord(acc_per_way)
        int_inc = geocoding(acc_per_int)

        template.set_string(render_template("accident.html",  way_inc=way_inc, int_inc=int_inc))
        print('Accident Done')


def render_cri_template(template = cri_template):
    with app.app_context():
        addr_fur = scraping('fur', min_pages = 35)
        addr_drug = scraping('drug', min_pages = 35)
        addr_rap = scraping('rap', min_pages = 35)
        addr_kill = scraping('kill', min_pages = 35)
        addr_agg = scraping('agg', min_pages = 35)
        addr_spa = scraping('spa', min_pages = 35)
        addr_fire = scraping('fire', min_pages = 35)

        way_fur, _ = crime_counter(addr_fur)
        way_drug, _ = crime_counter(addr_drug)
        way_rap, _ = crime_counter(addr_rap)
        way_kill, _ = crime_counter(addr_kill)
        way_agg, _ = crime_counter(addr_agg)
        way_spa, _ = crime_counter(addr_spa)
        way_fire, _ = crime_counter(addr_fire)

        addr_ci = crime_index(way_fur, way_drug, way_rap, way_kill, way_agg, way_spa, way_fire)

        way_ci = start_end_coord(addr_ci)

        template.set_string(render_template("crime_index.html",  way_ci=way_ci))


def update_templates(acc_temp = acc_template, cri_temp = cri_template):
    acc_thread = threading.Thread(target = render_acc_template, kwargs = {'template': acc_temp})
    cri_thread = threading.Thread(target = render_cri_template, kwargs = {'template': cri_temp})

    acc_thread.start()
    cri_thread.start()

    timer = threading.Timer(3600, update_templates, kwargs = {'acc_temp': acc_template, 'cri_temp': cri_template})
    timer.start()

acc_thread = threading.Thread(target = render_acc_template, kwargs = {'template': acc_template})
cri_thread = threading.Thread(target = render_cri_template, kwargs = {'template': cri_template})

acc_thread.start()
cri_thread.start()

'''timer = threading.Timer(3600, update_templates, kwargs = {'acc_temp': acc_template, 'cri_temp': cri_template}) #AGGIORNA LE PAGINE DOPO UN'ORA
timer.start()'''


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/accident')
def accident(template = acc_template):
    acc_thread.join()

    return template.get_string()


@app.route('/crime')
def crime(template = cri_template):
    cri_thread.join()

    return template.get_string()


if __name__ == '__main__':
    app.run(debug=True)