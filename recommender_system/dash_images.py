import json
import os
import pandas as pd
import random
import glob 
from os import listdir
import flask
import pickle
import base64
from PIL import Image as PImage
import urllib.request


import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

path = '/Users/Emin/GitHub/AgoraAI/src'
'''
files = listdir(path)
images_list = [i for i in files if i.endswith('.png')] ## output file names only
encoded_image = []

for img in images_list:
    encoded_image.append(base64.b64encode(open(img, 'rb').read()))

encoded_images_jpg = []
images_list_jpg = [i for i in files if i.endswith('.jpg')] ## output file names only
for img in images_list_jpg:
    encoded_images_jpg.append(base64.b64encode(open(img, 'rb').read()))
'''
data = pd.read_csv('data_dash.csv')
data.drop(['sqft', 'property types'],inplace=True,axis=1)
data.dropna(axis=0, inplace=True) 

preferences = pd.DataFrame(columns=list(data))
preferences.to_csv('prefs.csv', index=False)
for url in data['imsgs_url']:
    temp = data.loc[data['imsgs_url']==url,'addresses'].iloc[0]
    img_name = temp + '.jpg'
    urllib.request.urlretrieve(url,img_name)
        
path = '/Users/Emin/GitHub/AgoraAI/src'
files = listdir(path)
images_list = [i for i in files if i.endswith('.jpg')] 
images_list = [i for i in images_list if 'output' not in i]

encoded_image = []
item_in_df = []
random.shuffle(images_list)
for img in images_list:
    encoded_image.append(base64.b64encode(open(img, 'rb').read()))
    item_in_df.append(img)


row_1 = html.Div([(dbc.Row([
                            dbc.Col([
                                html.Img(src='data:image/png;base64,{}'.format(encoded_image[0].decode()),
                                style={'width': '100px', 'height': '100px'}),
                                html.P('Address is {}'.format(item_in_df[0])),
                                dbc.Button('Like This One', id='like_val_0', style={'vertical-align': "bottom"}, n_clicks=0),
                            ]),
                            dbc.Col([
                                html.Img(src='data:image/png;base64,{}'.format(encoded_image[1].decode()),
                                style={'width': '100px', 'height': '100px'}),
                                html.P('Address is {}'.format(item_in_df[1])),
                                dbc.Button('Like This One', id='like_val_1', style={'vertical-align': "bottom"}, n_clicks=0),
                            ]),
                            dbc.Col([
                                html.Img(src='data:image/png;base64,{}'.format(encoded_image[2].decode()),
                                style={'width': '100px', 'height': '100px'}),
                                html.P('Address is {}'.format(item_in_df[2])),
                                dbc.Button('Like This One', id='like_val_2', style={'vertical-align': "bottom"}, n_clicks=0),
                            ])
                ]))])

row_2 = html.Div([(dbc.Row([
                             dbc.Col([
                                html.Img(src='data:image/png;base64,{}'.format(encoded_image[3].decode()),
                                style={'width': '100px', 'height': '100px'}),
                                html.P('Address is {}'.format(item_in_df[3])),
                                dbc.Button('Like This One', id='like_val_3', style={'vertical-align': "bottom"}),
                        ]),
                            dbc.Col([
                                html.Img(src='data:image/png;base64,{}'.format(encoded_image[4].decode()),
                                style={'width': '100px', 'height': '100px'}),
                                html.P('Address is {}'.format(item_in_df[4])),
                                dbc.Button('Like This One', id='like_val_4', style={'vertical-align': "bottom"}),
                        ]),
                            dbc.Col([
                                html.Img(src='data:image/png;base64,{}'.format(encoded_image[5].decode()),
                                style={'width': '100px', 'height': '100px'}),
                                html.P('Address is {}'.format(item_in_df[5])),
                                dbc.Button('Like This One', id='like_val_5', style={'vertical-align': "bottom"}),
                        ])
                ]))])

predict =  html.Div([
                    html.Button ('Predict', id='predict_val', n_clicks=0), # color = 'primary', className='mr-1'
                    html.Div(id='images_new')  
                ])
container_out = html.Div([html.Div(id='container')])
placeholder = html.Div([html.Div(id='intermediate_value', style={'display': 'none'})])                

                          
app.layout = dbc.Container(children=[row_1, html.Br(), row_2, html.Br(), placeholder, html.Br(), container_out, html.Br(), predict])

@app.callback(Output('intermediate_value', 'children'), #container (intermediate_value), children
            [#Input('predict_val', 'n_clicks'),
            Input('like_val_0', 'n_clicks_timestamp'),
            Input('like_val_1','n_clicks_timestamp'),
            Input('like_val_2', 'n_clicks_timestamp'), 
            Input('like_val_3', 'n_clicks_timestamp'),
            Input('like_val_4','n_clicks_timestamp'),
            Input('like_val_5', 'n_clicks_timestamp'), 
            ])

def construct_preferences(like_val_0,like_val_1, like_val_2, like_val_3, like_val_4, like_val_5):
    listedTimestamps = [like_val_0, like_val_1, like_val_2, like_val_3, like_val_4, like_val_5]
    listedTimestamps = [0 if v is None else v for v in listedTimestamps]
    sortedTimestamps = sorted(listedTimestamps)
    
    '''
    #delete csv file if it exists
    filename = os.path.expanduser('~') + '/GitHub/AgoraAI/src/prefs.csv'
    try:
        os.remove(filename)
    except OSError:
        #create a file with prefs.csv
        f = open('prefs.csv', 'x')
    '''

    if like_val_0 == sortedTimestamps[-1]:
        pickedButton = "like_val_0"
        print (pickedButton)
        sample_that_matches_address_0 = data[data['addresses'].str.contains(item_in_df[0].partition('.jpg')[0])]
        sample_that_matches_address_0.to_csv('prefs.csv', columns=list(data), mode='a', header=False)
        
    if like_val_1 == sortedTimestamps[-1]:
        pickedButton = "like_val_1"
        print (pickedButton)
        sample_that_matches_address_1 = data[data['addresses'].str.contains(item_in_df[1].partition('.jpg')[0])]
        sample_that_matches_address_1.to_csv('prefs.csv', columns=list(data), mode='a', header=False)
        
    if like_val_2 == sortedTimestamps[-1]:
        pickedButton = "like_val_2"
        print (pickedButton)
        sample_that_matches_address_2 = data[data['addresses'].str.contains(item_in_df[2].partition('.jpg')[0])]
        sample_that_matches_address_2.to_csv('prefs.csv', columns=list(data), mode='a', header=False)

    if like_val_3 == sortedTimestamps[-1]:
        pickedButton = "like_val_3"
        print (pickedButton)
        sample_that_matches_address_2 = data[data['addresses'].str.contains(item_in_df[3].partition('.jpg')[0])]
        sample_that_matches_address_2.to_csv('prefs.csv', columns=list(data), mode='a', header=False)

    if like_val_4 == sortedTimestamps[-1]:
        pickedButton = "like_val_4"
        print (pickedButton)
        sample_that_matches_address_2 = data[data['addresses'].str.contains(item_in_df[4].partition('.jpg')[0])]
        sample_that_matches_address_2.to_csv('prefs.csv', columns=list(data), mode='a', header=False)

    if like_val_5 == sortedTimestamps[-1]:
        pickedButton = "like_val_5"
        print (pickedButton)
        sample_that_matches_address_2 = data[data['addresses'].str.contains(item_in_df[5].partition('.jpg')[0])]
        sample_that_matches_address_2.to_csv('prefs.csv', columns=list(data), mode='a', header=False)        


        
@app.callback(Output('container', 'children'), 
            [Input('intermediate_value', 'children'),
            Input('predict_val', 'n_clicks')])
def update_output_images (intermediate_value, n_clicks):
    if (n_clicks!=0):
        
        preferences = pd.read_csv('prefs.csv')
        preferences.drop_duplicates(keep='first', inplace=True)
        temp = pd.DataFrame(columns=list(data))
        for counter, value in enumerate(preferences.iterrows()):
            temp.loc[counter] = data.loc[value[0]]

        final_preferences = temp.copy()
        print (preferences.shape)
        nbrs = pickle.load(open('nbrs.pkl', 'rb'))
        oe = pickle.load(open('oe.pkl', 'rb'))
        mabs = pickle.load(open('mabs.pkl', 'rb'))

        final_preferences = pd.DataFrame(oe.transform(final_preferences.values), columns = final_preferences.columns)
        final_preferences = pd.DataFrame(mabs.transform(final_preferences), columns = final_preferences.columns)
        distances, indices = nbrs.kneighbors(final_preferences.values)
        indices = indices.ravel()

        
        predictions = data.loc[indices]
        for url in predictions['imsgs_url']:
            temp = data.loc[data['imsgs_url']==url,'addresses'].iloc[0]
            img_name = temp + 'output.jpg'
            urllib.request.urlretrieve(url,img_name)
        images_list = [i for i in files if i.endswith('output.jpg')] 
        encoded_image_predict = []
        item_in_df_predict = []
        for img in images_list:
            encoded_image_predict.append(base64.b64encode(open(img, 'rb').read()))
            item_in_df_predict.append(img)
    
    
    
        row_1 = html.Div([(dbc.Row([
                                dbc.Col([
                                    html.Img(src='data:image/png;base64,{}'.format(encoded_image_predict[0].decode()),
                                    style={'width': '100px', 'height': '100px'}),
                                    html.P('Address is {}'.format(item_in_df_predict[0])),
                                    dbc.Button('Like This One', id='like_val_0', style={'vertical-align': "bottom"}, n_clicks=0),
                                ]),
                                dbc.Col([
                                    html.Img(src='data:image/png;base64,{}'.format(encoded_image_predict[1].decode()),
                                    style={'width': '100px', 'height': '100px'}),
                                    html.P('Address is {}'.format(item_in_df_predict[1])),
                                    dbc.Button('Like This One', id='like_val_1', style={'vertical-align': "bottom"}, n_clicks=0),
                                ]),
                                dbc.Col([
                                    html.Img(src='data:image/png;base64,{}'.format(encoded_image_predict[2].decode()),
                                    style={'width': '100px', 'height': '100px'}),
                                    html.P('Address is {}'.format(item_in_df_predict[2])),
                                    dbc.Button('Like This One', id='like_val_2', style={'vertical-align': "bottom"}, n_clicks=0),
                                ])
                    ]))])
        filename = os.path.expanduser('~') + '/GitHub/AgoraAI/src/prefs.csv'
        f = open(filename, 'w')
        f.truncate()
        f.close()
        
        return html.Div(row_1)
        
    
                
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)



