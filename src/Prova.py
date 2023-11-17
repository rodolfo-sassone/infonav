'''
dobbiamo provare a calcolare la distanza senza l'api google probabilmente risparmiamo in tempo e denaro
proviamo prima una distanza naive tipo lat1 - lat2 + lng1 - lng2 SEMBRA FUNZIONARE ED È VELOCISSIMOOOO
altrimenti cedi chatGPT
'''
from datetime import datetime

# Ottenere la data corrente
data_corrente = datetime.now()

# Formattare la data come una stringa
data_formattata = data_corrente.strftime("%Y")

# Stampare la data formattata
print("Data corrente formattata:", data_formattata)



'''from spacy.lang.en import English

nlp = English()
ruler = nlp.add_pipe("entity_ruler")
patterns = [{"label": "ORG", "pattern": "Apple", "id": "apple"},
            {"label": "GPE", "pattern": [{"LOWER": "san"}, {"LOWER": "francisco"}], "id": "san-francisco"},
            {"label": "GPE", "pattern": [{"LOWER": "san"}, {"LOWER": "fran"}], "id": "san-francisco"},
            {'label':'YEAR', 'pattern': [{'TEXT': {'REGEX': '20[0-9][0-9]'}}]}]

ruler.add_patterns(patterns)

doc1 = nlp("Apple is opening its first big office in San Francisco in the 2000.")
print([(ent.text, ent.label_, ent.ent_id_) for ent in doc1.ents])

doc2 = nlp("Apple is opening its first big office in San Fran.")
print([(ent.text, ent.label_, ent.ent_id_) for ent in doc2.ents])
'''

'''import json
import xml.etree.ElementTree as ET


tree = ET.parse("InfoNav/src/data/Bari.osm")
root = tree.getroot()

via= 'via napoli'

nodes_ID = []

for way in root.findall('way'):
    for tag in way.findall('tag'):
        if tag.attrib['k'] == 'name' and tag.attrib['v'].lower() == via.lower():
            for nd in way.findall('nd'):
                nodes_ID.append(nd.attrib['ref'])

nodes = json.load(open("ScrapingBot/src/data/nodes.json"))

massimo = 0
n1 = {}
n2 = {}
for id1 in nodes_ID:
    for id2 in nodes_ID:        
        distance = abs(float(nodes[id1]['lat']) - float(nodes[id2]['lat']) + float(nodes[id1]['lng']) - float(nodes[id2]['lng']))

        if distance > massimo:
            massimo = distance
            n1 = {'lat':nodes[id1]['lat'], 'lng':nodes[id1]['lng']}
            n2 = {'lat':nodes[id2]['lat'], 'lng':nodes[id2]['lng']}
            
print(n1,n2)
'''
'''
import json
import googlemaps

API_key = '#YourAPI-Key'
gmaps = googlemaps.Client(key = API_key)


incroci = json.load(open("incroci2.json", encoding="utf8"))

via = "via giulio petroni"

incroci_via = []

for i in incroci:
    if via in i['ways']:
        incroci_via.append(i)

massimo = 0
for i in incroci_via:
    for j in incroci_via:        
        m = gmaps.distance_matrix(origins = {'lat':i['lat'], 'lng':i['lng']}, destinations = {'lat':j['lat'], 'lng':j['lng']})
        
        if m['rows'][0]['elements'][0]['distance']['value'] > massimo:
            massimo = m['rows'][0]['elements'][0]['distance']['value']
            inc1 = {'lat':i['lat'], 'lng':i['lng']}
            inc2 = {'lat':j['lat'], 'lng':j['lng']}
            
print(inc1,inc2)
'''
'''
import googlemaps

API_key = '#YourAPI-Key'
place_key = 'AIzaSyCd3P7ABK-YKlSH9BLrppbkBoXQpGrIpvY'


gmaps = googlemaps.Client(key = API_key)
raggio_ricerca = '50000'

string = "via capruzzi"
#string = string.replace(' ','%20')

l = gmaps.geocode(address = string, components = {"administrative_area":"bari"})

for r in l:
    print(r)
               
r = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address=' + string + '&components=administrative_area:bari&key=' + API_key)
r.raise_for_status()

d = r.json()
print(d["status"])
if d["status"] == 'OK':
    for place in d["results"]:
        print(place)

        lat = place['geometry']['location']['lat']
        lng = place['geometry']['location']['lng']
        
        r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + str(lat) + ',' + str(lng) + '&radius=' + raggio_ricerca + '&key=' + place_key)
        r.raise_for_status()
        
        intersections = r.json()
        
        print(intersections["status"])
        if intersections["status"] == 'OK':
            for i in intersections["results"]:
                if 'neighborhood' in i['types']:
                    print(i)
                    '''
                    
'''
import spacy
import csv

with open('stradariocittadibari.csv', mode='r') as csv_file:
    nlp = spacy.load("it_core_news_sm")
    csv_reader = csv.DictReader(csv_file, delimiter=";")
    first = True
    data = []
    
    for riga in csv_reader:
        if first:
            #saltiamo la prima riga, quella di intestazione
            first = False
            continue
        doc = nlp(riga["TOPONIMO"])

        for ent in doc.ents:
            if ent.label_ == 'PER':
                print(ent.text)
'''          
'''
import spacy
from spacy import displacy

nlp = spacy.load("it_core_news_sm")

ruler = nlp.add_pipe("entity_ruler")
pattern = [{"label":"LOC", "pattern": [{"LOWER": "via"}, {"LOWER": "brigata"}, {"LOWER": "regina"}]}]
ruler.add_patterns(pattern)

doc = nlp("Scontro in via Brigata Regina: auto si ribalta, ferita donna")

for token in doc:
    print("TEXT    POS    TAG   DEP    HEAD")
    print(token.text + "    " +  token.pos_ + "    " +  token.tag_ + "    " +  token.dep_ + "    " +  token.head.text)
    print()

for ent in doc.ents:
    print(ent.text, ent.label_)
    print(spacy.explain(ent.label_))
    
displacy.serve(doc)
'''
'''
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
# Add match ID "HelloWorld" with no callback and one pattern
pattern = [{"LOWER": "hello"}, {"IS_PUNCT": True}, {"LOWER": "world"}, {"IS_PUNCT": True}]
matcher.add("HelloWorld", [pattern])

doc = nlp("Hello, world! Hello world!")
matches = matcher(doc)
for match_id, start, end in matches:
    string_id = nlp.vocab.strings[match_id]  # Get string representation
    span = doc[start:end]  # The matched span
    print(match_id, string_id, start, end, span.text)
'''
'''
import spacy
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab)
terms = ["Barack Obama", "Angela Merkel", "Washington, D.C."]
# Only run nlp.make_doc to speed things up
patterns = [nlp.make_doc(text) for text in terms]
matcher.add("TerminologyList", patterns)

doc = nlp("German Chancellor Angela Merkel and US President Barack Obama "
          "converse in the Oval Office inside the White House in Washington, D.C.")
matches = matcher(doc)
for match_id, start, end in matches:
    span = doc[start:end]
    print(span.text)
    '''
'''    
import spacy
from spacy.tokens import Doc

if not Doc.has_extension("text_id"):
    Doc.set_extension("text_id", default=None)

text_tuples = [
    ("This is the first text.", {"text_id": "text1"}),
    ("This is the second text.", {"text_id": "text2"})
]

nlp = spacy.load("en_core_web_sm")
doc_tuples = nlp.pipe(text_tuples, as_tuples=True)

docs = []
for doc, context in doc_tuples:
    doc._.text_id = context["text_id"]
    docs.append(doc)

for doc in docs:
    print(f"{doc._.text_id}: {doc.text}")
    '''
'''
import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import json

with open("exercises/en/countries.json", encoding="utf8") as f:
    COUNTRIES = json.loads(f.read())
with open("exercises/en/country_text.txt", encoding="utf8") as f:
    TEXT = f.read()

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab)
patterns = list(nlp.pipe(COUNTRIES))
matcher.add("COUNTRY", patterns)

# Create a doc and reset existing entities
doc = nlp(TEXT)
doc.ents = []

# Iterate over the matches
for match_id, start, end in matcher(doc):
    # Create a Span with the label for "GPE"
    span = Span(doc, start, end, label="GPE")

    # Overwrite the doc.ents and add the span
    doc.ents = list(doc.ents) + [span]

    # Get the span's root head token
    span_root_head = span.root.head
    # Print the text of the span root's head token and the span text
    print(span_root_head.text, "-->", span.text)

# Print the entities in the document
print([(ent.text, ent.label_) for ent in doc.ents if ent.label_ == "GPE"])
'''
'''
import json
import spacy
from spacy.language import Language
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher

with open("stradario.json", encoding="utf8") as f:
    STRADARIO = json.loads(f.read())

#with open("stradarioconlocalita.json", encoding="utf8") as f:
    #LOCALITA = json.loads(f.read())

nlp = spacy.blank("it")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher.add("STRADARIO", list(nlp.pipe(STRADARIO)))


@Language.component("stradario_component")
def stradario_component_function(doc):
    # Create an entity Span with the label "GPE" for all matches
    matches = matcher(doc)
    doc.ents = [Span(doc, start, end, label="LUOGO") for match_id, start, end in matches]
    return doc


# Add the component to the pipeline
nlp.add_pipe("stradario_component")
print(nlp.pipe_names)

# Getter that looks up the span text in the dictionary of country capitals
#def get_loalita(span):
   # LOCALITA.get(span.text)

# Register the Span extension attribute "capital" with the getter get_capital
#Span.set_extension("capital", getter=get_capital)

# Process the text and print the entity text, label and capital attributes
doc = nlp("Scontro in via Brigata Regina: auto si ribalta, ferita donna")
print([(ent.text, ent.label_) for ent in doc.ents])
'''
