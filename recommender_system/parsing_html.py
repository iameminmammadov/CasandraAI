import logging 
import os 
from io import BytesIO, StringIO
from zipfile import ZIP_DEFLATED, ZipFile
from requests.adapters import HTTPAdapter
import time
from datetime import date
import boto3


from bs4 import BeautifulSoup
from requests.packages.urllib3.util.retry import Retry

import numpy as np
import pandas as pd
import requests
import googlemaps

import aws

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
    data['cities'] = np.asarray(provinces).ravel()
    data['zips'] = np.asarray(zip_codes).ravel() 
    data['beds'] = np.asarray(beds).ravel()
    data['baths'] = np.asarray(baths).ravel()
    data['property_types'] = np.asarray(property_types).ravel()
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


