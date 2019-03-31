#import packages
import requests
import json
import pandas as pd
import time

# import dataframe

df = pd.read_csv('data.csv, index_col=0')


#locationiq_reverse geocode zipcode
#free token
private_token = "API KEY" 

zip_code = []
### 'postcode' not found in address so append sometimes doesn't work
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

df['zip_code'] = zip_code

# parks within 1000 meters of geolocation
park_count = []

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

df['park_count'] = park_count

# supermarkets within 1000 meters of geolocation
supermarket_count = []


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
