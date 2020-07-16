import pandas as pd
import numpy as np
import pickle
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MaxAbsScaler, OrdinalEncoder 
import load_transform as lt

def training_stage ():
    data = lt.transform_loaded_data()
    oe = OrdinalEncoder()
    data = pd.DataFrame(oe.fit_transform(data), columns=data.columns)
    
    mabs = MaxAbsScaler()
    data = pd.DataFrame(mabs.fit_transform(data), columns = data.columns)
    
    nbrs= NearestNeighbors(n_neighbors=1, metric='cosine')
    nbrs.fit(data)
    
    with open('nbrs.pkl','wb') as f:
        pickle.dump(nbrs,f)
    
    with open('oe.pkl','wb') as f:
        pickle.dump(oe,f)
        
    with open('mabs.pkl', 'wb') as f:
        pickle.dump(mabs, f)

training_stage()    
''' 
The result of this training will be passed to the actual dashboard.img, where 
preferences will be constructed based on likes 
'''
    

