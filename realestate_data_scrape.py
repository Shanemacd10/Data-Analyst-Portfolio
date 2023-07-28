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
    
    def url_search(url):
        #(str)-->(BeautifulSoup) takes a url string and outputs html soup object
        html_txt = requests.get(url).text
        soup = BeautifulSoup(html_txt, 'lxml')
        return soup

    def search_loop():
        #()-->()iterates through price search params and runs page_loop to get data for each result (needed since royallepage.ca limits result to <=1000)
        for x in range(1,10):
            n = str(x*100000)
            m = str(x*100000 + 99999)
            soup = url_search(r'https://www.royallepage.ca/en/search/homes/?search_str=Nova+Scotia%2C+NS%2C+CAN&csrfmiddlewaretoken=gwr7nLTOgjCRzUfCho1OZ1vY4a1XWmfPkhXlSnpDItMAY1eaxcS4cXk3j3QhCZZS&property_type=&house_type=&features=&listing_type=&lat=45.76663995400003&lng=-61.63182999999998&upper_lat=&upper_lng=&lower_lat=&lower_lng=&bypass=&radius=&zoom=&display_type=gallery-view&travel_time=false&travel_time_min=30&travel_time_mode=drive&travel_time_congestion=&da_id=&segment_id=&tier2=False&tier2_proximity=0&address=Nova+Scotia&method=homes&address_type=province&city_name=&prov_code=NS&school_id=&min_price=' + n + r'&max_price=' + m +r'&min_leaseprice=0&max_leaseprice=5000%2B&beds=0&baths=0&transactionType=SALE&keyword=&sortby=')
            temp_lst = soup.find('ul', class_='frow').text
            if temp_lst is None:
                pg_nums = 1
            else:
                pg_nums = int(temp_lst.split()[-1])
                
            page_loop(n, m, pg_nums, soup)
        page_loop('0', '50000', pg_nums, soup)
        page_loop('50001', '99999', pg_nums, soup)
        page_loop('1000000', '5000000%2B', pg_nums, soup)
    
    def page_loop(n,m,pg_nums, soup):
        #(str, str, int, BeautifulSoup)-->() iterates through each page of search with price search params and runs add_house_data to get data on each page
        for x in range(1, pg_nums +1):
            url = r'https://www.royallepage.ca/en/search/homes/' + str(x) + r'/?search_str=Nova+Scotia%2C+NS%2C+CAN&csrfmiddlewaretoken=gwr7nLTOgjCRzUfCho1OZ1vY4a1XWmfPkhXlSnpDItMAY1eaxcS4cXk3j3QhCZZS&property_type=&house_type=&features=&listing_type=&lat=45.76663995400003&lng=-61.63182999999998&upper_lat=&upper_lng=&lower_lat=&lower_lng=&bypass=&radius=&zoom=&display_type=gallery-view&travel_time=false&travel_time_min=30&travel_time_mode=drive&travel_time_congestion=&da_id=&segment_id=&tier2=False&tier2_proximity=0&address=Nova+Scotia&method=homes&address_type=province&city_name=&prov_code=NS&school_id=&min_price=' + n + r'&max_price=' + m + r'&min_leaseprice=0&max_leaseprice=5000%2B&beds=0&baths=0&transactionType=SALE&keyword=&sortby='
            soup = url_search(url)
            add_house_data(soup, house_list)

            #sleep function to not overwhelm royallepage website servers with requests
            secs = random.randint(1, 10)
            time.sleep(secs)

    def add_house_data(soup, house_lst):
        #(str, lst) --> () takes unfiltered html string and sorts and adds address, city, price, bedrooms, and bathrooms to house list
        houses = soup.find_all('li', class_ = 'card-group__item')
        for x in houses:
                lst=[]
                
                #Gets address and appends to lst
                address = x.find('address', class_ = 'address-1')
                lst.append(none_type_check(address))

                city_prov = x.find('address', class_ = 'card__address-2')
                cp = none_type_check(city_prov)

                #checking if string is none type, if it isn't splitting city and province and appending to lst
                if cp is None:
                    city = None
                    prov = None
                else:
                    city, prov = cp.split(', ')
                    prov = can_prov_names[prov]
                lst.append(city)
                lst.append(prov)
                
                #getting lattitude and longitude from html code and appending them to lst
                lat_long = x.find('div').attrs['data-rlp-key']
                temp = lat_long.split('.')
                lat = '.'.join(temp[:2])
                long = '.'.join(temp[2:])
                lst.append(lat)
                lst.append(long)
                
                price = x.find('span', class_ = 'title--h3 price')
                lst.append(int(none_type_check(price)[1:].replace(',', '')))

                #getting then splitting number of beds and baths then appending to lst
                bed_bath = x.find('div', class_ = 'listing-meta listing-meta--small').text
                bed_bath = ' '.join(bed_bath.split())
                bed_bath_nums = re.findall(r'\d+',bed_bath)
                lst.append(bed_bath.split(' ',1)[0])
                bed_bath = re.findall(r'\d+',bed_bath)
                for n in bed_bath:
                    lst.append(int(n))
                house_list.append(lst)

    def none_type_check(house):
        #(bs4.element.Tag)-->(str) takes a BeatifulSoup element and checks if it is none empty
        if house is None:
            return None
        else:
            temp = house.text
            return ' '.join(temp.split())

    def add_sheet():
        #()-->()writes data to Realestate_Data_Scrape.xlsx with sheet name RL_Data_day.month.year_Nova_Scotia
        now = datetime.now()
        s_name = 'RL_Data_' + now.strftime('%d.%m.%Y_Nova_Scotia')
        df = pd.DataFrame(data = house_list, columns = ['Address', 'City', 'Province', 'Lattitude', 'Longitude', 'Price', 'Property_Type', 'Bedrooms', 'Bathrooms'])
        writer = pd.ExcelWriter(r'C:\Users\Shane\Downloads\Excel\Realestate_Data_Scrape.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name= s_name)
        writer._save()
        
# Dict used to convert abreviated provinces to full names 
    can_prov_names = {
  'AB': 'Alberta',
  'BC': 'British Columbia',
  'MB': 'Manitoba',
  'NB': 'New Brunswick',
  'NL': 'Newfoundland and Labrador',
  'NS': 'Nova Scotia',
  'NT': 'Northwest Territories',
  'NU': 'Nunavut',
  'ON': 'Ontario',
  'PE': 'Prince Edward Island',
  'QC': 'Quebec',
  'SK': 'Saskatchewan',
  'YT': 'Yukon'
}
# Runs the search loop to get the data and add it to house_list then adds it to a new sheet in excel
    print('Please wait until data is downloaded')
    house_list = []
    search_loop()
    add_sheet()
    print('Data Downloaded')
    
if __name__ == '__main__':
    main()
