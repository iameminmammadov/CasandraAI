from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import googlemaps


'''
ToDO
1. Add parks/high_school scores/cafes/greenery/etc
2. add longitude/latitude/walk_score/transit_score
3. Add images
4. Add year built
5. Fix it to show only for sale options
'''
class Scraper:
    def __init__(self, pages):
        self.pages = pages
    
    @staticmethod
    def get_headers():
        headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'accept-encoding': 'gzip, deflate, sdch, br',
               'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
               'cache-control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
        return headers

    def get_listings(self):
        headers = self.get_headers()
        #decide whether dict or list
#        total_listings = dict()
        data = pd.DataFrame() 
        total_listings = []
        total_prices = []
        total_addresses = []
        total_cities = []
        total_provinces = []
        total_zips = []        
        total_beds = []
        total_baths = []
        total_property_types = []
        total_sqft = []
        total_urls = []
        total_inside_listing = {}

        pages = self.pages + 1
        for page in range(1, pages):
            print (page)
            url = 'https://www.remax.ca/on/toronto-real-estate?page=' + str(page)
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            listing = soup.findAll('div', attrs={'class': 'left-content flex-one'})
            total_listings.append(listing) #that will return list with loops: 20 results packed into list of 3
#            total_listings[page] = listing
            prices, addresses, cities, provinces, zips = self.get_info(listing)
            
            total_prices.append(prices)
            total_addresses.append(addresses)
            total_cities.append(cities)
            total_provinces.append(provinces)
            total_zips.append(zips)
            
            details = soup.findAll('div', attrs={'class': 'property-details'})
            beds, baths, property_types, sqft = self.get_details(details)
            total_beds.append(beds)
            total_baths.append(baths)
            total_property_types.append(property_types) 
            total_sqft.append(sqft)
            
            url_listing = soup.findAll('app-listing-card', attrs={'class': 'ng-star-inserted'})
            total_urls.append(self.get_urls(url,url_listing))
            
        #for counter, value in enumerate(np.asarray(total_urls).ravel()):
        #    total_inside_listing[counter] = self.get_inside_listing(value)
           
        data['prices'] = (np.asarray(total_prices).ravel()).astype(int)
        data['addresses'] = np.asarray(total_addresses).ravel() 
        data['province'] = np.asarray(total_provinces).ravel() 
        data['cities'] = np.asarray(total_cities).ravel()
        data['zips'] = np.asarray(total_zips).ravel() 
        data['beds'] = np.asarray(total_beds).ravel()
        data['baths'] = np.asarray(total_baths).ravel()
        data['property types'] = np.asarray(total_property_types).ravel()
        data['sqft'] = np.asarray(total_sqft).ravel() 
        data['url'] = np.asarray(total_urls).ravel()
        #data['lat'] = self.get_lat_long(data)[0]
       # data['long'] = self.get_lat_long(data)[1]
        #data['neighborhood'] = self.get_lat_long(data)[2]
        #data['description']=total_inside_listing.values()
        
        
        return data


    def get_info(self, listing): 
        total_prices = []
        total_addresses = []
        total_provinces = []
        total_cities = [] 
        total_zips = []
        for inside in listing:
            price = inside.find('h3', attrs={'class': 'price'}).text.partition('$')[2] #np.array?
            price = price.replace(',','')

            total_prices.append(price)
            info = inside.find_all('span', attrs={'class': 'ng-star-inserted'})
            total_addresses.append(info[1].text.replace(',',''))
            total_cities.append(info[2].text.replace(',',''))
            total_provinces.append(info[4].text.replace(',',''))
            total_zips.append(info[6].text)
        return total_prices, total_addresses, total_cities, total_provinces, total_zips
    
    def get_details(self, details):
        total_beds = []
        total_baths = []
        total_property_types = []
        total_sqft = []
        for inside in details:
            bed = inside.text.partition('|')[0]
            if bed:
                bed = bed.replace('bed','')
                total_beds.append(bed)
            else:
                total_beds.append(np.nan)
            
            bath = inside.text.partition('|')[2].partition('|')[0]
            if bath:
                bath = bath.replace('bath','')
                total_baths.append(bath)
            else:
                total_baths.append(np.nan)
            
            sqft = inside.text.partition('|')[2].partition('|')[2].partition('|')[0]
            if sqft:
                try:
                    sqft = sqft.replace('sqft','')
                    total_sqft.append(int(sqft))
                except ValueError:
                    total_sqft.append(np.nan)       
            else:
                total_sqft.append(np.nan)
            
            
            property_type = inside.text.partition('|')[2].partition('|')[2].partition('|')[2]
            if property_type:        
                total_property_types.append(property_type)
            else:
                total_property_types.append(np.nan)
        return total_beds, total_baths, total_property_types, total_sqft
    
    def get_urls(self, url, url_listing):
        total_urls = []
        url = url.partition('/on')[0]
        for inside in url_listing:
            total_urls.append(url+'/break'+inside.a['href'])
        return total_urls
    
    def get_inside_listing (self, url_inside_listing):
        headers = self.get_headers()
        response = requests.get(url_inside_listing, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        '''
        try:
            description = soup.find('p', attrs={'class': 'content'})
            return description.text
        except AttributeError:
            return np.nan
        '''   
        #if 'sqft' in description or 'sqf' in description:
        #    sqft = description[description.description('sqft')-5:description.find('sqf')+5]
       
    def get_lat_long (self,data):
        lat = list()
        long = list()
        neighborhood = list()
        gmaps = googlemaps.Client(key='AIzaSyCgMx9AYHqce9sQaXs29zvSQEcpjGXZFj0')

        for counter in range(len(data)):
            address_toronto = data['addresses'][counter] + ',' + data['cities'][counter] + ',' + \
                              data['province'][counter]  + ','+data['zips'] [counter]
                              
            if ' - ' in address_toronto:
                address_toronto = address_toronto.partition(' - ')[2]
            
            try:
                geocode_result=gmaps.geocode(address_toronto)
                lat.append(geocode_result[0]['geometry']['location']['lat'])
                long.append(geocode_result[0]['geometry']['location']['lng'])
                neighborhood.append(geocode_result[0]['address_components'][2]['short_name'])
                
            except IndexError:
                geocode_result=gmaps.geocode(address_toronto)
                lat.append(geocode_result[0]['geometry']['location']['lat'])
                long.append(geocode_result[0]['geometry']['location']['lng'])
                neighborhood.append(geocode_result[0]['address_components'][2]['short_name'])

        return lat, long, neighborhood
        
    def to_db (self, data):
        pass




if __name__=="__main__":  
    scraper = Scraper (120)
    data  = scraper.get_listings()
   