'''
Created on 19 set 2023

@author: Rodolfo Pio Sassone
'''
import json
import xml.etree.ElementTree as ET
import requests
from flask import Flask, render_template
from myParser import Parser
from scraping import scraperBT
from way import way, overall
from page_template import template
import threading

app = Flask(__name__)

#pipeline su bari today
#effettua scraping, parsing e gecoding. restituisce una lista con le coordinate e il numero di incidenti in ogni via riconosciuta
def pipelineBT(link, min_pages = 10, inter = False):
    scraper = scraperBT(link)
    old_len = 0

    list_pages = scraper.get_pages(list_pages = [])
    while len(list_pages) < min_pages and old_len < len(list_pages):
        new_link = scraper.prefisso + list_pages[-1]
        old_len = len(list_pages)
        list_pages = scraper.get_pages(link = new_link, list_pages = list_pages)
    
    list_articles = scraper.get_articles(list_pages)
    docs = Parser().parse_where(list_articles)
    
    #LOCALITA NON AGGIUNTA ALLA PIPELINE di spacy quindi niente localita' tra le ent
    list_addresses = []
    for doc in docs:
        addresses = []
        year = '2023'
        for ent in doc.ents:
            if ent.label_.lower() == 'luogo':
                addresses.append(ent.ent_id_.lower())
            elif ent.label_.lower() == 'year':
                year = ent.text
        list_addresses.append({'addresses': addresses, 'year': year}) #lista di indirizzi per ogni articolo trovato e anno
    

    for addresses in list_addresses:
        print(addresses)

    list_addr, intersections = crime_counter(list_addresses)

    int_coord = []
    if inter:
        int_coord = geocoding(intersections)

    way_coord = start_end_coord(list_addr)

    print(int_coord, way_coord)
    return int_coord, way_coord


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


def geocoding(luoghi):
    data = []

    for l in luoghi:
        string = ''
        for address in l['address']:
            string = string + ' ' + address
            string = string.replace(' ','%20')
                
        r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+string+'&components=administrative_area:bari&key=#YourAPI-Key')
        r.raise_for_status()
        
        d = r.json()
        print(d["status"])
        
        if d["status"] == "OK":
            inters = {'lat':d['results'][0]["geometry"]["location"]['lat'], 'lng':d['results'][0]["geometry"]["location"]['lng'], 'count':l['count'], 'year':l['year']}
            data.append(inters)
    
    return(data)

#Data il nome di una via ci restituisce il punto d'inizio e il punto di fine
def start_end_coord(list_addr):
    way_coord = []
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
        else:
            for id1 in nodes_ID:
                for id2 in nodes_ID:        
                    distance = abs(float(nodes[id1]['lat']) - float(nodes[id2]['lat']) + float(nodes[id1]['lng']) - float(nodes[id2]['lng']))

                    if distance > massimo:
                        massimo = distance
                        n1 = {'lat':nodes[id1]['lat'], 'lng':nodes[id1]['lng']}
                        n2 = {'lat':nodes[id2]['lat'], 'lng':nodes[id2]['lng']}
        
            if item['address'].upper() == 'CORSO CAVOUR' or item['address'].upper() ==  'VIA PRINCIPE AMEDEO' or item['address'].upper() ==  'VIA BRIGATA REGINA':
                way = {'start':n2, 'end':n1, 'count':item['count'], 'name': item['address'].upper(), 'year':item['year']}
            else:
                way = {'start':n1, 'end':n2, 'count':item['count'], 'name': item['address'].upper(), 'year':item['year']}
            way_coord.append(way)

    return way_coord


def crime_index(way_fur1 = None, way_fur2 = None, way_drug = None, way_rap = None, way_kill = None, way_agg = None, way_spa = None, way_fire = None):
    crimes = {} #{'anno':{'nome_via': way_object, 'nome_via1': way_object1, ...}, 'anno1':{'nome_via': way_object, 'nome_via1': way_object1, ...}, ...}

    crimes = add_crime(way_fur1, 'fur', crimes)
    crimes = add_crime(way_fur2, 'fur', crimes)
    crimes = add_crime(way_drug, 'drug', crimes)
    crimes = add_crime(way_rap, 'rap', crimes)
    crimes = add_crime(way_kill, 'kill', crimes)
    crimes = add_crime(way_agg, 'agg', crimes)
    crimes = add_crime(way_spa, 'spa', crimes)
    crimes = add_crime(way_fire, 'fire', crimes)

    ways = []
    history = overall()
    for year in crimes:
        if year == '2022':
            for _, wayy in crimes[year].items():
                history.update_crimes(wayy)
    print('******************************HISTORY(2022)******************************************')
    print(history.get_crimes())
    print('******************************2023******************************************')
    print(crimes['2023'])
    for name, wayy in crimes['2023'].items():
        ci = 0
        for k, v in wayy.get_crimes().items():
            if history.get_crime(k) != 0:
                sub_index = v / history.get_crime(k)
            else:
                sub_index = v / 2   #TODO costante sensata o media dei crimini in history
            ci = ci + sub_index

        ways.append({'start':wayy.get_start(), 'end':wayy.get_end(), 'ci':ci, 'fur':wayy.get_crime('fur'), 'drug':wayy.get_crime('drug'), 'rap':wayy.get_crime('rap'), 'kill':wayy.get_crime('kill'), 'agg':wayy.get_crime('agg'), 'spa':wayy.get_crime('spa'), 'fire':wayy.get_crime('fire'),'name':name})

    return ways


def add_crime(ways, crime, crimes):
    if ways != None:
        for w in ways:
            if w['year'] in crimes and  w['name'] in crimes[w['year']]:
                crimes[w['year']][w['name']].set_crime(crime,w['count'])
            else:
                if w['year'] not in crimes:
                    crimes[w['year']] = {}
                crimes[w['year']][w['name']] = way(w['start'], w['end'])
                crimes[w['year']][w['name']].set_crime(crime, w['count'])
    
    return crimes


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


def sum_per_loc(ways = None, ints = None):
    done = []
    summed = []
    if ways != None and ints == None:
        for way in ways:
            name = way['name']
            if name not in done:
                sum = 0
                for w in ways:
                    if w['name'] == name:
                        sum = sum + w['count']

                nw = {'start':way['start'], 'end':way['end'], 'count': sum, 'name': name}
                summed.append(nw)
                done.append(name)
    elif ints != None and ways == None:
        for inter in ints:
            lat_lng = {'lat':inter['lat'], 'lng':inter['lng']}
            if lat_lng not in done:
                sum = 0
                for i in ints:
                    if i['lat'] == lat_lng['lat'] and i['lng'] == lat_lng['lng']:
                        sum = sum + i['count']

                w = {'lat':inter['lat'], 'lng':inter['lng'], 'count':sum}
                summed.append(w)
                done.append(lat_lng)
    else:
        print("error only one parameter between ways and ints")
    
    return summed


acc_template = template()
cri_template = template() 


def render_acc_template(template = acc_template):
    with app.app_context():
        print('Started')
        LINK_INCIDENTI = "/tag/incidenti-stradali/"

        int_inc, way_inc = pipelineBT(LINK_INCIDENTI, min_pages = 50, inter = True)

        #rate_way = rate_acc(ways = way_inc)
        #rate_int = rate_acc(ints = int_inc)
        way_inc = sum_per_loc(ways = way_inc)
        int_inc = sum_per_loc(ints = int_inc)


        template.set_string(render_template("accident.html",  way_inc=way_inc, int_inc=int_inc))
        print('Accident Done')


def render_cri_template(template = cri_template):
    with app.app_context():
        LINK_FURTI1 = "/tag/furti/"
        LINK_FURTI2 = "/tag/furto/"
        LINK_RAPINE = '/tag/rapine/'    
        LINK_INCENDI = '/tag/incendi/'
        LINK_DROGA = '/tag/droga/'
        LINK_ARRESTI = '/tag/arresti/' #TODO da utilizzare, trovato massimo ISTAT
        LINK_OMICIDI = '/tag/omicidi/'
        LINK_AGGRESSIONI = '/tag/aggressioni/'
        LINK_SPARATORIA = '/tag/sparatoria/'
        
        _, way_fur1 = pipelineBT(LINK_FURTI1, min_pages = 35)
        _, way_fur2 = pipelineBT(LINK_FURTI2, min_pages = 35)
        _, way_drug = pipelineBT(LINK_DROGA, min_pages = 35)
        _, way_rap = pipelineBT(LINK_RAPINE, min_pages = 35)
        _, way_kill = pipelineBT(LINK_OMICIDI, min_pages = 35)
        _, way_agg = pipelineBT(LINK_AGGRESSIONI, min_pages = 35)
        _, way_spa = pipelineBT(LINK_SPARATORIA, min_pages = 35)
        _, way_fire = pipelineBT(LINK_INCENDI, min_pages = 35)

        way_ci = crime_index(way_fur1, way_fur2, way_drug, way_rap, way_kill, way_agg, way_spa, way_fire)
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

#acc_thread.start()
cri_thread.start()

timer = threading.Timer(3600, update_templates, kwargs = {'acc_temp': acc_template, 'cri_temp': cri_template}) #AGGIORNA LE PAGINE DOPO UN'ORA
timer.start()


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