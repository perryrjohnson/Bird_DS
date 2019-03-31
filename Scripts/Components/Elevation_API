#import packages
import requests
import json
import pandas as pd
import time


#import df

df = pd.read_csv('data.csv', index_col=0')

#Google cloud api key
apikey = 'APIKEY' 

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
