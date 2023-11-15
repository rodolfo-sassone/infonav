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
    def parse_where(self, list_article):
        nlp = Italian()
        
        ruler = nlp.add_pipe("entity_ruler").from_disk("InfoNav/src/data/patterns_withID.jsonl")
        patterns = [{'label':'YEAR', 'pattern': [{'TEXT': {'REGEX': '20[0-9][0-9]'}}]}]

        ruler.add_patterns(patterns)

        docs = list(nlp.pipe(list_article))
        
        articles_with_luogo = []
        for doc in docs:
            if doc._.has_luogo:
                articles_with_luogo.append(doc)
            
        return articles_with_luogo