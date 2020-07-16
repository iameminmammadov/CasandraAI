import pandas as pd
import database_worker as dw

def load_data_into_df ():
    engine = dw.get_engine()
    df = pd.read_sql_table('remax_table', engine)
    return df
    
def transform_loaded_data ():
    df = load_data_into_df()
    urls = list(df['url'])
    df.drop(['scraped_date', 'property_types', 'url',],inplace=True,axis=1)
    return df
    