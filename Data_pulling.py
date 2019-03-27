#import packages
import requests
import json
import pandas as pd
import datetime as dt
from uszipcode import SearchEngine
import time
import osmnx as ox

#cities and corresponding latitude/longitude coordinates
cities = [('Austin', 30.26715, -97.74306), 
          ('Atlanta', 33.753746, -84.386330),
          ('DC', 38.89511, -77.03637),
          ('Indianapolis', 39.7685, -86.159),
          ('Santa Monica', 34.024212, -118.496475)]

# reverse engineering access to Bird Scooter API-- need to 'create' new email address to get a new token
# every time we run the script
login = {"email": "ernieels69@gmail.com"}
headers = {"Device-id": "123E4567-E89B-12D3-A456-426655440060", "Platform": "ios", "Content-Type": "application/json"}
response = requests.post('https://api.bird.co/user/login', json=login, headers=headers)
login = json.loads(response.text)

token = login["token"]

token = token

data = pd.DataFrame([])

#loop through city and corresponding coordinates to create df from Bird API pull
for city in cities:
    lat = city[1]
    lon = city[2]
    headers2 = {"Authorization": 'Bird' + ' ' + token,
            "Device-id": "123E4567-E89B-12D3-A456-426655440060",
            "App-Version": "3.0.5",
            "Location": json.dumps({"latitude":lat,"longitude":lon})}
    results = requests.get("https://api.bird.co/bird/nearby?latitude="+str(lat)+"&longitude="+str(lon)+"&radius=10000", headers = headers2)
    bird_parsed = json.loads(results.text)
    keys = bird_parsed.keys()
    dict_you_want={'my_items':bird_parsed['birds']for key in keys}
    df = pd.DataFrame(dict_you_want)
    df2 = df['my_items'].apply(pd.Series)
    df2 = pd.concat([df2.drop(['location'], axis=1), df2['location'].apply(pd.Series)], axis=1)
    df2['timestamp'] = dt.datetime.now()
    df2['weekday'] = df2['timestamp'].dt.dayofweek
    df2['city'] = city[0]
    data = data.append(df2)
    
# Weather company data API credentials
username=Username
password=Password

location = []
temps = []
precip = []
wspd = []
clds = []
uv_index = []

#loop through city and corresponding coordinates to create df from weather company API pull
for city in cities:
    lat = city[1]
    lon = city[2]
    line='https://'+username+':'+password+'@twcservice.mybluemix.net/api/weather/v1/geocode/'+str(lat)+'/'+str(lon)+'/observations.json?&units=m'
    r=requests.get(line)
    weather = json.loads(r.text)
    location.append(city[0])
    temps.append(weather['observation']['temp'])
    precip.append(weather['observation']['precip_total'])
    wspd.append(weather['observation']['wspd'])
    clds.append(weather['observation']['clds'])
    uv_index.append(weather['observation']['uv_index'])        

weather_df = pd.DataFrame(data = [location, temps, precip, wspd, clds, uv_index]).T
weather_df.columns = ['city', 'temp',
                          'precip', 'wspd', 'clds', 'uv_index']

#merged Bird data and weather data on city.
df = pd.merge(data, weather_df, on='city')


#Reverse geocode zipcode
#free token from locationiq
private_token = private_token 


zip_code = []

### loop through coordinates to find zipcode associated with geolocation
for i in range(len(df['latitude'])):
    url = 'https://us1.locationiq.com/v1/reverse.php?key='+private_token+'&lat='+str(df['latitude'][i])+'&lon='+str(df['longitude'][i])+'&format=json'
    r = requests.get(url)
    data = r.json()
    if 'postcode' in data['address']:
        zip_code.append(data['address']['postcode'])
        print(zip_code[i])
        time.sleep(0.09)
    else:
        zip_code.append(0)
        print(zip_code[i])
        time.sleep(0.09)

#add column to df
df['zip_code'] = zip_code

# parks within 1000 meters of geolocation
park_count = []

# loop through coordinates to find the # parks within 1000 meters of the geolocation
for i in range(len(df['latitude'])):
    count = 0    
    url = 'https://us1.locationiq.com/v1/nearby.php?key='+private_token+'&lat='+str(df['latitude'][i])+'&lon='+str(df['longitude'][i])+'&tag='+'park'+'&radius='+str(1000)+'&format=json'
    r = requests.get(url)
    data = r.json()
    if 'error' in data:
        count = 0
        park_count.append(0)
        print(data)
        print(count)
        time.sleep(0.09)
    else:   
        count = len(data)
        print(data)
        print(count)
        park_count.append(count)
        time.sleep(0.09)

#add column to df
df['park_count'] = park_count

# supermarkets within 1000 meters of geolocation
supermarket_count = []

# loop through geocoordinates to count the number of supermarkets within 1000 meters of geolocation
for i in range(len(df['latitude'])):
    count = 0    
    url = 'https://us1.locationiq.com/v1/nearby.php?key='+private_token+'&lat='+str(df['latitude'][i])+'&lon='+str(df['longitude'][i])+'&tag='+'supermarket'+'&radius='+str(1000)+'&format=json'
    r = requests.get(url)
    data = r.json()
    if 'error' in data:
        count = 0
        supermarket_count.append(0)
        print(data)
        print(count)
        time.sleep(0.09)
    else:   
        count = len(data)
        print(data)
        print(count)
        supermarket_count.append(count)
        time.sleep(0.09)
        
# add to df
df['supermarket_count_1000m'] = supermarket_count

# bus stations within 1000 meter of geolocation
bus_count = []


for i in range(len(df['latitude'])):
    count = 0    
    url = 'https://us1.locationiq.com/v1/nearby.php?key='+private_token+'&lat='+str(df['latitude'][i])+'&lon='+str(df['longitude'][i])+'&tag='+'bus_station'+'&radius='+str(1000)+'&format=json'
    r = requests.get(url)
    data = r.json()
    if 'error' in data:
        count = 0
        bus_count.append(0)
        print(data)
        print(count)
        time.sleep(0.09)
    else:   
        count = len(data)
        print(data)
        print(count)
        bus_count.append(count)
        time.sleep(0.09)

df['bus_count'] = bus_count

# gas stations within 1000 meters of geolocation
fuel_count = []


for i in range(len(df['latitude'])):
    count = 0    
    url = 'https://us1.locationiq.com/v1/nearby.php?key='+private_token+'&lat='+str(df['latitude'][i])+'&lon='+str(df['longitude'][i])+'&tag='+'fuel'+'&radius='+str(1000)+'&format=json'
    r = requests.get(url)
    data = r.json()
    if 'error' in data:
        count = 0
        fuel_count.append(0)
        print(data)
        print(count)
        time.sleep(0.09)
    else:   
        count = len(data)
        print(data)
        print(count)
        fuel_count.append(count)
        time.sleep(0.09)

df['fuel_count'] = fuel_count


#Google cloud api key
apikey = APIKEY 

# elevation in meters for geolocation  
elevation = [] 
   
for i in range(len(df['latitude'])):
    url = 'https://maps.googleapis.com/maps/api/elevation/json?locations='+str(df['latitude'][i])+','+str(df['longitude'][i])+'&key='+apikey
    r = requests.get(url)
    data = r.json()
    elevation.append(data['results'][0]['elevation'])
    print(elevation[i])
    time.sleep(0.5)
    
# elevation is in meters
df['elevation'] = elevation

# tag states
states = []

for city in df['city']:
    if city == 'Austin':
        states.append('TX')
    if city == 'Atlanta':
        states.append('GA')
    if city == 'DC':
        states.append('DC')
    if city == 'Indianapolis':
        states.append('IN')
    if city == 'Santa Monica':
        states.append('CA')
        
df['states'] = states 


# find walk_score and bike_score for each geolocation

walk_score = []
bike_score = []

walk_apikey = APIKEY

for i in range(len(df['latitude'])):
    url = 'http://api.walkscore.com/score?format=json&&lat='+str(df['latitude'][i])+'&lon='+str(df['longitude'][i])+'&transit=1&bike=1&wsapikey='+walk_apikey
    r = requests.get(url)
    data = r.json()
    if 'walkscore' in data:
        walk_score.append(data['walkscore'])
    if 'walkscore' not in data:
        walk_score.append(0)
    if 'bike' in data:
        bike_score.append(data['bike']['score'])
    if 'bike' not in data:
        bike_score.append(0)
        
    print(walk_score[i])   
    print(bike_score[i])

    time.sleep(0.5)    
    
df['walk_score'] = walk_score
df['bike_score'] = bike_score


# find zipcode specific insights
search = SearchEngine(simple_zipcode=True)

radius_in_miles = []
land_area_in_sqmi = []
water_area_in_sqmi = []
pop_density = []
population = []
housing_units = []

for code in df['zip_code']:
    if int(code) > 0:
        zipcode = search.by_zipcode(str(code))
        data = zipcode.to_dict()
        radius_in_miles.append(data['radius_in_miles'])
        land_area_in_sqmi.append(data['land_area_in_sqmi'])
        water_area_in_sqmi.append(data['water_area_in_sqmi'])
        pop_density.append(data['population_density'])
        population.append(data['population'])
        housing_units.append(data['housing_units'])
    else:
        radius_in_miles.append(0)
        land_area_in_sqmi.append(0)
        water_area_in_sqmi.append(0)
        pop_density.append(0)
        population.append(0)
        housing_units.append(0)        

df['radius_in_miles'] = radius_in_miles
df['land_area_in_sqmi'] = land_area_in_sqmi
df['water_area_in_sqmi'] = water_area_in_sqmi
df['pop_density'] = pop_density
df['population'] = population
df['housing_units'] = housing_units

df['point'] = list(zip(df.latitude, df.longitude))

### park count, bar count and bench count within 100 meters of geolocation
parking = []
bar = []
bench = []

for i in range(len(df['latitude'])):
    parking_count = 0
    bar_count = 0
    bench_count = 0
    returned = ox.pois.pois_from_point(df['point'][i], distance=100, amenities='cafe')
    if len(returned) > 0:
        amenities = returned.amenity
        for ID in amenities:
            if ID == 'bar':
                bar_count = bar_count + 1
            if ID == 'parking':
                parking_count = parking_count + 1
            if ID == 'bench':
                bench_count = bench_count + 1 
            
        parking.append(parking_count)
        bar.append(bar_count)
        bench.append(bench_count)
        print(parking_count)
    else:
        parking.append(parking_count)
        bar.append(bar_count)
        bench.append(bench_count) 
        print(parking_count)


df['parking_count'] = parking
df['bar_count'] = bar
df['bench_count'] = bench

# number of intersections in graph, that is, nodes with >1 street emanating from them
intersection_count = []

#how many streets (edges in the undirected representation of the graph) emanate from each node (ie,intersection or dead-end) on average (mean)
streets_per_node_avg = []

# edge_length_total divided by the sum of the great circle distances between the nodes of each edge
circuity_avg = []

# mean edge length in the undirected representation of the graph, in meters
street_length_avg = []


## Street network within 0.25km of the lat-lon point
for i in range(len(df['latitude'])):
    G = ox.graph_from_point((df['latitude'][i], df['longitude'][i]), distance=250, network_type='all')
    stats = ox.basic_stats(G)
    intersection_count.append(stats['intersection_count'])
    streets_per_node_avg.append(stats['streets_per_node_avg'])
    circuity_avg.append(stats['circuity_avg'])
    street_length_avg.append(stats['street_length_avg'])
    print(stats['intersection_count'])
    print(i)
    
df['intersection_count'] = intersection_count
df['streets_per_node_avg'] = streets_per_node_avg
df['circuity_avg'] = circuity_avg
df['street_length_avg'] = street_length_avg  


df.to_csv('master_merged.csv')
