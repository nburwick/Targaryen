# Import Dependencies for Notebook
import pandas as pd
import json
import os
import numpy as np
from pprint import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import MemoryCacheHandler
import time
from tqdm import tqdm

from spotify_creds import sp_uri, mdb_uri, secret, cid

server = ServerApi('1')
# Create a new client and connect to the server
mongo = MongoClient(mdb_uri, server_api=server)
database = mongo['targ_data']
targ_songs = database['song_data']

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret, cache_handler=MemoryCacheHandler())

def get_data():
    songs_in_mongo = list(targ_songs.find({'preview_url': None}))
    mongo_df = pd.json_normalize(songs_in_mongo)
    # df_cleaned.to_json(os.path.join('..', 'Outputs', 'cleaned_data.json'),orient='records')
    return mongo_df

df = get_data()

keep_traits = ['track_id', 'artists', 'track_name',
                       'popularity', 'duration_ms', 'explicit', 'danceability',
                       'energy', 'key', 'loudness', 'mode','speechiness',
                       'acousticness','instrumentalness','liveness','valence',
                       'tempo','time_signature']

df = df[df['preview_url'].isnull()].reset_index(drop=True)

not_found=[]
print("PUSHING NEW TRACKS INTO MONGO: See Progress Below")
for index, track in tqdm(df.iterrows(), total=df.shape[0]): 
    spotify = spotipy.Spotify(auth_manager=client_credentials_manager)
    time.sleep(1)
    results = spotify.search(f"track:{track['track_name']} artist:{track['artists'][0]}", limit=50)['tracks']['items']
    # print(results[0])
    for result in results:
        if result['name'] == track['track_name'] and result['artists'][0]['name'] and pd.notnull(result['preview_url']):
            df_index = df[df['track_name'] == result['name']].index[0]
            if not pd.isnull(result['preview_url']):
                df.at[df_index, 'preview_url'] = result['preview_url']
                obj_id = {'_id' : df.loc[df_index, '_id']}
                push = { "$set" : {'preview_url' : result['preview_url'], 'track_url': result['external_urls']['spotify'],
                                   'track_id': result['id']}}
                targ_songs.update_one(obj_id, push)
                break
            else:
                not_found.append(track.to_dict())