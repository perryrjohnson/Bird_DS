import pandas as pd
import json
import requests

df = pd.read_csv('data.csv', index_col=0)

# find walk_score and bike_score for each geolocation

# set empty walk_score list
walk_score = []
bike_score = []
apikey = 'APIKEY'


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


    time.sleep(0.5)    
    
df['walk_score'] = walk_score
df['bike_score'] = bike_score
    


df.to_csv('new_walk.csv')
