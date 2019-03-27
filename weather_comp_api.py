import requests
import json
import numpy as np
import pandas as pd
import datetime as dt

# Weather company data API credentials
username="UserName"
password="Password"
 
cities = [('Austin', 30.266926, -97.750519), 
          ('Atlanta', 33.753746, -84.386330),
          ('DC', 38.889484, -77.035278),
          ('Indianapolis', 39.832081, -86.145454),
          ('Santa Monica', 34.024212, -118.496475)]

temps = []
precip = []
wspd = []
location = []
clds = []
uv_index = []

for city in cities:
    lat = city[1]
    lon = city[2]
    line='https://'+username+':'+password+'@twcservice.mybluemix.net/api/weather/v1/geocode/'+str(lat)+'/'+str(lon)+'/observations.json?&units=m'
    r=requests.get(line)
    weather = json.loads(r.text)
    location = np.append(location, city[0])
    temps = np.append(temps,weather['observation']['temp'])
    precip = np.append(precip, weather['observation']['precip_total'])
    wspd = np.append(wspd, weather['observation']['wspd'])
    clds = np.append(clds, weather['observation']['clds'])
    uv_index = np.append(uv_index, weather['observation']['uv_index'])
  
   
dataset = pd.DataFrame(data = [location, temps, precip, wspd, clds, uv_index]).T


dataset = dataset.rename(columns={0: "city", 1: "temp", 2: 'precip', 3 : 'wspd', 4 : 'clds', 5: 'uv_index'})

dataset['timestamp'] = dt.datetime.now()

dataset.to_csv('weather.csv')
