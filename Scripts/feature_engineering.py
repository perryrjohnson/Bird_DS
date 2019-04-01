import geopandas as gpd
import pandas as pd
import osmnx as ox
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
from shapely import wkt

cities = [('Austin', 30.26715, -97.74306), 
          ('Atlanta', 33.753746, -84.386330),
          ('DC', 38.89511, -77.03637),
          ('Indianapolis', 39.7685, -86.159),
          ('Santa Monica', 34.024212, -118.496475)]


master_gdf = import_gpd('master_merge.csv')
    
for city in cities:
    city_gdf = master_gdf[master_gdf['city'] == city[0]]
    lat = city[1]
    lon = city[2]
    center_point = (lat, lon)
    
    # grab street data (roads and intersections) for entire city
    city_streets = ox.graph_from_point(center_point, distance = 12000, network_type = 'drive')
    nodes, edges = ox.graph_to_gdfs(city_streets)
    
    #remove doubled road IDs
    city_rds = remove_double_ID_streets(edges)
    
    
    city_highways = city_rds[city_rds.highway == 'motorway']
    city_primary = city_rds[city_rds.highway == 'primary']
    city_secondary = city_rds[city_rds.highway == 'secondary']
    city_resid = city_rds[city_rds.highway == 'residential']
    

    city_gdf['road_type'] = city_gdf['geometry'].apply(find_closest_road, roads = city_rds)
    city_gdf['closest_highway'] = city_gdf['geometry'].apply(distance_to_roadway, roadway = city_highways)
    city_gdf['closest_primary'] = city_gdf['geometry'].apply(distance_to_roadway, roadway = city_primary)
    city_gdf['closest_secondary'] = city_gdf['geometry'].apply(distance_to_roadway, roadway = city_secondary)
    city_gdf['closest_residential'] = city_gdf['geometry'].apply(distance_to_roadway, roadway = city_resid)


    city_df = pd.DataFrame(city_gdf)
    city_df.to_csv(city[0]+'.csv')

    
    

    
        
