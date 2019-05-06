import dash
import numpy as np
import json
import requests
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import dash_table_experiments as dash_table
import copy 
import plotly.graph_objs as go
from haversine import haversine
from geopy.geocoders import GoogleV3
import uuid
import operator
from sklearn.externals import joblib
from shapely.geometry import  MultiPoint
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from app_functions import *
from rq import Queue
from worker import conn
from utils import count_words_at_url


mapbox_access_token = 'APIKEY'

# Mapping layout
layout = dict(
    autosize=True,
    height=800,
    font=dict(color='#fffcfc'),
    titlefont=dict(color='#fffcfc', size='18'),
    margin=dict(
        l=2,
        r=2,
        b=0,
        t=35
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=12), orientation='h'),
    title='Bird Scooters in the area',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style='light',
        center=dict(
            lon=-118.496475,
            lat=34.024212
        ),
        zoom=13,
        bearing=0,
        pitch=0
    )
)

def empty_map(address_data, lat, lon):
    ''' Create the map layout with address location'''
    address_layout = copy.deepcopy(layout)
    address_layout['mapbox']['center']['lat'] = lat
    address_layout['mapbox']['center']['lon'] = lon
    return {
                "data": [
                                                {
                    "type": "scattermapbox",
                    "lat": list(address_data['my_lat']),
                    "lon": list(address_data['my_lon']),
                    "text": "Your Search Location",
                    "mode": "markers",
                    "name": "Your Search Location",
                    "marker": {
                        "size": 12,
                        "opacity": 0.9,
                        "color": 'orange'
                    }
                }
                                ],
            "layout": address_layout
            }                    
        
        
def map_estimate(address_data, scooters, lat, lon):
    ''' Create the map layout with address location'''
    address_layout = copy.deepcopy(layout)
    address_layout['mapbox']['center']['lat'] = lat
    address_layout['mapbox']['center']['lon'] = lon
    
    if 'nest_dummy' in address_data:
        if scooters == 'id' and len(address_data) > 2:
            address_data = address_data[address_data['nest_dummy'] == 0]
            lat, lon = cluster_algorithm(address_data)
            return {
                "data": [
                        {
                                "type": "scattermapbox",
                                "lat": list(address_data['latitude']),
                                "lon": list(address_data['longitude']),
                                "text": list(address_data['battery_level']),
                                "mode": "markers",
                                "name": "Current non-nest Scooters",
                                "marker": {
                                        "size": 4,
                                        "opacity": 1.00,
                                        "color": 'blue'
                                        }
                                },
                                                {
                    "type": "scattermapbox",
                    "lat": list(address_data['my_lat']),
                    "lon": list(address_data['my_lon']),
                    "text": "Your Search Location",
                    "mode": "markers",
                    "name": "Your Search Location",
                    "marker": {
                        "size": 12,
                        "opacity": 0.9,
                        "color": 'orange'
                    }
                },
                                            {
                    "type": "scattermapbox",
                    "lat": list(lat),
                    "lon": list(lon),
                    "text": "Recommended New Nests",
                    "mode": "markers",
                    "name": "Recommended New Nests",
                    "marker": {
                        "size": 10,
                        "opacity": 0.9,
                        "color": 'green'
                    }
                }
                                ],
            "layout": address_layout
            }
                          
        if scooters == 'nest_id' and len(address_data[address_data['nest_dummy'] == 1]) > 2:
            address_data = address_data[address_data['nest_dummy'] == 1]

            return {
               "data": [
                       {
                               "type": "scattermapbox",
                               "lat": list(address_data['latitude']),
                               "lon": list(address_data['longitude']),
                               "text": list(address_data['battery_level']),
                               "mode": "markers",
                               "name": "Current Nest Scooters",
                               "marker": {
                                       "size": 4,
                                       "opacity": 1.00,
                                       "color": 'red'
                                       }
                               },
                                           {
                    "type": "scattermapbox",
                    "lat": list(address_data['my_lat']),
                    "lon": list(address_data['my_lon']),
                    "text": "Your Search Location",
                    "mode": "markers",
                    "name": "Your Search Location",
                    "marker": {
                        "size": 15,
                        "opacity": 0.9,
                        "color": 'orange'
                    }
                } 
                               ],
            "layout": address_layout
            }

        if scooters == 'all' and len(address_data) > 2:
            return {
               "data": [
                       {
                               "type": "scattermapbox",
                               "lat": list(address_data['latitude']),
                               "lon": list(address_data['longitude']),
                               "text": list(address_data['battery_level']),
                               "mode": "markers",
                               "name": "All Scooters",
                               "marker": {
                                       "size": 4,
                                       "opacity": 1.00,
                                       "color": 'purple'
                                       }
                               },
                                           {
                    "type": "scattermapbox",
                    "lat": list(address_data['my_lat']),
                    "lon": list(address_data['my_lon']),
                    "text": "Your Search Location",
                    "mode": "markers",
                    "name": "Your Search Location",
                    "marker": {
                        "size": 15,
                        "opacity": 0.9,
                        "color": 'orange'
                    }
                }
                               ],
            "layout": address_layout
            }    

    else:
        return {
                "data": [
                                                {
                    "type": "scattermapbox",
                    "lat": list(address_data['my_lat']),
                    "lon": list(address_data['my_lon']),
                    "text": "Your Search Location",
                    "mode": "markers",
                    "name": "Your Search Location",
                    "marker": {
                        "size": 12,
                        "opacity": 0.9,
                        "color": 'orange'
                    }
                }
                                ],
            "layout": address_layout
            }        
                          
app = dash.Dash()

server = app.server

q = Queue(connection=conn)

result = q.enqueue(count_words_at_url, 'http://heroku.com')

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

app.layout = html.Div(
    [
        html.H1("NestGenerator: Predicting Real-time Nest Locations", style={'textAlign': 'center', 'fomtSize':12}),
    
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            options = [
                                {'label': 'All Scooters', 'value': 'all'},   
                                {'label': 'Current Nest Scooters', 'value': 'nest_id'},
                                {'label': 'Current Non-Nest Scooters & Predicted Nest Locations', 'value': 'id'}
                            ],
                            value = 'nest_id',
                            id = 'dropdown-scooters'
                        )
                    ],
                    className='six columns',
                    style={'textAlign': 'center', 'fontSize': 20}
                ),

                dcc.Input(id='input-box', type='text', value='Santa Monica State Beach'),
                html.Button('Submit', id='button', style={'textAlign': 'center', 'fontSize': 18}),
            
            ], style={'textAlign': 'center', 'fontSize': 24}),


        html.Div(
            [
                            dcc.Graph(id='address_map',
                    style={'margin-top': '10'})
            ], className = "six columns"
        ),

        html.Div(
        	[
        		dcc.Markdown(id='output-container-button')
        	], style={'textAlign': 'center', 'fontSize': 24, 'margin-top': '65', 'margin-left': '30'}, 
        	className = 'five columns'
        ),

        html.Div(id='suggestions', children='',
            style={'textAlign': 'center', 'margin-top': '50', 'margin-left': '30'}, 
            className = "five columns"),

        html.Div(
            [
                dash_table.DataTable(
                rows=[{}], # initialise the rows
                id='datatable',
                )
                ],
            style={'textAlign': 'center', 'margin-top': '25', 'margin-left': '35', 'fontSize': 16}, 
            className = "five columns"), 

        html.Div(id='intermediate_value', style={'display': 'none'})
    ]
)

@app.callback(
    dash.dependencies.Output('intermediate_value', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])

def find_bird_nests(n_clicks, value):
	
    ##  Get the lat long of address input  by user
    address = str(value)
    geolocator = GoogleV3(api_key='APIKEY')
    location = geolocator.geocode(address)
    lat, lon = location_edge_case(location)
    
    df = bird_api_ping(lat, lon)
    if 'nest_id' in df and len(df) > 2:
        # calculate number of scooters within 2, 5, 10, 25, 50, and 100 meters of a given scooter for a given time snapshot
        two_meter = []
        five_meter = []
        ten_meter = []
        twentyfive_meter = []
        fifty_meter = []
        hundred_meter = []
        closest_scooter = []
        
        for i in range(len(df)):
            base_lat = df['latitude'][i]
            base_lon = df['longitude'][i]
            hold = haversine_np(base_lon, base_lat, df['longitude'].values, df['latitude'].values)
            cleaned = np.delete(hold, hold.argmin())
                 
            
            min_dist = min([i for i in cleaned])
            closest_scooter.append(min_dist)
            
            two_count = len([i for i in cleaned if i < 2])
            two_meter.append(two_count)
            
            five_count = len([i for i in cleaned if i < 5])
            five_meter.append(five_count)
            
            ten_count = len([i for i in cleaned if i < 10])
            ten_meter.append(ten_count)
            
            twentyfive_count = len([i for i in cleaned if i < 25])
            twentyfive_meter.append(twentyfive_count)
    
            fifty_count = len([i for i in cleaned if i < 50])
            fifty_meter.append(fifty_count)
    
            hundred_count = len([i for i in cleaned if i < 100])
            hundred_meter.append(hundred_count)  

        df['two_meter'] = two_meter  
        df['five_meter'] = five_meter
        df['ten_meter'] = ten_meter
        df['twentyfive_meter'] = twentyfive_meter
        df['fifty_meter'] = fifty_meter
        df['hundred_meter'] = hundred_meter
        df['closest_scooter'] = closest_scooter

      
        # count the number of scooters with battery level >= 95 within a five meter distance for a given snapshot in time
        highest_bat_proximity = []

        for i in range(len(df)):
            base_lat = df['latitude'][i]
            base_lon = df['longitude'][i]
            battery_calc = df[['battery_level', 'longitude', 'latitude']].values
            yes = battery_calc[battery_calc[:, 0] >= 95]

            hold = haversine_np(base_lon, base_lat, yes[:, 1], yes[:, 2])
            cleaned = np.delete(hold, hold.argmin())
    
            five_meters = len([i for i in cleaned if i <=5])
            highest_bat_proximity.append(five_meters)


        df['highest_bat_proximity'] = highest_bat_proximity

        # count the number of scooters with battery level < 60 within a 10 meter distance
        low_bat_proximity = []

        for i in range(len(df)):
            base_lat = df['latitude'][i]
            base_lon = df['longitude'][i]
            battery_calc = df[['battery_level', 'longitude', 'latitude']].values
            yes = battery_calc[battery_calc[:, 0] < 60]
            
            hold = haversine_np(base_lon, base_lat, yes[:, 1], yes[:, 2])
            cleaned = np.delete(hold, hold.argmin())
        
            ten_meters = len([i for i in cleaned if i <=10])
            low_bat_proximity.append(ten_meters)

        df['low_bat_proximity'] = low_bat_proximity
        
        # create log feature for closest scooter
        df['log_scooter'] = np.log(df['closest_scooter'])
        
        X_vars_min = ['log_scooter', 'battery_level', 'fifty_meter', 'two_meter', 
              'ten_meter', 'twentyfive_meter', 'low_bat_proximity',
               'highest_bat_proximity']
        
        X = df[X_vars_min]

        loaded_model = joblib.load('rfc_model.sav')
        
        nest_dummy = loaded_model.predict(X)
        
        df['nest_dummy'] = nest_dummy
        
        return df.to_json(orient='split')
    
    else:

        return df.to_json(orient='split')
    

@app.callback(
    Output('output-container-button', 'children'),
    [Input('intermediate_value', 'children'),
     Input('dropdown-scooters', 'value')])
    
def get_proximity(model_df, scooter):
    
    model_df = pd.read_json(model_df, orient='split')
    
    lat = model_df['my_lat'][0]
    lon = model_df['my_lon'][0]
    
    if lat == 48.445012:
        return('''This is Whitefish, Montana but I don't think you wanted that!
               Please type in an actual location!''')
         
    if 'nest_dummy' not in model_df:
        
        return('''No Scooters in this Area or it's after 9pm local time!''')
             
    if scooter == 'id' and len(model_df[model_df['nest_dummy'] == 0]) > 0:
        model_df = model_df[model_df['nest_dummy'] == 0]
        lat_clust, lon_clust = cluster_algorithm(model_df)
        location = (lat, lon)
        
        if len(lat_clust) >= 1:
            all_dist = []
            for i in range(len(lat_clust)):
                clust_lat = lat_clust[i]
                clust_lon = lon_clust[i]
                all_clust = (clust_lat, clust_lon)
                dist = haversine(location, all_clust)
                all_dist.append(dist)
                
            minimum = min(all_dist)
            minimum = 1000 * minimum         

            return('''The nearest Generated Nest is {0} meters away.'''.format(int(np.round(minimum, 0))))
        else:
            return('''There are no Generated Nests based on current Non-nest Scooter locations.''')

    if scooter == 'id' and len(model_df[model_df['nest_dummy'] == 0]) <= 0:
            return('''There are no Generated Nests based on current Non-nest Scooter locations.''')

    if scooter == 'nest_id' and len(model_df[model_df['nest_dummy'] == 1]) > 0:
        location = (lat, lon)        
        all_dist = []
        for i in range(len(model_df)):
            all_lat = model_df['latitude'][i]
            all_lon = model_df['longitude'][i]
            all_geo = (all_lat, all_lon)
            if model_df['nest_dummy'][i] == 0:
                pass
            else:
                all_dist.append(haversine(location, all_geo))
                
        minimum = min(all_dist)
        minimum = 1000 * minimum
            
        return('''The nearest Nest Scooter is {0} meters away.'''.format(int(np.round(minimum, 0))))            

    if scooter == 'nest_id' and len(model_df[model_df['nest_dummy'] == 1]) <= 0:
        return('''There are no Nest scooters in this area.''')
        
    if scooter == 'all' and len(model_df) > 0:
        location = (lat, lon)
        dist = haversine_np(lon, lat, model_df['longitude'].values, model_df['latitude'].values)
        minimum = min(dist)         
        
        return('''The nearest scooter is {0} meters away.'''.format(int(np.round(minimum, 0))))
     
@app.callback(
    Output('datatable', 'rows'),
    [Input('intermediate_value', 'children'),
     Input('dropdown-scooters', 'value')])

def create_table(model_df, scooters):
    model_df = pd.read_json(model_df, orient='split')
    lat = model_df['my_lat'][0]
    lon = model_df['my_lon'][0]

    if lat == 48.445012:
        
        return('')
        
    if 'nest_dummy' not in model_df:

        return('')
        
    if scooters == 'id' and len(model_df[model_df['nest_dummy'] == 0]) > 0:
        nest_scooters = find_closest_nests(lat, lon, model_df, 'id')
        nest_scooters = pd.DataFrame(nest_scooters)
        nest_scooters = nest_scooters.rename(columns={0: 'Nest Address', 1: 'Meters Away'})
        nest_scooters = nest_scooters.sort_values(['Meters Away'], ascending=True)        
        nest_scooters = nest_scooters.round(0)
        return nest_scooters.to_dict('records')
        
    if scooters == 'nest_id' and len(model_df[model_df['nest_dummy'] == 1]) > 0:      
        nest_scooters = find_closest_nests(lat, lon, model_df, 'nest_id')
        nest_scooters = pd.DataFrame(nest_scooters)
        nest_scooters = nest_scooters.rename(columns={0: 'Distance (Meters)', 1: 'Battery Level'})
        nest_scooters = nest_scooters.sort_values(['Distance (Meters)'], ascending=True)
        nest_scooters = nest_scooters.round(0)

        return nest_scooters.to_dict('records') 
        
    if scooters == 'all' and len(model_df) > 0:
        nest_scooters = find_closest_nests(lat, lon, model_df, 'all')
        nest_scooters = pd.DataFrame(nest_scooters)
        nest_scooters = nest_scooters.rename(columns={0: 'Distance (Meters)', 1: 'Battery Level'})
        nest_scooters = nest_scooters.sort_values(['Distance (Meters)'], ascending=True)
        nest_scooters = nest_scooters.round(0)

        return nest_scooters.to_dict('records')
    
    else:
        return('')
    
@app.callback(
        Output('address_map', 'figure'),
        [Input('intermediate_value', 'children'),
         Input('dropdown-scooters', 'value')])

def location_map(address_df, scooters):
    address_df = pd.read_json(address_df, orient='split')
    
    lat = address_df['my_lat'][0]
    lon = address_df['my_lon'][0]
    
    if len(address_df) <= 2:
        address_map = empty_map(address_df, lat, lon)
        
        return  address_map
        
    if scooters == 'id':
        address_map = map_estimate(address_df, 'id', lat, lon)
        return address_map
    
    if scooters == 'nest_id':
        address_map = map_estimate(address_df, 'nest_id', lat, lon)
        return address_map

    if scooters == 'all':
        address_map = map_estimate(address_df, 'all', lat, lon)
        return address_map 
    


if __name__ == '__main__':
    app.run_server()
