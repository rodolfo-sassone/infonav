'''
Created on 18 set 2023

@author: Rodolfo Pio Sassone
'''
import csv
import spacy

with open('InfoNav/src/stradariocittadibari.csv', mode='r') as csv_file:
    nlp = spacy.load("it_core_news_sm")
    csv_reader = csv.DictReader(csv_file, delimiter=";")
    first = True
    data = []
    
    for riga in csv_reader:
        if first:
            #saltiamo la prima riga, quella di intestazione
            first = False
            continue
        doc = nlp.make_doc(riga["TOPONIMO"])
        
        luogo = {'label':'LUOGO', 'pattern': [{'LOWER': riga['DUG'].lower()}]}
        for token in doc:
            t = {'LOWER':token.text.lower()}
            luogo['pattern'].append(t)
        
        luogo['id'] = riga['DUG'] + " " + riga['TOPONIMO']
        
        data.append(luogo)
        
    #secondo giro per prendere solo i cognomi come abbreviazioni delle vie
    file = open('InfoNav/src/stradariocittadibari.csv', mode='r')
    reader = csv.DictReader(file, delimiter=";")
    for riga in reader:
        if first:
            #saltiamo la prima riga, quella di intestazione
            first = False
            continue
        doc_entity = nlp(riga["TOPONIMO"])
        
        for ent in doc_entity.ents:
            if ent.label_ == 'PER':
                luogo = {'label':'LUOGO', 'pattern': [{'LOWER': riga['DUG'].lower()}]}
                t = {'LOWER':ent[-1].text.lower()}
                luogo['pattern'].append(t)

                if 'id' not in luogo:
                    luogo['id'] = riga['DUG'] + " " + riga['TOPONIMO']

            data.append(luogo)
        
    ruler = nlp.add_pipe("entity_ruler")
    patterns = data
    ruler.add_patterns(patterns)
    ruler.to_disk("InfoNav/src/data/patterns_withID.jsonl")
  
'''        
with open('stradariocittadibari.csv', mode='r') as csv_file:
    nlp = Italian()
    csv_reader = csv.DictReader(csv_file, delimiter=";")
    first = True
    data = set()
    
    for riga in csv_reader:
        if first:
            #saltiamo la prima riga, quella di intestazione
            first = False
            continue
        doc = nlp.make_doc(riga["LOCALITA'"])
        
        localita = {'label':'LOCALITA', 'pattern': []}
        for token in doc:
            t = {'LOWER':token.text.lower()}
            localita['pattern'].append(t)
        
        data.append(localita)
        
    ruler = nlp.add_pipe("entity_ruler")
    patterns = data
    ruler.add_patterns(patterns)
    ruler.to_disk("./patterns_localita.jsonl")
 '''        
