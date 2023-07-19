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



def songRecommender(track_id, mongoDB, traits_dictionary, num_recs, explicit):
    import pandas as pd
    import os
    from sklearn.neighbors import NearestNeighbors
    if num_recs == "" or num_recs == None:
      num_recs = 10
    
    # Convert DataBased Songs into a DataFrame
    original_df = pd.json_normalize(mongoDB)
    original_df = original_df[original_df['track_id'] != track_id].reset_index(drop=True)
<<<<<<< HEAD
=======
    print(f"{len(mongoDB) - original_df.shape[0]} tracks removed")
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
    
    # Filter Explicit?
    if explicit == "0":
      # No was selected
      original_df = original_df[~original_df['explicit']].reset_index(drop=True)

    # Extract Song Qualities
<<<<<<< HEAD
    song_q = original_df[['danceability', 'energy', 'key',
                          'loudness', 'mode', 'speechiness',
                          'acousticness','instrumentalness',
                          'liveness', 'valence', 'tempo',
                          'time_signature']].dropna().reset_index(drop=True)
=======
    song_q = original_df.drop(columns=['track_id', 'artists', 'track_name', 'duration_ms', 'track_url', 'popularity', 'explicit','_id'], errors='ignore').dropna().reset_index(drop=True)
    
    # print(song_q.info())
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed

    # Establish KNN Model
    knn = NearestNeighbors(n_neighbors=int(num_recs))
    knn.fit(song_q)

    # Convert Searched Song Traits
<<<<<<< HEAD
    search = pd.DataFrame(traits_dictionary)
    search = search[['danceability', 'energy', 'key',
                     'loudness', 'mode', 'speechiness',
                     'acousticness','instrumentalness',
                     'liveness', 'valence', 'tempo',
                     'time_signature']]
    
    # Find Similar Songs from KNN Model
    result = knn.kneighbors(search)[1].tolist()[0]
    
    # Filter DataBase Songs by Result Indices
    result_df = original_df.iloc[result].reset_index(drop=True)
    
    # Create Clickable Links & Clean Artists
    for index, track in result_df.iterrows():
      if not pd.isnull(track['track_url']):
        result_df.loc[index,'Track Name'] = f'<a href={track["track_url"]}>{track["track_name"]}</a>'
      arts = str(track['artists']).strip("][").split(", ")
      result_df.loc[index, 'Artists'] = ", ".join(arts).replace("'","")
      if not pd.isnull(result_df.loc[index,'preview_url']):
        result_df.loc[index, 'Preview'] = f"<audio controls='paused' src='{track['preview_url']}'>"
      else:
        result_df.loc[index, 'Preview'] = "Preview Unavailable"
    
    result_df.index += 1
    
    print(result_df[['track_name', 'artists']])
    return result_df[['Track Name', 'Artists', 'Preview']]
=======
    test = pd.DataFrame(traits_dictionary)
    test = test.drop(columns=['track_id', 'artists', 'track_name', 'duration_ms', 'track_url', 'popularity', 'explicit', '_id'], errors='ignore')
    
    # Find Similar Songs from KNN Model
    result = knn.kneighbors(test)[1].tolist()[0]
    
    # Filter DataBase Songs by Result Indices
    result_df = original_df.iloc[result]
    
    # Create Clickable Links & Clean Artists
    for index, track in result_df.iterrows():
      link = track['track_url']
      name = track['track_name']
      result_df.loc[index,'track_name'] = f'<a href={link}>{name}</a>'
      arts = track['artists'].strip("][").split(", ")
      result_df.loc[index, 'artists'] = ", ".join(arts).replace("'","")
    
    result_df = result_df[['track_name', 'artists']].reset_index(drop=True)
    return result_df
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
