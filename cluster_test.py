import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
import time
from scipy.sparse import csr_matrix
from scipy.spatial.distance import squareform, pdist
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

# import DC df
df = pd.read_csv('DC_1.csv', index_col=0)


eps = 300 #meters
minpts = 10 #smallest cluster size allowed
pseduo_minpts = 1

n_clusters = 5




# get the street network for Washington, DC
city = ['DC', 38.89511, -77.03637] 
lat = city[1]
lon = city[2]
center_point = (lat, lon)
#convert to radians
stack = np.column_stack((df.latitude, df.longitude))
rads = np.radians(stack)

G = ox.graph_from_point(center_point, distance=4000, network_type='all')
fig, ax = ox.plot_graph(G, show=False, close=False)
fig.set_size_inches(8, 8)

ax.scatter(df.longitude, df.latitude, c='red')
ax.set_title(str(len(df.longitude))+' Bird Scooter observations in '+city[0])   
plt.show()


eps_rad =eps / 3671000
db = DBSCAN(eps=eps_rad, min_samples=minpts, metric='haversine', algorithm='ball_tree')
df['spatial_cluster'] = db.fit_predict(rads)


# plot firms by cluster
color_map = {-1:'black', 0:'g', 1:'r', 2:'m', 3:'b'}
point_colors = [color_map[c] for c in df['spatial_cluster']]
fig, ax = ox.plot_graph(G, node_size=0, show=False, close=False)
ax.scatter(x = df['longitude'], y = df['latitude'], c=point_colors, marker='.', s=50, zorder=3)
ax.set_title('Clustering of Bird Scooters in '+city[0])
plt.show()