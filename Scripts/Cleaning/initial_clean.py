import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np



df = pd.read_csv('final_merge.csv', index_col=0)


df = df.drop(['precip', 'code', 'corner_dist', 'signal_dist', 'captive'], axis=1)

df['wspd'] = df['wspd'].fillna(0)

df = df.to_csv('final_merge.csv')
