import os
from os.path import expanduser

from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import googlemaps

import configparser
from walkscore import WalkScoreAPI




def parse_webpage(url, page_contents):
    soup = BeautifulSoup(page_contents, 'html.parser')
    listing = soup.findAll('div', attrs={'class': 'left-content flex-one'})
    prices, addresses, cities, provinces, zip_codes = get_info(listing)
    details = soup.findAll('div', attrs={'class': 'property-details'})
    beds, baths, property_types = get_details(details)
    url_listing = soup.findAll('app-listing-card', attrs={'class': 'ng-star-inserted'})
    urls = get_urls(url,url_listing)
   
    data = pd.DataFrame()
    data['prices'] = (np.asarray(prices).ravel()).astype(int)
    data['addresses'] = np.asarray(addresses).ravel() 
    data['province'] = np.asarray(provinces).ravel() 
    data['cities'] = np.asarray(cities).ravel()
    data['zips'] = np.asarray(zip_codes).ravel() 
    data['beds'] = np.asarray(beds).ravel()
    data['baths'] = np.asarray(baths).ravel()
    data['property_types'] = np.asarray(property_types).ravel()
    data['latitude'] = get_lat_long(data)[0]
    data['longitude'] = get_lat_long(data)[1]
    data['neighborhood'] = get_lat_long(data)[2]   
    data['walk_score'] = get_walk_transit_bike_scores(data)[0]
    data['transit_score'] = get_walk_transit_bike_scores(data)[1]
    data['bike_score'] = get_walk_transit_bike_scores(data)[2]
    data['url'] = np.asarray(urls).ravel()
    return data
   
def get_info(listing): 
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


def get_details(details):
    total_beds = []
    total_baths = []
    total_property_types = []
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
        
        property_type = inside.text.partition('|')[2].partition('|')[2].partition('|')[2]
        if property_type:        
            total_property_types.append(property_type)
        else:
            total_property_types.append(np.nan)
    return total_beds, total_baths, total_property_types

def get_urls(url, url_listing):
    total_urls = []
    url = url.partition('/on')[0]
    for inside in url_listing:
        total_urls.append(url+'/break'+inside.a['href'])
    return total_urls

def get_lat_long (data):
    latitude = list()
    longitude = list()
    neighborhood = list()

    
    home = expanduser("~")
    passfile = os.path.join(home, "config.ini")
    config = configparser.ConfigParser()
    config.read(passfile)
    
    gmaps = googlemaps.Client(key=config['google-maps-API']['key'])

    
    data.reset_index(drop=True, inplace=True)    
    
    for counter in range(len(data)):
        address_toronto = data['addresses'].iloc[counter] + ',' + \
                          data['cities'].iloc[counter] + ',' + \
                          data['province'].iloc[counter]  + ','+\
                          data['zips'].iloc[counter]
                          
        if ' - ' in address_toronto:
            address_toronto = address_toronto.partition(' - ')[2]
        
        #gMaps
        geocode_result=gmaps.geocode(address_toronto)
        latitude.append(geocode_result[0]['geometry']['location']['lat'])
        longitude.append(geocode_result[0]['geometry']['location']['lng'])
        neighborhood.append(geocode_result[0]['address_components'][2]['short_name'])
        
    return latitude, longitude, neighborhood

    
            
def get_walk_transit_bike_scores (data):
    walk_score = list()
    transit_score = list()
    bike_score = list()
    
    home = expanduser("~")
    passfile = os.path.join(home, "config.ini")
    config = configparser.ConfigParser()
    config.read(passfile)
    
    home = expanduser("~")
    passfile = os.path.join(home, "config.ini")
    config = configparser.ConfigParser()
    config.read(passfile)
    
    walk_api = WalkScoreAPI(api_key = config['walkscore-API']['key'])
    
    data.reset_index(drop=True, inplace=True)    

    for counter in range(len(data)):
        address_toronto = data['addresses'].iloc[counter] + ',' + \
                          data['cities'].iloc[counter] + ',' + \
                          data['province'].iloc[counter]  + ','+\
                          data['zips'].iloc[counter]
                          
        if ' - ' in address_toronto:
            address_toronto = address_toronto.partition(' - ')[2]
            
        result_walk = walk_api.get_score(longitude = data['longitude'].iloc[counter], 
                                         latitude = data['latitude'].iloc[counter], 
                                         address = address_toronto)
        
        walk_score.append(result_walk.walk_score)
        transit_score.append(result_walk.transit_score)
        bike_score.append(result_walk.bike_score)
        
        
        
    return walk_score, transit_score, bike_score


