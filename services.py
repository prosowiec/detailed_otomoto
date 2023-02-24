from bs4 import BeautifulSoup
from urllib.request import urlopen
import ssl 
import certifi
import http.client  
import regex as re
import pandas as pd
import os
http.client._MAXHEADERS = 1000


class parameters:
    make:str = ''
    model:str = ''
    price = 0
    year = 0
    mileage = 0
    eng_cap = 0
    eng_type = ''
    power = 0
    gearbox:str = ''
    transmission:str = ''
    body:str = ''
    origin:str = ''
    condition:int = 1
    equipment:int = 1

class Scraper(parameters):
    def __init__(self,soup = '', soup_prettify = '', param_table='') -> None:
        self.soup = soup
        self.soup_prettify = soup_prettify
        self.param_table = param_table
        self.currency = ''
        self.filename = ''
        self.url = ''

    def make_soup(self,url):
        self.url = url
        r = urlopen(url, context=ssl.create_default_context(cafile=certifi.where()))
        self.soup = BeautifulSoup(r, "html.parser")
        self.soup_prettify = self.soup.prettify()
        self.param_table = self.soup.find_all("div", {"class":"offer-content offer-content--secondary"})
        self.param_table = str(self.param_table[0]).replace('\n', ' ')

    def make_parameters(self):
        self.year = int(self.find_re(pattern = '(?<=produkcji</span> <div class=\"offer-params__value\"> )(.*?)(?= </div>)'))
        self.mileage = self.erase_unit(self.find_re(pattern= '(?<=Przebieg</span> <div class=\"offer-params__value\"> )(.*?)(?= </div>)'))
        self.eng_cap = self.erase_unit(self.find_re(pattern= '(?<=skokowa</span> <div class=\"offer-params__value\"> )(.*?)(?= </div>)'))
        self.eng_type = self.find_re(pattern= '(?<=filter_enum_fuel_type%5D%5B0%5D=)(.*?)(?=\" title)')
        self.power = self.erase_unit(self.find_re(pattern= '(?<=Moc</span> <div class=\"offer-params__value\"> )(.*?)(?= </div>)'))
        self.gearbox = self.find_re(pattern= '(?<=filter_enum_gearbox%5D%5B0%5D=)(.*?)(?=\" title)')
        self.transmission = self.find_re(pattern= '(?<=filter_enum_transmission%5D%5B0%5D=)(.*?)(?=\" title)')
        self.body = self.find_re(pattern= '(?<=/seg-)(.*?)(?=/\" title)')
        self.origin = self.find_re(pattern= '(?<=filter_enum_country_origin%5D%5B0%5D=)(.*?)(?=\" title)')
        self.make_price()
        self.make_model()

    def get_imglist(self):
        img_pat = re.compile('(?<={\"src\":\")(.*?)(?=\",\"w\":0,\"h\":0})')
        image_list = re.findall(img_pat,self.soup_prettify)
        for i,img in enumerate(image_list):
            img = re.sub('\\\\','',img)
            image_list[i] = img
        return image_list
    
    def make_model(self):
        pattern = re.compile('(?<=\/oferta\/)(.*?)(?=-)')
        self.make = re.search(pattern, self.url).group(0)
        pattern = re.compile(f'(?<={self.make}-)(.*?)(?=-)')
        self.model = re.search(pattern, self.url).group(0)

    def make_price(self):
        self.price = self.soup.find_all("span", {"class":"offer-price__number"})
        self.price = str(self.price[0])
        if 'PLN' in self.price:
            self.currency = 'PLN'
        else:
            self.currency = 'EUR'
        self.price= self.erase_unit(self.price)
    
    def find_re(self,pattern):
        pattern = re.compile(pattern)
        search = re.findall(pattern, self.param_table)
        try:
            return search[0]
        except IndexError:
            return '0' 
    
    def erase_unit(self,param):
        res = ''
        for i in range(1,len(param)-1):
            if param[i].isnumeric() and not param[i+1].isalpha() and not param[i-1].isalpha() :
                res +=param[i]
        return int(res)

    def load_df(self):
        headers = ['make','model','price' ,'year','mileage','eng_cap','eng_type' ,'power','gearbox','transmission','body','origin','condition','equipment']
        data = {
                'make' : [self.make],
                'model': [self.model],
                'price' : [self.price],
                'year' : [self.year],
                'mileage' : [self.mileage],
                'eng_cap' : [self.eng_cap],
                'eng_type' : [self.eng_type],
                'power' : [self.power],
                'gearbox' : [self.gearbox],
                'transmission' : [self.transmission],
                'body' : [self.body],
                'origin' : [self.origin],
                'condition' : [self.condition],
                'equipment' : [self.equipment],
        }
        df = pd.DataFrame(data)
        if not os.path.isfile(f'data/{self.filename}'):
           df.to_csv(f'data/{self.filename}', header=headers, index = False)
        else: 
           df.to_csv(f'data/{self.filename}', mode='a', header=False,index = False)

class Links:
    def __init__(self):
        self.soup = ''
        self.soup_find = ''
        self.url = ''
        self.file_name = ''
        self.link_list = []

    def make_soup(self):
        r = urlopen(self.url, context=ssl.create_default_context(cafile=certifi.where()))
        self.soup = BeautifulSoup(r, "html.parser")
        self.soup_find = str(self.soup.find("main", {"class":"ooa-1hab6wx eagdslh9"}))
    
    def scrape_links(self):
        for page in range(1,self.number_of_pages_oto()):
            self.url = f'{self.url}&page={page}'
            self.make_soup()
            pattern = re.compile('(?<=<a href=\")(.*?)(?=\" target=\")')
            search = re.findall(pattern, self.soup_find)
            for link in search:
                df = pd.DataFrame({link})
                df.to_csv(f'links/{self.file_name}.csv', mode='a', index=False, header=False)
        
        df = pd.DataFrame({self.file_name+'.csv'})
        df.to_csv(f'filenames.csv', mode='a', index=False, header=False)

    def number_of_pages_oto(self):
        page_pattern = re.compile('(?<=<li aria-label=\"Page )(.*?)(?=\" class=\"pagination)')
        page = re.findall(page_pattern,str(self.soup))
        if not page:
            number_of_pages = 1
        else:
            number_of_pages = page.pop()
        return int(number_of_pages)
    


    