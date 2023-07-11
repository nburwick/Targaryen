#!/usr/bin/env python
# coding: utf-8

# In[4]:


get_ipython().run_line_magic('env', 'HV_DOC_HTML=True')


# In[5]:


pip install -q hvplot


# In[6]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.cluster import KMeans, AgglomerativeClustering, Birch
from sklearn.decomposition import PCA
import hvplot.pandas


import seaborn as sb

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import TSNE

import warnings
warnings.filterwarnings('ignore')


# In[7]:


# read in cleaned data
playlistDF = pd.read_csv('../Outputs/cleaned_data.csv')
playlistDF.head()


# In[8]:


playlistDF.info()


# In[9]:


# drop null values
playlistDF.dropna(inplace=True)
playlistDF.head()


# In[10]:


playlistDF.info()


# In[11]:


# drop string columns and columns that won't be used
playlistUpdated = playlistDF.drop(['track_id', 'artists', 'album_name', 'track_name', 'track_genre', 'duration_ms'], axis=1)
playlistUpdated


# In[12]:


# scale data in playlistUpdated
playlistUpdated = StandardScaler().fit_transform(playlistUpdated[["popularity", "danceability", "energy", "key", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"]])
playlistUpdated = pd.DataFrame(playlistUpdated, columns=["popularity", "danceability", "energy", "key", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"])
playlistUpdated.head()


# In[13]:


# Create a PCA model instance and set `n_components=2`.
pcaModel = PCA(n_components=2)


# In[14]:


# Use the PCA model with `fit_transform` to reduce to two principal components
playlistPCA = pcaModel.fit_transform(playlistUpdated)

# View the first five rows of the DataFrame.
playlistPCA[:5]


# In[15]:


# breakdown of the explained variance for all rows of data that was reduced
pcaModel.explained_variance_ratio_


# In[16]:


# dump of the features that contribute to the variance ratios of each PC
pd.DataFrame(pcaModel.components_,
             columns=playlistUpdated.columns,
             index=["PC1", "PC2"])
# PC1: acousticness
# PC2: tempo


# In[17]:


# Create a list with the number of k-values from 1 to 21
kValues = list(range(1, 21))


# In[18]:


# convert playlistPCA to a dataframe
playlistPCADF = pd.DataFrame(playlistPCA)
playlistPCADF.head()


# In[19]:


# Create an empty list to store the inertia values
inertia = []

# Create a for loop to compute the inertia with each possible value of k
for k in kValues:
  # make a model for the value of k
  kModel = KMeans(n_clusters=k, random_state=0)

  # fit the model onto the data
  kModel.fit(playlistPCADF)

  # append inertia value to list
  inertia.append(kModel.inertia_)


# In[20]:


# Create a DataFrame with the data to plot the Elbow curve
pcaElbowDF = pd.DataFrame (
        {
            "k": kValues,
            "inertia": inertia
        }
)

pcaElbowDF.head()


# In[21]:


# Plot the DataFrame to identify the optimal value for K
hvplot.extension("bokeh")
pcaElbowCurve = pcaElbowDF.hvplot.line(
    x="k",
    y="inertia",
    xticks="k",
    title="PCA Elbow Curve"
).opts(width=900, height=400)

pcaElbowCurve


# In[22]:


# Create a KMeans instance with 3 clusters: model
model = KMeans(n_clusters=5, random_state=1)

# Fit the K-Means model using the scaled data
model.fit(playlistPCADF)

# generate the list of predicted values
kmeans_predictions = model.predict(playlistPCADF)
# Print the resulting array of cluster values.
kmeans_predictions[:5]


# In[23]:


predictedDF = playlistUpdated.copy()
# Add class columns with the labels to the new DataFrame
predictedDF["kmeans-segments"] = kmeans_predictions
predictedDF['track_name'] = playlistDF['track_name']
predictedDF['track_genre'] = playlistDF['track_genre']
predictedDF['track_id'] = playlistDF['track_id']
predictedDF['artists'] = playlistDF['artists']
predictedDF[0] = playlistPCADF[0]
predictedDF[1] = playlistPCADF[1]

predictedDF.head(3)


# In[33]:


# Plot the kmeans clusters
hvplot.extension("bokeh")
predictedDF.hvplot.scatter(
    x="0",
    y="1",
    by="kmeans-segments"
)


# In[34]:


track_name = 'KICK BACK'


# In[35]:


# identify kmeans of selected song
k_predict = predictedDF.loc[predictedDF['track_name'] == track_name, 'kmeans-segments'].values[0]
k_predict


# In[36]:


# filter dataframe by kmeans value
predictedDF = predictedDF.loc[predictedDF['kmeans-segments']==k_predict]
predictedDF.head()


# In[26]:


# drop string columns and unecessary columns in predictedDF
predictedUpdated = predictedDF.drop(['track_id', 'artists', 'track_name', 'track_genre', 'kmeans-segments', 0, 1], axis=1)
predictedUpdated.head()


# In[27]:


# Create a PCA model instance and set `n_components=2`.
pcaModel2 = PCA(n_components=2)


# In[28]:


# Use the PCA model with `fit_transform` to reduce to three principal components
predictedPCA = pcaModel2.fit_transform(predictedUpdated)

# View the first five rows of the DataFrame
predictedPCA[:5]


# In[29]:


# breakdown of the explained variance for all rows of data that were reduced
pcaModel2.explained_variance_ratio_


# In[30]:


# dump of the features that contribute to the variance ratios of each PC
pd.DataFrame(pcaModel2.components_,
             columns=predictedUpdated.columns,
             index=["PC1", "PC2"])
# PC1: liveness
# PC2: danceability


# In[31]:


# Create a list with the number of k-values from 1 to 21
kValues2 = list(range(1, 21))


# In[32]:


# convert predictedPCA to a dataframe
predictedPCADF = pd.DataFrame(predictedPCA)
predictedPCADF.head()


# In[33]:


# Create an empty list to store the inertia values
inertia2 = []

# Create a for loop to compute the inertia with each possible value of k
for k2 in kValues2:
  # make a model for the value of k
  kModel2 = KMeans(n_clusters=k2, random_state=0)

  # fit the model onto the data
  kModel2.fit(predictedPCADF)

  # append inertia value to list
  inertia2.append(kModel2.inertia_)


# In[34]:


# Create a DataFrame with the data to plot the Elbow curve
pcaElbowDF2 = pd.DataFrame (
        {
            "k2": kValues2,
            "inertia2": inertia2
        }
)

pcaElbowDF2.head()


# In[35]:


# Plot the DataFrame to identify the optimal value for K
hvplot.extension("bokeh")
pcaElbowCurve2 = pcaElbowDF2.hvplot.line(
    x="k2",
    y="inertia2",
    xticks="k2",
    title="PCA Elbow Curve 2"
).opts(width=900, height=400)

pcaElbowCurve2


# In[36]:


# Create a KMeans instance with 3 clusters: model
model2 = KMeans(n_clusters=3, random_state=1)

# Fit the K-Means model using the scaled data
model2.fit(predictedPCADF)

# generate the list of predicted values
kmeans_predictions2 = model2.predict(predictedPCADF)

# Print the resulting array of cluster values.
kmeans_predictions2[:5]


# In[37]:


predictedDF2 = predictedUpdated.copy()

# Add class columns with the labels to the new DataFrame
predictedDF2["kmeans-segments2"] = kmeans_predictions2
predictedDF2['track_name'] = predictedDF['track_name']
predictedDF2['track_genre'] = predictedDF['track_genre']
predictedDF2['track_id'] = predictedDF['track_id']
predictedDF2['artists'] = predictedDF['artists']
predictedDF2[0] = predictedPCADF[0]
predictedDF2[1] = predictedPCADF[1]

predictedDF2.head(3)


# In[38]:


# Plot the kmeans clusters
hvplot.extension("bokeh")
predictedDF2.hvplot.scatter(
    x="0",
    y="1",
    by="kmeans-segments2"
)


# In[39]:


# identify kmeans of selected song
k_predict2 = predictedDF2.loc[predictedDF2['track_name'] == track_name, 'kmeans-segments2'].values[0]
k_predict2


# In[40]:


# filter dataframe by kmeans value
predictedDF3 = predictedDF2.loc[predictedDF2['kmeans-segments2']==k_predict2]
predictedDF3


# In[41]:


# number of songs selected by user
songNumber = 5


# In[42]:


# sort dataframe by popularity
predictedDF3 = predictedDF3.sort_values('popularity')
predictedDF3 = predictedDF3.head(songNumber)
predictedDF3


# In[43]:


# convert predicted songs into a list
predictedSongs = predictedDF3['track_name'].tolist()
predictedSongs


# In[ ]:




