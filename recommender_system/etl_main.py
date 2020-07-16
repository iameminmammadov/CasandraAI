import logging 
import os 
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from requests.adapters import HTTPAdapter
import time
from datetime import date



from requests.packages.urllib3.util.retry import Retry

import pandas as pd
import requests

#Custom 
import parsing_html
import aws
import database_worker as dw

def validate_urls(urls):
    """
    Make sure each URL in a list starts with 'http://' and is not empty,
    which can happen when reading URLs from a file.
    :param list(str) urls: list of URLs
    :return list(str): list of validated URLs
    """
    validated = []

    for u in urls:
        if u.startswith('http://'):
            validated.append(u)

        elif u.startswith('www.'):
            validated.append(f'http://{u}')

        else:
            continue

    return validated

def get_urls_from_s3(bucket, urls_key):
    '''
    Get a list of URLs to scrape from a text file stored in S3
    '''
    data = aws.download_s3_object(bucket, urls_key)
    text = data.decode()
    urls = text.split(os.linesep)
    validated = validate_urls(urls)
    return validated
    
    
def get_headers():
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'accept-encoding': 'gzip, deflate, sdch, br',
           'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
           'cache-control': 'max-age=0',
           'upgrade-insecure-requests': '1',
           'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
    return headers    

def get_session(max_retries, backoff_factor, retry_on):
    '''Get session object for the HTTP request.


    :param int max_retries: maximum number of retries on HTTP request failure
    :param float backoff_factor: delay second attemp for HTTP request retry
    :param int retry_on: codes that dictate whether or not a retry should be attempted
    :return session: session object

    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    '''
    session = requests.Session()
    retry = Retry(total=max_retries, connect = max_retries,
                  read=max_retries, backoff_factor =backoff_factor,
                  status_forcelist = retry_on)
    adapter = HTTPAdapter (max_retries = retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session

def download_page_content(url, session, max_retries):
    """
    Download the contents of a web page.
    
    If the server's response was 200, proceed.
    If the response is not 200 and not one of the status codes the Session
    object is programmed to retry on (500, 502 and 504), send the
    status code.
    
    Retry 10 times.
    
    :param requests.Session: Session object
    :param str url: page URL
    :param int timeout: allowed period for the server to respond (in seconds)
    :param int max_retries: maximum number of retries if HTTP request fails
    :return str: web page content
    """
    headers = get_headers()
    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            start = 'www.'
            end = '.ca'
            url_name = url[url.find(start)+ len(start):url.find(end)]
            logging.info(f'scraped {url_name}')
            print ('scraped')
            return response.text
        else:
            msg = f'scraping failed with the response code: {response.status_code} for {url}'
            logging.error(msg)
            return
    except Exception as e:
        msg = f'scraping failed: {e} for {url}'
        logging.error(msg)
        max_retries = max_retries - 1
        time.sleep (60)


def extract ():
    '''
    Performs the extraction steps of webscraping:
        download raw pages content
        zip data 
        upload data to AWS S3
    '''
    zip_file_object = BytesIO()
    zip_archive = ZipFile(zip_file_object, 'a', compression=ZIP_DEFLATED)
    session = get_session (5, backoff_factor=0.3, retry_on=(500, 502, 504))
    today = date.today()

    # Go through url and download the page content 
    logging.info('scraping started')    
    pages = 4
    for page in range(1, pages):
        print (page)
        url = 'https://www.remax.ca/on/toronto-real-estate?page=' + str(page)
        results = download_page_content(url, session, 5)
        if results is not None:
            start = 'www.'
            end = '.ca'
            url_name = url[url.find(start)+ len(start):url.find(end)]
            name = url_name + '_page_' +str(page) +'_' + str(today)
            zip_archive.writestr(f'{name}.txt', results)    
        time.sleep(1)
    
    zip_archive.close()
    archive_key = 'raw_page_content_' +url_name + '_' + str(today) 
    aws.upload_s3_object(zip_file_object, bucket='remaxraw',key=archive_key)

def transform():
    today = date.today()      
    url = 'https://www.remax.ca/on/toronto-real-estate' 
    start = 'www.'
    end = '.ca'
    url_name = url[url.find(start)+ len(start):url.find(end)]
    archive_key = 'raw_page_content_' +url_name + '_' + str(today) 
    logging.info(f'downloading raw pages from {url_name}')
    raw_pages_zip = aws.download_s3_object('remaxraw', archive_key)
    logging.info('reading raw pages archive')
    zip_data = BytesIO(raw_pages_zip)
    zip_obj = ZipFile(zip_data,'r')

    data = pd.DataFrame()
    for file_name in zip_obj.namelist():        
        print (file_name)
        page_contents = zip_obj.read(file_name).decode()
        parsed = parsing_html.parse_webpage(url, page_contents)
        data = pd.concat([data, parsed],axis=0)
    return data

    '''Dump it to S3. It can be dumped to S3 and logged from S3 into Database.
    I am just logging straight into DB'''


def load():
    '''Load the dataframe into database
    ToDo:
        Write a check to stop when url start repeating.
    '''
    #data = transform()
    data.drop_duplicates(inplace=True)
    data.reset_index(inplace=True, drop=True)
    data['scraped_date'] = [str(date.today())] * len(data)
    
    
    table_name = 'remax_table'
    scraping_date = str(date.today())
    engine = dw.get_engine()     
    connection = dw.get_connection()
    curr = connection.cursor()
    
    if dw.table_exists(table_name, curr) is False:
        dw.create_table(table_name, curr)
        connection.commit()
        connection.close()
        
    connection = dw.get_connection()
    curr = connection.cursor()
    
    
    if dw.table_exists(table_name, curr): 
        dw.check_table_for_loaded_data(table_name,scraping_date, curr)
        connection.commit()
        connection.close()
        curr.close()
        
        connection = dw.get_connection()
        curr = connection.cursor()
        
        logging.info(f'writing into {table_name}')
        data.to_sql(table_name, engine, if_exists='append', index=False)
    
    connection.commit()
    connection.close()
    curr.close()
    engine.dispose()

    


extract()
data = transform()
#load()