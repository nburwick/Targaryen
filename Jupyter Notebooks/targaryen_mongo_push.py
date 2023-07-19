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

cid = cid
secret = secret
uri = "http://localhost:8080"
os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = uri
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret, cache_handler=MemoryCacheHandler())
spotify = spotipy.Spotify(auth_manager=client_credentials_manager)

def get_clean_csv_data():
    genre_seeds = spotify.recommendation_genre_seeds()['genres']
    seeds = np.arange(1,len(genre_seeds) +1)
    genres_convert = dict(zip(genre_seeds, seeds))
    df = pd.read_csv(os.path.join('..','Resouces', 'dataset-long.csv'), delimiter=',', index_col=0, low_memory=False)
    df_cleaned = df.drop_duplicates(['track_name', 'artists'], keep='first').reset_index(drop=True)
    df_cleaned = df_cleaned.dropna(subset='track_name').reset_index(drop=True)
    df_cleaned['track_url'] = None
    df_cleaned['genre_seed'] = None
    for index, track in tqdm(df_cleaned.iterrows(), total=df_cleaned.shape[0]):
        genre = track['track_genre']
        df_cleaned.at[index, 'genre_seed'] = genres_convert[genre]
        df_cleaned.at[index, 'artists'] = track['artists'].split(';')
    songs_in_mongo = list(targ_songs.find({}))
    mongo_df = pd.json_normalize(songs_in_mongo)
    mongo_df.drop(columns='_id', inplace=True, errors='ignore')
    df_cleaned.update(mongo_df)
    # df_cleaned.to_json(os.path.join('..', 'Outputs', 'cleaned_data.json'),orient='records')
    return df_cleaned, mongo_df

df, mongo_df = get_clean_csv_data()


not_found = [] 
keep_traits = ['track_id', 'artists', 'track_name',
                       'popularity', 'duration_ms', 'explicit', 'danceability',
                       'energy', 'key', 'loudness', 'mode','speechiness',
                       'acousticness','instrumentalness','liveness','valence',
                       'tempo','time_signature']


df = df[df['track_url'].isnull()].reset_index(drop=True)

# create chunks
chunks = [df.iloc[df.index[i:i + 50]] for i in range(0, df.shape[0], 50)]

# file = open(os.path.join('..', 'Outputs', 'cleaned_data.json'), "a")
print("PUSHING NEW TRACKS INTO MONGO: See Progress Below")
for chunk in tqdm(chunks, total=len(chunks)): 
    spotify = spotipy.Spotify(auth_manager=client_credentials_manager)
    ids = chunk['track_id'].tolist()
    results_1 = spotify.tracks(ids)['tracks']
    for result in results_1:
        if result['id'] in ids:
            df_index = chunk[chunk['track_id'] == result['id']].index[0]
            df.at[df_index, 'album_name'] = result['album']['name']
            artists = []
            for art in result['artists'][:]:
                artists.append(art['name'])
            df.at[df_index, 'artists'] = artists
            df.at[df_index, 'track_url'] = result['external_urls']['spotify']
            df.at[df_index, 'preview_url'] = result['preview_url']
            df.at[df_index, 'popularity'] = result['popularity']
    results_2 = spotify.audio_features(ids)
    for result in results_2:
        if result['id'] in ids:
            df_index = chunk[chunk['track_id'] == result['id']].index[0]
            delete = set(result.keys()) - set(keep_traits)
            for trait in delete:
                del result[trait]
            for trait in result.keys():
                df.at[df_index, trait] = result[trait]
            push = json.loads(df.iloc[df_index].to_json())
            targ_songs.insert_one(push)
            

df = df[~df['track_url'].isnull()]     
df.to_json(os.path.join('..', 'Outputs', 'cleaned_data.json'),orient='records')