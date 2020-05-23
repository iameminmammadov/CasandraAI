import logging
import sys
import os
from os.path import expanduser
import configparser

from sqlalchemy import create_engine
import psycopg2
from psycopg2.extensions import AsIs
from psycopg2 import sql


def get_connection():
    home = expanduser("~")
    passfile = os.path.join(home, "config.ini")
    config = configparser.ConfigParser()
    config.read(passfile)
    conn = None
    try:
        conn = psycopg2.connect(database = config['database']['database'],
                                user = config['database']['username'],
                                password = config['database']['password'],
                                host = config['database']['hostname'],
                                port= config['database']['port'])
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return False

def get_engine():
    home = expanduser("~")
    passfile = os.path.join(home, "config.ini")
    config = configparser.ConfigParser()
    config.read(passfile)
    engine_config = config['database']['engine']
    engine = create_engine(engine_config, echo=True)
    return engine

def table_exists (table_name, curr):
    '''Check if table exists in database.
    :param str table_name: name of the table
    :param connection: connection
    :return bool: If table exists, return True
    '''
    #curr = connection.cursor()
    curr.execute("select exists(select * from information_schema.tables where table_name=%s)",
                (table_name,))
    return curr.fetchone()[0]
    
'''
def already_loaded(table_name, scraping_date, curr):
    
    There can be duplicates if scraping is run on the same date
    :param str table_name: name of the table
    :param str scraping_date: date of the scraping
    :param connection: psycopg2 connection object
    :return bool: True if rows corresponding to scraping_date are present
    
    #curr = connection.cursor()
    query = """select exists 
                (select 1 from {}
                where collection_date = {})""".format(sql.Identifier('table_name'), scraping_date)
    curr.execute(query)
    return curr.fetchone()[0]
'''

            
def create_table(table_name, curr):
    query = """ 
                CREATE TABLE IF NOT EXISTS {} (
                        url VARCHAR PRIMARY KEY,
                        prices INT,
                        addresses VARCHAR,
                        province VARCHAR,
                        cities VARCHAR,
                        zips VARCHAR,
                        beds VARCHAR,
                        baths VARCHAR,
                        property_types VARCHAR,
                        scraped_date VARCHAR
                        )""".format(table_name)
    #curr = connection.cursor()
    curr.execute(query)
    

        
    
    
