'''
Created on 19 set 2023

@author: Rodolfo Pio Sassone
'''
from spacy.tokens import Doc
from spacy.lang.it import Italian

def get_has_luogo(doc):
            return any([ent.label_=="LUOGO" for ent in doc.ents])

Doc.set_extension("has_luogo", getter=get_has_luogo)

class Parser(object):
    '''
    classdocs
    '''      
    def parse(self, list_article, scraper):
        nlp = Italian()
        
        ruler = nlp.add_pipe("entity_ruler").from_disk("InfoNav/src/data/patterns_withID.jsonl")
        patterns = [{'label':'YEAR', 'pattern': [{'TEXT': {'REGEX': '20[0-9][0-9]'}}]}]

        if scraper == 'BT':
            date_patterns = [ {'label':'DATE', 'pattern': [{'LOWER': {'REGEX': 'stamattina|oggi|stasera'}}, {'LOWER':'pomeriggio', 'OP':'{0,1}'}], 'id':'OGGI'},
                            {'label':'DATE', 'pattern': [{'LOWER': 'ieri'}, {'LOWER': {'REGEX': 'mattina|pomeriggio|sera'}}], 'id':'IERI'},
                            {'label':'DATE', 'pattern': [{'LOWER':"altro"}, {'LOWER':'ieri'}], 'id':"L'ALTRO IERI"},
                            {'label':'DATE', 'pattern': [{'LOWER':"lunedì"}, {'LOWER': {'REGEX': 'mattina|pomeriggio|sera|scorso'}}], 'id':"LUNEDI"},
                            {'label':'DATE', 'pattern': [{'LOWER':"martedì"}, {'LOWER': {'REGEX': 'mattina|pomeriggio|sera|scorso'}}], 'id':"MARTEDI"},
                            {'label':'DATE', 'pattern': [{'LOWER':"mercoledì"}, {'LOWER': {'REGEX': 'mattina|pomeriggio|sera|scorso'}}], 'id':"MERCOLEDI"},
                            {'label':'DATE', 'pattern': [{'LOWER':"giovedì"}, {'LOWER': {'REGEX': 'mattina|pomeriggio|sera|scorso'}}], 'id':"GIOVEDI"},
                            {'label':'DATE', 'pattern': [{'LOWER':"venerdì"}, {'LOWER': {'REGEX': 'mattina|pomeriggio|sera|scorso'}}], 'id':"VENERDI"},
                            {'label':'DATE', 'pattern': [{'LOWER':"sabato"}, {'LOWER': {'REGEX': 'mattina|pomeriggio|sera|scorso'}}], 'id':"SABATO"},
                            {'label':'DATE', 'pattern': [{'LOWER':"domenica"}, {'LOWER': {'REGEX': 'mattina|pomeriggio|sera|scorso'}}], 'id':"DOMENICA"},
                            {'label':'DATE', 'pattern': [{'IS_DIGIT':True}, {'LOWER': {'REGEX': 'gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre'}}], 'id':'NORM'}]
        elif scraper == 'BL':
             date_patterns = [{'label':'DATE', 'pattern': [{'IS_DIGIT':True}, {'LOWER': {'REGEX': 'gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre'}}], 'id':'NORM'}]

        patterns = patterns + date_patterns
        ruler.add_patterns(patterns)

        docs = list(nlp.pipe(list_article))
        
        articles_with_luogo = []
        for doc in docs:
            if doc._.has_luogo:
                articles_with_luogo.append(doc)
            
        return articles_with_luogo