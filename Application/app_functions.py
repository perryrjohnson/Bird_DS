import numpy as np
import json
import requests
import pandas as pd
from haversine import haversine
import uuid
import operator
from shapely.geometry import  MultiPoint
from sklearn.cluster import DBSCAN


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
    results = requests.get("https://api.bird.co/bird/nearby?latitude="+str(lat)+"&longitude="+str(lon)+"&radius=1", headers = headers2)
    bird_parsed = json.loads(results.text)
    keys = bird_parsed.keys()
    dict_you_want={'my_items':bird_parsed['birds']for key in keys}
    df = pd.DataFrame(dict_you_want)
    if len(df) > 0:
        df = df['my_items'].apply(pd.Series)
        df = pd.concat([df.drop(['location'], axis=1), df['location'].apply(pd.Series)], axis=1)
        df['my_lat'] = lat
        df['my_lon'] = lon
    else:
        df = pd.DataFrame([[lat,lon]], columns=['my_lat', 'my_lon'])
    return df

def get_centroid(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    return list(centroid)

def cluster_algorithm(df):
    
    coords = df[['latitude', 'longitude']].values

    # eps is the physical distance from each point that forms its neighborhood
    # points must be within 25 meters of each other and a cluster must contain at least 4 points.
    eps_rad = 50 / 3671000

    db = DBSCAN(eps=eps_rad, min_samples=4, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))

    cluster_labels = db.labels_
    
    clusters = pd.Series([coords[cluster_labels==n] for n in range(min(cluster_labels), max(cluster_labels))])

    clust_lat = []
    clust_lon = []
    for i in range(len(clusters)):
        centroid_point = get_centroid(clusters[i])
        lat, lon = centroid_point
        clust_lat.append(lat)
        clust_lon.append(lon)
        
    return clust_lat, clust_lon     

def cluster_address(df):
    # reverse geocode to get the address for the cluster centroid
    address = []
    api_key='APIKEY'
    lat, lon = cluster_algorithm(df)
    for i in range(len(lat)):
        url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng='+str(lat[i])+','+str(lon[i])+'&key='+api_key
        r = requests.get(url)
        data = r.json()  
        address.append(data['results'][0]['formatted_address'])
    
    return address

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.    

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c

    m = km * 1000
     
    return m     
 
def location_edge_case(location):
    if location is None:
        lat = 48.445012
        lon = -114.360542
        
        return lat, lon
    else:
        lat = float(location[1][0])
        lon = float(location[1][1])
        
        return lat, lon
        
def find_closest_nests(lat, lon, df, scooters):
    # calculate the closest nest proximity for a non nest scooter in meters at a snapshot in time      
    location = (lat, lon)
   
    if scooters == 'id':        
        df = df[df['nest_dummy'] == 0]
        lat_clust, lon_clust = cluster_algorithm(df)
        all_dist = []
        lon = df['longitude'].values
        lat = df['latitude'].values
        
        for i in range(len(lat_clust)):
            clust_lat = lat_clust[i]
            clust_lon = lon_clust[i]
            all_clust = (clust_lat, clust_lon)
            dist = haversine(location, all_clust)
            dist = dist * 1000
            all_dist.append(dist)
            
        all_dist.sort(reverse=False)
        if len(all_dist) > 5:
            top_five = all_dist[0:5]
            return top_five
        else:
            return all_dist

    if scooters == 'nest_id':      
        all_dist = []       
        for i in range(len(df)):
            all_lat = df['latitude'][i]
            all_lon = df['longitude'][i]
            all_geo = (all_lat, all_lon)
            if df['nest_dummy'][i] == 0:
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
