import dash
import numpy as np
import json
import requests
import datetime as dt
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

mapbox_access_token = 'pk.eyJ1IjoicHJqMDciLCJhIjoiY2p1N2l6ZnlnMHR1YzRlazlsZXJhbm1zZCJ9.G770typ9b-pygTLkxRoa7Q'


def bird_api_ping(lat, lon):
    # reverse engineering access to Bird Scooter API-- need to 'create' new email address to get a new token
    # every time we run the script
    lowercase_str = uuid.uuid4().hex
    login = {"email": lowercase_str+"@gmail.com"}
    headers = {"Device-id": "123E4567-E89B-12D3-A456-426655440060", "Platform": "ios", "Content-Type": "application/json"}
    response = requests.post('https://api.bird.co/user/login', json=login, headers=headers)
    login = json.loads(response.text)

    token = login["token"]

    headers2 = {"Authorization": 'Bird' + ' ' + token,
            "Device-id": "123E4567-E89B-12D3-A456-426655440060",
            "App-Version": "3.0.5",
            "Location": json.dumps({"latitude":lat,"longitude":lon})}
    results = requests.get("https://api.bird.co/bird/nearby?latitude="+str(lat)+"&longitude="+str(lon)+"&radius=100000", headers = headers2)
    bird_parsed = json.loads(results.text)
    keys = bird_parsed.keys()
    dict_you_want={'my_items':bird_parsed['birds']for key in keys}
    df = pd.DataFrame(dict_you_want)
    if len(df) > 0:
        df = df['my_items'].apply(pd.Series)
        df = pd.concat([df.drop(['location'], axis=1), df['location'].apply(pd.Series)], axis=1)
        df['timestamp'] = dt.datetime.now()
        df['weekday'] = df['timestamp'].dt.dayofweek
    else:
        df
    
    return df

def find_closest_nests(lat, lon, df, scooters):
    # calculate the closest nest proximity for a non nest scooter in meters at a snapshot in time      
    location = (lat, lon)

    
    if scooters == 'id':        
        all_dist = []
        for i in range(len(df)):
            all_lat = df['latitude'][i]
            all_lon = df['longitude'][i]
            all_geo = (all_lat, all_lon)
            if df['battery_level'][i] <= 90:
                pass
            else:
                dist = haversine(location, all_geo)
                dist = dist * 1000
                bat = df['battery_level'][i]
                nest = [dist, bat]
                all_dist.append(nest)
                
        all_dist.sort(key=operator.itemgetter(0))
        top_five = all_dist[0:5]
    
        return top_five

    if scooters == 'nest_id':
        all_dist = []       
        for i in range(len(df)):
            all_lat = df['latitude'][i]
            all_lon = df['longitude'][i]
            all_geo = (all_lat, all_lon)
            if df['battery_level'][i] > 90:
                pass
            else:
                dist = haversine(location, all_geo)
                dist = dist * 1000
                bat = df['battery_level'][i]
                nest = [dist, bat]
                all_dist.append(nest)
                
        all_dist.sort(key=operator.itemgetter(0))
        top_five = all_dist[0:5]
    
        return top_five

    if scooters == 'all':
        all_dist = []
        for i in range(len(df)):
            all_lat = df['latitude'][i]
            all_lon = df['longitude'][i]
            all_geo = (all_lat, all_lon)
            dist = haversine(location, all_geo)
            dist = dist * 1000
            bat = df['battery_level'][i]
            nest = [dist, bat]
            all_dist.append(nest)
                
        all_dist.sort(key=operator.itemgetter(0))
        top_five = all_dist[0:5]
    
        return top_five

# Mapping layout
layout = dict(
    autosize=True,
    height=800,
    font=dict(color='#fffcfc'),
    titlefont=dict(color='#fffcfc', size='18'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor="#191A1A",
    paper_bgcolor="#020202",
    legend=dict(font=dict(size=16), orientation='h'),
    title='Bird Scooters in the city',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="dark",
        center=dict(
            lon=-118.496475,
            lat=34.024212
        ),
        zoom=13,
    )
)
        
def map_estimate(address_data, scooters, lat, lon):
    ''' Create the map layout with address location and underlying heatmap of pollutants'''
    address_layout = copy.deepcopy(layout)
    address_layout['mapbox']['center']['lat'] = lat
    address_layout['mapbox']['center']['lon'] = lon

    if scooters == 'id':
        address_data = address_data[address_data['battery_level'] > 90]

        return {
                "data": [
                        {
                                "type": "scattermapbox",
                                "lat": list(address_data['latitude']),
                                "lon": list(address_data['longitude']),
                                "text": list(address_data['battery_level']),
                                "mode": "markers",
                                "name": "City",
                                "marker": {
                                        "size": 4,
                                        "opacity": 1.00,
                                        "color": 'green'
                                        }
                                }
                                ],
            "layout": address_layout
            }
        
    if scooters == 'nest_id':
       address_data = address_data[address_data['battery_level'] <= 90]

       return {
               "data": [
                       {
                               "type": "scattermapbox",
                               "lat": list(address_data['latitude']),
                               "lon": list(address_data['longitude']),
                               "text": list(address_data['battery_level']),
                               "mode": "markers",
                               "name": "City",
                               "marker": {
                                       "size": 4,
                                       "opacity": 1.00,
                                       "color": 'red'
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
                               "lat": list(address_data['latitude']),
                               "lon": list(address_data['longitude']),
                               "text": list(address_data['battery_level']),
                               "mode": "markers",
                               "name": "City",
                               "marker": {
                                       "size": 4,
                                       "opacity": 1.00,
                                       "color": 'yellow'
                                       }
                               }
                               ],
            "layout": address_layout
            }    
                
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash()

server = app.server

"""data = [go.Scattermapbox(lat=df['latitude'], lon=df['longitude'], mode='markers', marker=go.scattermapbox.Marker(
        size=9
        ), text=df['id'])]"""

layout = go.Layout(autosize=True, height=800, width =600,
                   hovermode='closest', 
                   mapbox=dict(
        accesstoken = mapbox_access_token,
        style="dark",
        center=dict(lat=34.024212, lon=-118.496475),
        zoom=12))

"""fig = dict(data=data, layout=layout)"""

app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501
app.layout = html.Div(
    [
        html.H1("Real-time Electric Scooters and Nests", style={'textAlign': 'center'}),
    
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            options = [
                                {'label': 'All Scooters', 'value': 'all'},   
                                {'label': 'Nest Scooters', 'value': 'nest_id'},
                                {'label': 'Non-nest Scooters', 'value': 'id'}
                            ],
                            value = 'nest_id',
                            id = 'dropdown-scooters'
                        )
                    ],
                    className='six columns',
                    style={'textAlign': 'center', 'fontSize': 20}
                ),

                dcc.Input(id='input-box', type='text', value='3100 Main St, Santa Monica'),
                html.Button('Submit', id='button', style={'textAlign': 'center', 'fontSize': 18}),
            
            ], style={'textAlign': 'center', 'fontSize': 24}),


        html.Div(
            [
                dcc.Graph(id='address_map',
                          #figure = fig,
                    style={'margin-top': '10'})
            ], className = "six columns"
        ),

        html.Div(
        	[
        		dcc.Markdown(id='output-container-button')
        	], style={'textAlign': 'center', 'fontSize': 36, 'margin-top': '65', 'margin-left': '30'}, 
        	className = 'five columns'
        ),

        html.Div(id='suggestions', children='',
            style={'textAlign': 'center', 'margin-top': '50', 'margin-left': '30'}, 
            className = "five columns"),

        html.Div(
            [
                dash_table.DataTable(
                rows=[{}], # initialise the rows
                id='datatable'
                )   
            ], style={'textAlign': 'center', 'margin-top': '25', 'margin-left': '30', 'fontSize': 18}, 
            className = "five columns"),

        html.Div(id='intermediate_value', style={'display': 'none'})
    ]
)

@app.callback(
    dash.dependencies.Output('intermediate_value', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])

def find_bird_nests(n_clicks, value):
	
    ## A. Get the lat long of address input  by user
    address = str(value)
    geolocator = GoogleV3(api_key='AIzaSyBZLOJfP1yw-F5T26O_nNcjXpceL6KrD3Q')
    location = geolocator.geocode(address) # contains full address and lat long data
    lat = float(location[1][0])
    lon = float(location[1][1])   
    df = bird_api_ping(lat, lon)
    if len(df) > 0:
        df['my_lat'] = lat
        df['my_lon'] = lon

        return df.to_json(orient='split')    
    else:
        return df.to_json(orient='split')
    

@app.callback(
    Output('output-container-button', 'children'),
    [Input('intermediate_value', 'children'),
     Input('dropdown-scooters', 'value')])
    
def get_proximity(model_df, scooter):

    model_df = pd.read_json(model_df, orient='split')
    
    if len(model_df) < 1:
        return("No Scooters in this Area or it's after 9pm local time!") 
        
    else:
        lat = model_df['my_lat'][0]
        lon = model_df['my_lon'][0]
        location = (lat, lon)
        all_dist = []
        for i in range(len(model_df)):
            all_lat = model_df['latitude'][i]
            all_lon = model_df['longitude'][i]
            all_geo = (all_lat, all_lon)
            if location == all_geo:
                pass
            else:
                all_dist.append(haversine(location, all_geo))
                
        minimum = min(all_dist)
        minimum = 1000 * minimum


        if scooter == 'id':
            return('''The nearest scooter is {0} meters away.'''.format(np.round(minimum, 0)))
            
        if scooter == 'all':
            return('''The nearest all scooter is {0} meters away.'''.format(np.round(minimum, 0)))            
        
        else:
            return('''The nearest Nest is {0} meters away.'''.format(np.round(minimum, 0)))


@app.callback(
	Output('suggestions', 'children'),
	[Input('intermediate_value', 'children')])

def create_suggestions(model_df):
    model_df = pd.read_json(model_df, orient='split')
    if len(model_df) < 1:
        out_of_range = html.Div([
                            html.P("There are no Nests at the time", style = {'fontSize': 32})
                            ])
        return out_of_range
    
    if len(model_df) >= 1:
        out_of_range = html.Div([
                            html.P("These are the five closest scooters from your specified location", 
                                   style = {'fontSize': 28})
                            ])
        return out_of_range


@app.callback(
    Output('datatable', 'rows'),
    [Input('intermediate_value', 'children'),
     Input('dropdown-scooters', 'value')])

def create_table(model_df, scooters):
    model_df = pd.read_json(model_df, orient='split')
    lat = model_df['my_lat'][0]
    lon = model_df['my_lon'][0]
    
    if len(model_df) < 1:
        
        return('')
        
    if scooters == 'id':
        nest_scooters = find_closest_nests(lat, lon, model_df, 'id')
        nest_scooters = pd.DataFrame(nest_scooters)
        nest_scooters = nest_scooters.rename(columns={0: 'Distance (Meters)', 1: 'Battery Level'})
        nest_scooters = nest_scooters.sort_values(['Distance (Meters)'], ascending=True)
        nest_scooters = nest_scooters.round(0)

        return nest_scooters.to_dict('records')

    if scooters == 'nest_id':
        nest_scooters = find_closest_nests(lat, lon, model_df, 'nest_id')
        nest_scooters = pd.DataFrame(nest_scooters)
        nest_scooters = nest_scooters.rename(columns={0: 'Distance (Meters)', 1: 'Battery Level'})
        nest_scooters = nest_scooters.sort_values(['Distance (Meters)'], ascending=True)
        nest_scooters = nest_scooters.round(0)

        return nest_scooters.to_dict('records') 
    
    if scooters == 'all':
        nest_scooters = find_closest_nests(lat, lon, model_df, 'all')
        nest_scooters = pd.DataFrame(nest_scooters)
        nest_scooters = nest_scooters.rename(columns={0: 'Distance (Meters)', 1: 'Battery Level'})
        nest_scooters = nest_scooters.sort_values(['Distance (Meters)'], ascending=True)
        nest_scooters = nest_scooters.round(0)

        return nest_scooters.to_dict('records')
    
@app.callback(
        Output('address_map', 'figure'),
        [Input('intermediate_value', 'children'),
         Input('dropdown-scooters', 'value')])

def location_map(address_df, scooters):
    address_df = pd.read_json(address_df, orient='split')

    if len(address_df) < 1:
        return('')
    
    if scooters == 'id':
        address_map = map_estimate(address_df, 'id', lat = address_df.loc[0, 'latitude'], 
                               lon=address_df.loc[0, 'longitude'])
        return address_map
    
    if scooters == 'nest_id':
        address_map = map_estimate(address_df, 'nest_id', lat = address_df.loc[0, 'latitude'], 
                               lon=address_df.loc[0, 'longitude'])
        return address_map

    if scooters == 'all':
        address_map = map_estimate(address_df, 'all', lat = address_df.loc[0, 'latitude'], 
                               lon=address_df.loc[0, 'longitude'])
        return address_map  

if __name__ == '__main__':
    app.run_server()
