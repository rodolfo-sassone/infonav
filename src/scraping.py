'''
Created on 19 set 2023

@author: Rodolfo Pio Sassone
'''

import bs4
import requests
from myParser import Parser
from datetime import datetime, timedelta
import locale
#BOT per scraping su BARI TODAY

class scraperBT(object):
    '''
    classdocs
    '''
    def __init__(self, topic):
        links = {'inc': ["/tag/incidenti-stradali/"], 'fur':["/tag/furti/", "/tag/furto/"], 'rap':['/tag/rapine/'], 'fire':['/tag/incendi/'], 'drug':['/tag/droga/'], 'arr':['/tag/arresti/'], 'kill':['/tag/omicidi/'], 'agg': ['/tag/aggressioni/'], 'spa':['/tag/sparatoria/']}
        self.link_topic = links[topic]
        self.prefisso = "https://www.baritoday.it"
        self.base_link = self.prefisso + self.link_topic[0]
    

    def get_pages_per_link(self, min_pages = 10, links = []):
        if links == []:
            links = self.link_topic

        list_pages = []
        for link in links:
            old_len = 0

            list_pages = self.get_pages(link = self.prefisso + link, list_pages = list_pages)
            while len(list_pages) < min_pages and old_len < len(list_pages):
                new_link = self.prefisso + list_pages[-1]
                old_len = len(list_pages)
                list_pages = self.get_pages(link = new_link, list_pages = list_pages)
        
        return list_pages

    def get_pages(self, link, list_pages):
        if link == '':
            link = self.base_link
            
        response = requests.get(link)
        response.raise_for_status()
        
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        
        div_pagine = soup.find('div', class_ = 'c-pagination u-flex u-items-center u-justify-center u-py-large')
        pagine = div_pagine.find_all('a', class_="c-pagination__item u-flex u-items-center u-justify-center u-label-04 u-no-underline u-mr-base u-py-xxsmall")
        
        #il primo link non e' presente nella pagina
        if link[len(self.prefisso):] not in list_pages:
            list_pages.append(link[len(self.prefisso):])

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
        
    def scrape(self, min_pages = 10):
        locale.setlocale(locale.LC_TIME, "it_IT")

        list_pages = self.get_pages_per_link(links = self.link_topic, min_pages=min_pages)
        
        list_articles = self.get_articles(list_pages)
        docs = Parser().parse(list_articles, 'BT')

        #LOCALITA NON AGGIUNTA ALLA PIPELINE di spacy quindi niente localita' tra le ent
        list_addresses = []
        current = datetime.now()
        cy = current.strftime('%Y')
        for doc in docs:
            addresses = []
            year = cy
            for ent in doc.ents:
                if ent.label_.lower() == 'luogo':
                    addresses.append(ent.ent_id_.lower())
                elif ent.label_.lower() == 'year':
                    year = ent.text

            date = self.get_date(current, doc, year)
            list_addresses.append({'addresses': addresses, 'date':date, 'year': year}) #lista di indirizzi per ogni articolo trovato e anno

        return list_addresses

    def get_date(self, current, doc, year):
        date = ''
        for ent in doc.ents:
            if ent.label_.lower() == 'date':
                if ent.id_.lower() == 'oggi' and year == '2023':
                    date = current.strftime('%d %B')
                elif ent.id_.lower() == 'ieri' and year == '2023':
                    day = current - timedelta(days=1)
                    date = day.strftime('%d %B')
                elif ent.id_.lower() == "l'altro ieri" and year == '2023':
                    day = current - timedelta(days=2)
                    date = day.strftime('%d %B')
                elif ent.id_.lower() == "lunedi" and year == '2023':
                    today = current.strftime('%A')
                    if today == 'giovedì':
                        td = 3
                    elif today == 'venerdì':
                        td = 4
                    elif today == 'sabato':
                        td = 5
                    elif today == 'domenica':
                        td = 6
                    day = current - timedelta(days = td)
                    date = day.strftime('%d %B')
                elif ent.id_.lower() == "martedi" and year == '2023':
                    today = current.strftime('%A')
                    if today == 'venerdì':
                        td = 3
                    elif today == 'sabato':
                        td = 4
                    elif today == 'domenica':
                        td = 5
                    elif today == 'lunedì':
                        td = 6
                    day = current - timedelta(days = td)
                    date = day.strftime('%d %B') 
                elif ent.id_.lower() == "mercoledi" and year == '2023':
                    today = current.strftime('%A')
                    if today == 'sabato':
                        td = 3
                    elif today == 'domenica':
                        td = 4
                    elif today == 'lunedì':
                        td = 5
                    elif today == 'martedì':
                        td = 6
                    lun = current - timedelta(days = td)
                    date = lun.strftime('%d %B')
                elif ent.id_.lower() == "giovedi" and year == '2023':
                    today = current.strftime('%A')
                    if today == 'domenica':
                        td = 3
                    elif today == 'lunedì':
                        td = 4
                    elif today == 'martedì':
                        td = 5
                    elif today == 'mercoledì':
                        td = 6
                    lun = current - timedelta(days = td)
                    date = lun.strftime('%d %B')
                elif ent.id_.lower() == "venerdi" and year == '2023':
                    today = current.strftime('%A')
                    if today == 'lunedì':
                        td = 3
                    elif today == 'martedì':
                        td = 4
                    elif today == 'mercoledì':
                        td = 5
                    elif today == 'giovedì':
                        td = 6
                    lun = current - timedelta(days = td)
                    date = lun.strftime('%d %B')
                elif ent.id_.lower() == "sabato" and year == '2023':
                    today = current.strftime('%A')
                    if today == 'martedì':
                        td = 3
                    elif today == 'mercoledì':
                        td = 4
                    elif today == 'giovedì':
                        td = 5
                    elif today == 'venerdì':
                        td = 6
                    lun = current - timedelta(days = td)
                    date = lun.strftime('%d %B')
                elif ent.id_.lower() == "domenica" and year == '2023':
                    today = current.strftime('%A')
                    if today == 'mercoledì':
                        td = 3
                    elif today == 'giovedì':
                        td = 4
                    elif today == 'venerdì':
                        td = 5
                    elif today == 'sabato':
                        td = 6
                    lun = current - timedelta(days = td)
                    date = lun.strftime('%d %B')
                elif ent.id_.lower() == 'norm':
                    date = ent.text
        return date
    

class scraperBL(object):

    def __init__(self, topic):
        links = {'inc': 'https://barilive.it/?s=incidenti+stradali', 'fur':'https://barilive.it/?s=furti', 'rap':'https://barilive.it/?s=rapine', 'fire':'https://barilive.it/?s=incendi', 'drug':'https://barilive.it/?s=droga', 'arr':'https://barilive.it/?s=arresti', 'kill':'https://barilive.it/?s=omicidi', 'agg': 'https://barilive.it/?s=aggressioni', 'spa':'https://barilive.it/?s=sparatoria'}
        self.link_topic = links[topic]

    def get_nextPage(self, soup):
        link = None

        nav = soup.find('nav')
        div_pages = nav.find('div', class_ = 'nav-links')
        next_page = div_pages.find('a', class_ = 'next page-numbers')

        if next_page != None:
            link = next_page.get('href')     

        return link
    
    def get_articles(self, soup):
        div_articles = soup.find('div', class_ = 'live-search-content')
        articles = div_articles.find_all('article')

        la = []
        for art in articles:
            title = art.find('h3').get_text()
            date = art.find('span', class_ = 'live-search-date').get_text()
            text = date + ' ' + title

            paragraph = art.find('p')
            if paragraph != None:
                tp = paragraph.get_text()
                text = text + ' ' + tp

            la.append(text)

        return la
    
    def scrape(self, min_pages = 10):
        link_page = self.link_topic
        c = 0
        list_articles = []

        while c < min_pages and link_page != None:
            response = requests.get(link_page)
            response.raise_for_status()
                    
            soup = bs4.BeautifulSoup(response.text, 'html.parser')

            la = self.get_articles(soup)

            list_articles = list_articles + la
            link_page = self.get_nextPage(soup)
            c = c + 1
        
        docs = Parser().parse(list_articles, 'BL')
        
        #LOCALITA NON AGGIUNTA ALLA PIPELINE di spacy quindi niente localita' tra le ent
        list_addresses = []
        current = datetime.now()
        cy = current.strftime('%Y')
        for doc in docs:
            addresses = []
            year = cy
            date = ''
            for ent in doc.ents:
                if ent.label_.lower() == 'luogo':
                    addresses.append(ent.ent_id_.lower())
                elif ent.label_.lower() == 'year':
                    year = ent.text
                elif ent.label_.lower() == 'date':
                    date = ent.text
            list_addresses.append({'addresses': addresses, 'date': date,'year': year}) #lista di indirizzi per ogni articolo trovato e anno

        return list_addresses
