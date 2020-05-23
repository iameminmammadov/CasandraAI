import pandas as pd
import numpy as np
import pickle
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MaxAbsScaler, LabelEncoder, OrdinalEncoder 
from pandas.api.types import is_numeric_dtype



data = pd.read_csv('data_dash.csv')
data.drop(['sqft', 'property types'],inplace=True,axis=1)
data.dropna(axis=0, inplace=True) #bike score is 0
data_train = data.copy()
for col in data_train:
    if is_numeric_dtype(data_train[col]):
        data_train[col] = data_train[col].astype(int)


oe = OrdinalEncoder()
data_train = pd.DataFrame(oe.fit_transform(data_train), columns=data_train.columns)


mabs = MaxAbsScaler()
data_train = pd.DataFrame(mabs.fit_transform(data_train), columns = data_train.columns)

nbrs= NearestNeighbors(n_neighbors=1, metric='cosine')
nbrs.fit(data_train)

preferences = pd.read_csv('prefs.csv')
preferences.drop_duplicates(keep='first', inplace=True)
temp = pd.DataFrame(columns=list(data))
for counter, value in enumerate(preferences.iterrows()):
    temp.loc[counter] = data.loc[value[0]]

final_preferences = temp.copy()

#print (preferences.shape)
#nbrs = pickle.load(open('nbrs.pkl', 'rb'))
#e = pickle.load(open('oe.pkl', 'rb'))
#mabs = pickle.load(open('mabs.pkl', 'rb'))
   
final_preferences = pd.DataFrame(oe.transform(final_preferences.values), columns = final_preferences.columns)
final_preferences = pd.DataFrame(mabs.transform(final_preferences), columns = final_preferences.columns)
distances, indices = nbrs.kneighbors(final_preferences.values)
indices = indices.ravel()

import urllib.request
import base64
predictions = data.loc[indices]

for url in predictions['imsgs_url']:
    temp = data.loc[data['imsgs_url']==url,'addresses'].iloc[0]
    img_name = temp + 'output.jpg'
    urllib.request.urlretrieve(url,img_name)

from os import listdir

path = '/Users/Emin/GitHub/AgoraAI/src/scratch'
files = listdir(path)
images_list = [i for i in files if i.endswith('output.jpg')] 
encoded_image_predict = []
item_in_df = []
for img in images_list:
    encoded_image_predict.append(base64.b64encode(open(img, 'rb').read()))
    item_in_df.append(img)


'''

with open('nbrs.pkl','wb') as f:
    pickle.dump(nbrs,f)

with open('oe.pkl','wb') as f:
    pickle.dump(oe,f)
    
with open('mabs.pkl', 'wb') as f:
    pickle.dump(mabs, f)

'''    


#nbrs = pickle.load(open('nbrs.pkl', 'rb'))
#oe = pickle.load(open('oe.pkl', 'rb'))
#abs = pickle.load(open('mabs.pkl', 'rb'))

