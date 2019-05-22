# A Bird's Eye View: Leveraging Machine Learning to Generate Nests
A full-stack machine learning application, that classifies scooters into nests in real-time based on scooter attributes and city features. It then makes new nest recommendations for the non-nest scooters which are generated via geospatial clustering. 

### Data Collection and Machine Learning Pipeline 

<img src="Visualizations/ML_Pipeline.png" height="400">

The major bike and scooter providers (Bird, JUMP, Lime) don't have publicly accessible APIs. However, some folks have seemingly been able to reverse-engineer the Bird API used to populate the maps in their Android and iOS applications.

One interesting feature of this data is the nest_id, which indicates if the Bird scooter is in a "nest" - a centralized drop-off spot for charged Birds to be released back into circulation. 

By predicting whether a Bird is part of a nest or not, we could automate location recommendations for newly charged Birds to be released back on the streets. 

I set out to ask the following questions:
1) *Can real-time predictions be made to determine if a scooter is currently in a nest?*

2) *For non-nest scooters, can new nest location recommendations be generated from geospatial clustering?*


A walk through of the statistical analysis and machine learning model development can be found [here](https://github.com/perryrjohnson/Bird_DS/blob/master/Visualizations/display_notebook.ipynb)





Comments or Questions? Please email me at: perryrjohnson7@gmail.com
