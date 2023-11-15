'''
Created on 19 set 2023

@author: Rodolfo Pio Sassone
'''

import bs4
import requests

#BOT per scraping su BARI TODAY

class scraperBT(object):
    '''
    classdocs
    '''
    def __init__(self, link_topic):
        self.link_topic = link_topic
        self.prefisso = "https://www.baritoday.it"
        self.base_link = self.prefisso + self.link_topic
    
    def get_pages(self, link = '', list_pages = []):
        if link == '':
            link = self.base_link
            
        response = requests.get(link)
        response.raise_for_status()
        
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        
        div_pagine = soup.find('div', class_ = 'c-pagination u-flex u-items-center u-justify-center u-py-large')
        pagine = div_pagine.find_all('a', class_="c-pagination__item u-flex u-items-center u-justify-center u-label-04 u-no-underline u-mr-base u-py-xxsmall")
        
        #il primo link non e' presente nella pagina
        if self.link_topic not in list_pages:
            list_pages.append(self.link_topic)

        for pagina in pagine:
            l = pagina.get('href')
            if l not in list_pages:
                list_pages.append(l)

        return list_pages
    
    
    def get_articles(self, list_page):
        la = []
        
        for link in list_page:
            link_page = self.prefisso + link
            response = requests.get(link_page)
            response.raise_for_status()
                
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            div_articoli = soup.find('div', class_ = 'l-list-border')
            articoli = div_articoli.find_all("article")
        
            for articolo in articoli:
                #link = str(articolo.find("a", class_='o-link-text').get('href'))
                titolo = articolo.find("h1").get_text()
                text = titolo
                
                #il paragrafo potrebbe non essere presente
                paragrafo = articolo.find("p")
                if paragrafo != None:
                    p_text = paragrafo.get_text()
                    text = text + " " + p_text
                
                #aggiungiamo la data dell'articolo
                date = articolo.find('span', class_ = 'c-story__byline u-label-08 u-color-secondary u-mb-xsmall u-block').get_text()

                text = text + " " + date

                la.append(text)
                
        return la
        