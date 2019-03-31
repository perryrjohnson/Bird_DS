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

# output df to csv file
df.to_csv('data.csv')
