from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import xlsxwriter
from openpyxl import load_workbook
from datetime import datetime
import time
import random

def main():
    #()--> (str) prompts user for url input and returns a string of unfiltered html house data
    def add_house_data(soup, house_lst):
        #(str, lst) --> () takes unfiltered html string and sorts and adds data points to a list
        houses = soup.find_all('li', class_ = 'card-group__item')
        for x in houses:
                lst=[]
            #Gets data from HTML code
                address = x.find('address', class_ = 'address-1')
                lst.append(none_type_check(address))

                location = x.find('address', class_ = 'card__address-2')
                lst.append(none_type_check(location))
                
                price = x.find('span', class_ = 'title--h3 price')
                lst.append(int(none_type_check(price)[1:].replace(',', '')))
                
                bed_bath = x.find('div', class_ = 'listing-meta listing-meta--small').text
                
            # Eliminates spaces in HTML code and adds the data points to a list
                bed_bath = ' '.join(bed_bath.split())
                bed_bath_nums = re.findall(r'\d+',bed_bath)
                lst.append(bed_bath.split(' ',1)[0])
                
            # Gets number of bedrooms and bathrooms and appends to lst
                bed_bath = re.findall(r'\d+',bed_bath)
                for n in bed_bath:
                    lst.append(int(n))
                    
                house_list.append(lst)
    def none_type_check(house):
            if house is None:
                return None
            else:
                address = house.text
                return ' '.join(address.split())

    def page_loop():
        for x in range(1, pg_nums +1):
            url = 'https://www.royallepage.ca/en/search/homes/ns/halifax/' + str(x)+'/?property_type=&house_type=&features=&listing_type=&lat=44.648881000000074&lng=-63.57531199999994&bypass=&address=Halifax&address_type=city&city_name='+ city + r'&prov_code=' + prov + r'&display_type=gallery-view&da_id=&travel_time=&school_id=&search_str=Halifax%2C+NS%2C+CAN&id_search_str=Halifax%2C+NS%2C+CAN&school_search_str=&travel_time_min=30&travel_time_mode=drive&travel_time_congestion=&min_price=0&max_price=5000000%2B&min_leaseprice=0&max_leaseprice=5000%2B&beds=0&baths=0&transactionType=SALE&keyword='
            soup = url_search(url)
            add_house_data(soup, house_list)
            secs = random.randint(1, 10)
            time.sleep(secs)
            
    def url_search(url):
        html_txt = requests.get(url).text
        soup = BeautifulSoup(html_txt, 'lxml')
        return soup
        
            
    def add_sheet():
        now = datetime.now()
        s_name = 'RL_Data_' + now.strftime('%d.%m.%Y_' + city +'_' + prov)
        df = pd.DataFrame(data = house_list, columns = ['Address', 'City', 'Price', 'Property_Type', 'Bedrooms', 'Bathrooms'])
        writer = pd.ExcelWriter(r'C:\Users\Shane\OneDrive\Documents\Realestate_Data_Scrape.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name= s_name)
        writer._save()
    city = input('Enter the city you would like to search: ')
    prov = input ('Enter the province you would like to search (Abriviated): ')
    print('Please wait until data is downloaded')
    temp = url_search(r'https://www.royallepage.ca/en/search/homes/ns/halifax/?property_type=&house_type=&features=&listing_type=&lat=44.648881000000074&lng=-63.57531199999994&bypass=&address=Halifax&address_type=city&city_name='+ city + '&prov_code=' + prov + '&display_type=gallery-view&da_id=&travel_time=&school_id=&search_str=Halifax%2C+NS%2C+CAN&id_search_str=Halifax%2C+NS%2C+CAN&school_search_str=&travel_time_min=30&travel_time_mode=drive&travel_time_congestion=&min_price=0&max_price=5000000%2B&min_leaseprice=0&max_leaseprice=5000%2B&beds=0&baths=0&transactionType=SALE&keyword=')
    temp_lst = temp.find('ul', class_='frow').text
    pg_nums = int(temp_lst.split()[-1])
    house_list = []
    page_loop()
    add_sheet()
    print('Data Downloaded')
    
if __name__ == '__main__':
    main()

