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


def getDataset(songName, recSongs):
    # read in cleaned data
    playlistDF = pd.read_csv('cleaned_data.csv')    

    playlistDF.info()

    # drop null values
    playlistDF.dropna(inplace=True)
    playlistDF.head()

    playlistDF.info()

    # drop string columns and columns that won't be used
    playlistUpdated = playlistDF.drop(['track_id', 'artists', 'album_name', 'track_name', 'track_genre', 'duration_ms'], axis=1)
    playlistUpdated

    # scale data in playlistUpdated
    playlistUpdated = StandardScaler().fit_transform(playlistUpdated[["popularity", "danceability", "energy", "key", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"]])
    playlistUpdated = pd.DataFrame(playlistUpdated, columns=["popularity", "danceability", "energy", "key", "loudness", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "time_signature"])
    playlistUpdated.head()

    # Create a PCA model instance and set `n_components=2`.
    pcaModel = PCA(n_components=2)

    # Use the PCA model with `fit_transform` to reduce to two principal components
    playlistPCA = pcaModel.fit_transform(playlistUpdated)

    # dump of the features that contribute to the variance ratios of each PC
    pd.DataFrame(pcaModel.components_,
             columns=playlistUpdated.columns,
             index=["PC1", "PC2"])
        # PC1: acousticness
        # PC2: tempo

    # Create a list with the number of k-values from 1 to 21
    kValues = list(range(1, 21))

    # convert playlistPCA to a dataframe
    playlistPCADF = pd.DataFrame(playlistPCA)


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

    # Create a DataFrame with the data to plot the Elbow curve
    pcaElbowDF = pd.DataFrame (
            {
                "k": kValues,
                "inertia": inertia
            }
    )

    # Create a KMeans instance with 3 clusters: model
    model = KMeans(n_clusters=5, random_state=1)

    # Fit the K-Means model using the scaled data
    model.fit(playlistPCADF)

    # generate the list of predicted values
    kmeans_predictions = model.predict(playlistPCADF)
    # Print the resulting array of cluster values.
    kmeans_predictions[:5]

    predictedDF = playlistUpdated.copy()
    # Add class columns with the labels to the new DataFrame
    predictedDF["kmeans-segments"] = kmeans_predictions
    predictedDF['track_name'] = playlistDF['track_name']
    predictedDF['track_genre'] = playlistDF['track_genre']
    predictedDF['track_id'] = playlistDF['track_id']
    predictedDF['artists'] = playlistDF['artists']
    predictedDF[0] = playlistPCADF[0]
    predictedDF[1] = playlistPCADF[1]

    # Enter Song Name Here
    track_name = songName

    print(track_name)

    # identify kmeans of selected song
    k_predict = predictedDF.loc[predictedDF['track_name'] == track_name, 'kmeans-segments'].values[0]

    # filter dataframe by kmeans value
    predictedDF = predictedDF.loc[predictedDF['kmeans-segments']==k_predict]

    # drop string columns and unecessary columns in predictedDF
    predictedUpdated = predictedDF.drop(['track_id', 'artists', 'track_name', 'track_genre', 'kmeans-segments', 0, 1], axis=1)

    # Create a PCA model instance and set `n_components=2`.
    pcaModel2 = PCA(n_components=2)

    # Use the PCA model with `fit_transform` to reduce to three principal components
    predictedPCA = pcaModel2.fit_transform(predictedUpdated)

    # dump of the features that contribute to the variance ratios of each PC
    pd.DataFrame(pcaModel2.components_,
                columns=predictedUpdated.columns,
                index=["PC1", "PC2"])
    # PC1: liveness
    # PC2: danceability

    # Create a list with the number of k-values from 1 to 21
    kValues2 = list(range(1, 21))

    # convert predictedPCA to a dataframe
    predictedPCADF = pd.DataFrame(predictedPCA)

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

    # Create a DataFrame with the data to plot the Elbow curve
    pcaElbowDF2 = pd.DataFrame (
        {
            "k2": kValues2,
            "inertia2": inertia2
        }
    )
    
    # Create a KMeans instance with 3 clusters: model
    model2 = KMeans(n_clusters=3, random_state=1)

    # Fit the K-Means model using the scaled data
    model2.fit(predictedPCADF)

    # generate the list of predicted values
    kmeans_predictions2 = model2.predict(predictedPCADF)

    # Print the resulting array of cluster values.
    kmeans_predictions2[:5]


    predictedDF2 = predictedUpdated.copy()

    # Add class columns with the labels to the new DataFrame
    predictedDF2["kmeans-segments2"] = kmeans_predictions2
    predictedDF2['track_name'] = predictedDF['track_name']
    predictedDF2['track_genre'] = predictedDF['track_genre']
    predictedDF2['track_id'] = predictedDF['track_id']
    predictedDF2['artists'] = predictedDF['artists']
    predictedDF2[0] = predictedPCADF[0]
    predictedDF2[1] = predictedPCADF[1]

    # identify kmeans of selected song
    k_predict2 = predictedDF2.loc[predictedDF2['track_name'] == track_name, 'kmeans-segments2'].values[0]
    k_predict2

    # filter dataframe by kmeans value
    predictedDF3 = predictedDF2.loc[predictedDF2['kmeans-segments2']==k_predict2]

    # Enter number of songs selected here

    if not recSongs:
        songNumber = 5
    else:    
        songNumber = int(recSongs)

    #songNumber = recSongs

    # sort dataframe by popularity
    predictedDF3 = predictedDF3.sort_values('popularity')
    predictedDF3 = predictedDF3.head(songNumber)
    

    # convert predicted songs into a list
    predictedSongs = predictedDF3[['track_name','artists']]


    return predictedSongs