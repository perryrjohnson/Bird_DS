import pandas as pd
import json
import requests

df = pd.read_csv('new_states.csv', index_col=0)

# set empty walk_score list
walk_score = []

apikey = '719e7a58daf25647275ff58942226b56'





for i in range(len(df['latitude'])):
    url = 'http://api.walkscore.com/score?format=json&lat='+str(df['latitude'][i])+'&lon='+str(df['longitude'][i])+'&wsapikey='+apikey
    r = requests.get(url)
    data = r.json()
    walk_score.append(data['walkscore'])
    
    

df['walk_score'] = walk_score

df.to_csv('new_walk.csv')




