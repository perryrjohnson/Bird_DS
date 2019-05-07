import pandas as pd
import numpy as np
import osmnx as ox
from sklearn import metrics
import matplotlib.pyplot as plt
from haversine import haversine

df = pd.read_csv('data.csv', index_col=0)

# Cleaning up road categories 
df['road_type'] = df['road_type'].str.replace('_link', '')
df['road_type'] = np.where(df['road_type'] == 'trunk', 'secondary', df['road_type'])
df['road_type'] = np.where(df['road_type'] == 'living_street', 'residential', df['road_type'])
df['road_type'] = np.where(df['road_type'] == 'a', 'unclassified', df['road_type'])

# convert closest highweay, primary, secondary, residential from km to meters
df['closest_highway'] = [i * 1000 for i in df['closest_highway']]
df['closest_primary'] = [i * 1000 for i in df['closest_primary']]
df['closest_secondary'] = [i * 1000 for i in df['closest_secondary']]
df['closest_residential'] = [i * 1000 for i in df['closest_residential']]

 
# calculate the closest scooter proximity for each scooter in meters at a snapshot in time
min_dist = []

for i in range(len(df)):
    base_lat = df['latitude'][i]
    base_lon = df['longitude'][i]
    main_geo = (base_lat, base_lon)
    timestamp = df['timestamp'][i]
    all_dist = []
    for i in range(len(df)):
        all_lat = df['latitude'][i]
        all_lon = df['longitude'][i]
        all_geo = (all_lat, all_lon)
        if main_geo == all_geo or df['timestamp'][i] != timestamp:
            pass
        else:
            print(haversine(main_geo, all_geo))
            all_dist.append(haversine(main_geo, all_geo))
            
    minimum = min(all_dist)
    min_dist.append(minimum)

# convert this to closest scooter distance from km to meters
df['closest_scooter'] = [i * 1000 for i in min_dist]


# calculate number of scooters within 2, 5, 10, 25, 50, and 100 meters of a given scooter for a given time snapshot
two_meter = []
five_meter = []
ten_meter = []
twentyfive_meter = []
fifty_meter = []
hundred_meter = []
for i in range(len(df)):
    base_lat = df['latitude'][i]
    base_lon = df['longitude'][i]
    main_geo = (base_lat, base_lon)
    all_dist = []
    timestamp = df['timestamp'][i]
    for i in range(len(df)):
        all_lat = df['latitude'][i]
        all_lon = df['longitude'][i]
        all_geo = (all_lat, all_lon)
        if main_geo == all_geo or df['timestamp'][i] != timestamp:
            pass
        else:
            all_dist.append(haversine(main_geo, all_geo))
            
    all_dist_scaled = [i * 1000 for i in all_dist]
    two_count = len([i for i in all_dist_scaled if i<2])
    two_meter.append(two_count)    
    five_count = len([i for i in all_dist_scaled if i<5])
    five_meter.append(five_count)
    ten_count = len([i for i in all_dist_scaled if i<10])
    ten_meter.append(ten_count)
    twentyfive_count = len([i for i in all_dist_scaled if i<25])
    twentyfive_meter.append(twentyfive_count)
    fifty_count = len([i for i in all_dist_scaled if i<50])
    fifty_meter.append(fifty_count)
    hundred_count = len([i for i in all_dist_scaled if i< 100])
    hundred_meter.append(hundred_count)

df['two_meter'] = two_meter  
df['five_meter'] = five_meter
df['ten_meter'] = ten_meter
df['twentyfive_meter'] = twentyfive_meter
df['fifty_meter'] = fifty_meter
df['hundred_meter'] = hundred_meter

# count the number of scooters with battery level >= 95 within a five meter distance for a given snapshot in time
highest_bat_proximity = []

for i in range(len(df)):
    base_lat = df['latitude'][i]
    base_lon = df['longitude'][i]
    main_geo = (base_lat, base_lon)
    timestamp = df['timestamp'][i]    
    all_dist = []
    for i in range(len(df)):
        all_lat = df['latitude'][i]
        all_lon = df['longitude'][i]
        all_geo = (all_lat, all_lon)
        if main_geo == all_geo or df['battery_level'][i] < 95 or timestamp != df['timestamp'][i]:
            pass
        else:
            all_dist.append(haversine(main_geo, all_geo))
            
    all_dist_scaled = [i * 1000 for i in all_dist]
    five_meters = len([i for i in all_dist_scaled if i<=5])
    highest_bat_proximity.append(five_meters)        

df['highest_bat_proximity'] = highest_bat_proximity

# count the number of scooters with battery level >= 90 within a ten meter distance for a given snapshot in time
high_bat_proximity = []

for i in range(len(df)):
    base_lat = df['latitude'][i]
    base_lon = df['longitude'][i]
    main_geo = (base_lat, base_lon)
    timestamp = df['timestamp'][i]    
    all_dist = []
    for i in range(len(df)):
        all_lat = df['latitude'][i]
        all_lon = df['longitude'][i]
        all_geo = (all_lat, all_lon)
        if main_geo == all_geo or df['battery_level'][i] < 90 or timestamp != df['timestamp'][i]:
            pass
        else:
            all_dist.append(haversine(main_geo, all_geo))
            
    all_dist_scaled = [i * 1000 for i in all_dist]
    ten_meters = len([i for i in all_dist_scaled if i<=10])
    high_bat_proximity.append(ten_meters)        

df['high_bat_proximity'] = high_bat_proximity

# count the number of scooters with battery level < 60 within a 10 meter distance
low_bat_proximity = []

for i in range(len(df)):
    base_lat = df['latitude'][i]
    base_lon = df['longitude'][i]
    main_geo = (base_lat, base_lon)
    timestamp = df['timestamp'][i]
    all_dist = []
    for i in range(len(df)):
        all_lat = df['latitude'][i]
        all_lon = df['longitude'][i]
        all_geo = (all_lat, all_lon)
        if main_geo == all_geo or df['battery_level'][i] >= 60 or timestamp != df['timestamp'][i]:
            pass
        else:
            all_dist.append(haversine(main_geo, all_geo))
            
    all_dist_scaled = [i * 1000 for i in all_dist]
    ten_meters = len([i for i in all_dist_scaled if i<=10])
    low_bat_proximity.append(ten_meters)  

df['low_bat_proximity'] = low_bat_proximity


# calculate the closest high battery (>= 90%) scooter proximity for each scooter in meters at a snapshot in time and the average distance of the 5 closest high battery (>= 90%) scooters 
min_dist = []
avg_dist = []

for i in range(len(df)):
    base_lat = df['latitude'][i]
    base_lon = df['longitude'][i]
    main_geo = (base_lat, base_lon)
    timestamp = df['timestamp'][i]
    all_dist = []
    for i in range(len(df)):
        all_lat = df['latitude'][i]
        all_lon = df['longitude'][i]
        all_geo = (all_lat, all_lon)
        if main_geo == all_geo or df['timestamp'][i] != timestamp or df['battery_level'][i] < 90:
            pass
        else:
            all_dist.append(haversine(main_geo, all_geo))
            
    minimum = min(all_dist)
    all_dist.sort()
    top_five = all_dist[0:5]
    average = np.mean(top_five)
    min_dist.append(minimum)
    avg_dist.append(average)
    
# convert this distance from km to meters
df['min_high_bat_dist'] = [i * 1000 for i in min_dist]
df['avg_high_bat_dist'] = [i * 1000 for i in avg_dist]


# create log features for closest_highway and closest scooter

df['log_highway'] = np.log(df['closest_highway'])
df['log_scooter'] = np.log(df['closest_scooter'])
