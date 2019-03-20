import folium
from folium.plugins import MarkerCluster
import pandas as pd
import numpy as np

city = ['Santa Monica', 34.024212, -118.496475] 
lat = city[1]
lon = city[2]
austin_coords = [lat, lon]
my_map = folium.Map(location = austin_coords, zoom_start = 13)


df = pd.read_csv('LA_0.csv', index_col=0)

df.head()


df['latlon'] = list(zip(df.latitude, df.longitude))

bat_color = []

for level in df['battery_level']:
    if level >= 50:
        bat_color.append('green')
    if level < 50:
        bat_color.append('red')
df['bat_color'] = bat_color

for i in range(0,len(df)):
    folium.Marker([df.iloc[i]['latitude'], df.iloc[i]['longitude']], popup=df.iloc[i]['id'], icon=folium.Icon(color=df.iloc[i]['bat_color'])).add_to(my_map)

my_map


my_map.save('Washington, DC Bird Scooters Interactive.html')







