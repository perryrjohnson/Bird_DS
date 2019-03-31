#import packages
import requests
import json
import pandas as pd
import datetime as dt

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
