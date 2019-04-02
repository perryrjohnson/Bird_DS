import osmnx as ox
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn import metrics
import time

df = pd.read_csv('final_merge.csv', index_col=0)

kms_per_radian = 6371.0088

coords = df[['latitude', 'longitude']].values

# eps is the physical distance from each point that forms its neighborhood
# define epsilon as 0.025 kilometers (25 meters), converted to radians for use by haversine
epsilon  = 0.025 /  kms_per_radian
start_time  = time.time()

db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))

cluster_labels = db.labels_

df['cluster_labels'] = cluster_labels

num_clusters  = len(set(cluster_labels))

# all done, print the outcome
message = 'Clustered {:,} points down to {:,} clusters, for {:.1f}% compression in {:,.2f} seconds'
print(message.format(len(df), num_clusters, 100*(1 - float(num_clusters) / len(df)), time.time()-start_time))
print('Silhouette coefficient: {:0.03f}'.format(metrics.silhouette_score(coords, cluster_labels)))

df.to_csv('cluster_test.csv')
