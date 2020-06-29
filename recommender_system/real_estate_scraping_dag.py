from os import getenv
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

from etl_main import extract, transform, load

'''
Extract performs the extraction steps of webscraping:
    - downloads raw pages contents
    - zips data
    - unload zipped archived into S3
'''

'''
Transform performs the transform step of the pipeline:
    - downloads and unzips raw page archive from S3
    - parse page contents to retrive the actual data
    - write data as a csv file 
    - upload CSV to S3
'''

'''
Load CSV file containing the actual data into the database
'''

default_args = {
        'owner': 'Emin Mammadov',
        'depends_on_past': False,
        'start_date': datetime.now(),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 3,
        'retry_delay': timedelta(minutes = 30)
        }

dag = DAG ('real_estate_etl', 
           default_args = default_args, 
           schedule_interval='@once') #weekly


extract_task = PythonOperator(task_id = 'extract', 
                              python_callable = extract, 
                              dag = dag)

transform_task = PythonOperator(task_id = 'transform',
                                python_callable = transform,
                                dag = dag)

load_task = PythonOperator(task_id = 'load',
                           python_callable = load,
                           dag = dag)

extract_task >> transform_task >> load_task

'''
#'start_date': datetime.strptime (getenv('Scraping will start on'), 
        #                                 '%Y-%m-%dT%H:%M'),
'''