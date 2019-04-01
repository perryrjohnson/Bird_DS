# functions from Sam Chamberlain's HealthyHomes_Insight project

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points
from shapely import wkt
import itertools

def remove_double_ID_streets(df):
    '''Some OSM streets have doubled names (lists in list) that need to be removed for further
    calculations. This function removes any double IDs. This is very few (~10 of 10k).'''
    out_df = df.copy()
    for i, val in enumerate(out_df.highway):
        if isinstance(val, list):
            out_df.drop(i, inplace=True)
    return(out_df)

def distance_to_roadway(gps, roadway):
    '''Calculates distance from GPS point to nearest road line polygon'''
    dists = []
    for i in roadway.geometry:
        dists.append(i.distance(gps))
    return(np.min(dists))

def find_closest_road(gps, roads, buffer_dist = 0.0003):
    '''Finds the closest road to a GPS point. If no roads are within 30m the point is considered outside
    of a known roadway'''
    road_index = roads.sindex
    #build buffer around point (~ 30 meters)
    circle = gps.buffer(buffer_dist)
    
    #get index of possible nearest roads
    possible_matches_index = list(road_index.intersection(circle.bounds))
    possible_matches = roads.iloc[possible_matches_index]
    precise_matches = possible_matches[possible_matches.intersects(circle)].copy()

    #get distances to roads in buffer
    precise_matches['distance'] = precise_matches['geometry'].distance(gps)
    
    if precise_matches['distance'].empty is False:
        return(precise_matches.sort_values(['distance']).drop_duplicates('distance').iloc[0, 3])
    else:
        return('outside_area')


def nearest_intersection(gps, intersections):
    ''' Calculates distance from GPS point to nearest intersection'''
    closest_point = nearest_points(gps, MultiPoint(intersections.values))[1]
    return(gps.distance(closest_point))

def import_gpd(filename):
    '''Import csv file as geopandas dataframe with geometries calculated'''
    data = pd.read_csv(filename)
    data['geometry'] = data['geometry'].apply(wkt.loads)
    data_gpd = gpd.GeoDataFrame(data, geometry = data['geometry'], crs={'init' :'epsg:4326'})
    data_gpd = data_gpd.drop(['Unnamed: 0'], axis = 1)
    return(data_gpd)

