# traits_dictionary = {
#     'danceability': [0.714],
#     'energy': [0.472],
#     'key': [2],
#     'loudness':[-7.375],
#     'mode':1,
#     'speechiness':[0.0864],
#     'acousticness': [0.013],
#     'instrumentalness':[0.00000451],
#     'liveness':[0.266],
#     'valence':[0.238],
#     'tempo':[131.121],
#     'time_signature':[4]
# }



def songRecommender(track_id, mongoDB, traits_dictionary, num_recs):
    import pandas as pd
    import os
    from sklearn.neighbors import NearestNeighbors
    if num_recs == "" or num_recs == None:
      num_recs = 10
    
    # Convert DataBased Songs into a DataFram
    original_df = pd.json_normalize(mongoDB)
    original_df = original_df[original_df['track_id'] != track_id].reset_index(drop=True)

    # Extract Song Qualities
    song_q = original_df.drop(columns=['track_id', 'artists', 'album_name', 'track_name', 'track_genre', 'duration_ms', 'track_url', 'popularity', 'explicit','_id']).dropna().reset_index(drop=True)
    
    # print(song_q.info())

    # Establish KNN Model
    knn = NearestNeighbors(n_neighbors=int(num_recs))
    knn.fit(song_q)

    # Convert Searched Song Traits
    test = pd.DataFrame(traits_dictionary)
    test = test.drop(columns=['track_id', 'artists', 'album_name', 'track_name', 'track_genre', 'duration_ms', 'track_url', 'popularity', 'explicit', '_id'])
    
    # Find Similar Songs from KNN Model
    result = knn.kneighbors(test)[1].tolist()[0]
    
    # Filter DataBase Songs by Result Indices
    result_df = original_df.iloc[result]
    
    # Create Clickable Links & Clean Artists
    for index, track in result_df.iterrows():
      link = track['track_url']
      name = track['track_name']
      result_df.loc[index,'track_name'] = f'<a href={link}>{name}</a>'
      arts = track['artists'].strip("][").split(",")
      result_df.loc[index, 'artists'] = ", ".join(arts).replace("'","")
    
    result_df = result_df[['track_name', 'artists', 'track_genre']]
    return result_df