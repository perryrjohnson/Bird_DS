# import libraries
import osmnx as ox
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from shapely.geometry import  MultiPoint
from haversine import haversine
from sklearn import metrics

# read in a dataframe
df = pd.read_csv('final_merge.csv', index_col=0)

# get centroid lat, lon of a cluster
def get_centroid(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    return list(centroid)

# derive clusters from reading in dataframe with scooter's coordinates  
def cluster_algorithm(df):
    
    coords = df[['latitude', 'longitude']].values

    # eps is the physical distance from each point that forms its neighborhood
    # points must be within 50 meters of each other and a cluster must contain at least 4 points.
    eps_rad = 50 / 3671000

    db = DBSCAN(eps=eps_rad, min_samples=4, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))

    cluster_labels = db.labels_
    
    clusters = pd.Series([coords[cluster_labels==n] for n in range(min(cluster_labels), max(cluster_labels))])

    clust_lat = []
    clust_lon = []
    for i in range(len(clusters)):
        centroid_point = get_centroid(clusters[i])
        lat, lon = centroid_point
        clust_lat.append(lat)
        clust_lon.append(lon)
        
    return clust_lat, clust_lon 
