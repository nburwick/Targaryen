import pandas as pd
import json
import os
import numpy as np
from pprint import pprint
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth as auth
import time
from tqdm import tqdm

uri = 'mongodb+srv://nburwick:Swim_Fast01@cluster0.nvujnf4.mongodb.net/?retryWrites=true&w=majority'
server = ServerApi('1')
# Create a new client and connect to the server
mongo = MongoClient(uri, server_api=server)
database = mongo['targ_data']
targ_songs = database['song_data']

cid = "29ed89dc01c84a14bb29a6e1570405df"
secret = "ab90e0dfeae04c1ebfe248fa8ff2adeb"
uri = "http://localhost:8080"
os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = uri
scope = "user-library-read"
oauth = auth(scope=scope)
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
spotify = spotipy.Spotify(auth_manager=client_credentials_manager)

def get_clean_csv_data():
    genre_seeds = spotify.recommendation_genre_seeds()['genres']
    seeds = np.arange(1,len(genre_seeds) +1)
    genres_convert = dict(zip(genre_seeds, seeds))
    df = pd.read_csv(os.path.join('..','Resouces', 'dataset-long.csv'), delimiter=',', index_col=0, low_memory=False)
    df_cleaned = df.drop_duplicates(['track_name', 'artists']).reset_index(drop=True)
    df_cleaned = df_cleaned.dropna(subset='track_name').reset_index(drop=True)
    df_cleaned['track_url'] = None
    df_cleaned['genre_seed'] = None
    for index, track in df_cleaned.iterrows():
        genre = track['track_genre']
        df_cleaned.at[index, 'genre_seed'] = genres_convert[genre]
        df_cleaned.at[index, 'artists'] = track['artists'].split(';')
    songs_in_mongo = list(targ_songs.find({}))
    mongo_df = pd.json_normalize(songs_in_mongo)
    mongo_df.drop(columns='_id', inplace=True)
    df_cleaned.update(mongo_df)
    df_cleaned.to_json(os.path.join('..', 'Outputs', 'cleaned_data.json'),orient='records')
    js_data = json.loads(df_cleaned.to_json(orient='records'))
    return df_cleaned, js_data, mongo_df

df, file_data , mongo_df = get_clean_csv_data()


not_found = [] 
keep_traits = ['track_id', 'artists', 'track_name',
                       'popularity', 'duration_ms', 'explicit', 'danceability',
                       'energy', 'key', 'loudness', 'mode','speechiness',
                       'acousticness','instrumentalness','liveness','valence',
                       'tempo','time_signature']


# file = open(os.path.join('..', 'Outputs', 'cleaned_data.json'), "a")
print("PUSHING NEW TRACKS INTO MONGO: See Progress Below")
for index, track in tqdm(df[~(df.track_id.isin(mongo_df.track_id))].iterrows(), total=df[~(df.track_id.isin(mongo_df.track_id))].shape[0]):
    if pd.isnull(track['track_url']):
        try:
            track_id = track['track_id']
            result = spotify.track(track_id)
            # print(result)
            time.sleep(1)
            album = result['album']['name']
            artists = []
            # print(result['artists'])
            for art in result['artists'][:]:
                artists.append(art['name'])
            
            url = result['external_urls']['spotify']
            pop = result['popularity']
            result = spotify.audio_features(track_id)[0]
            # print(result)
            delete = set(result.keys()) - set(keep_traits)
            
            for trait in delete:
                del result[trait]
            
            for trait in result.keys():
                df.loc[index, trait] = result[trait]
                
            df.loc[index, 'album_name'] = album
            df.at[index, 'artists'] = artists
            df.loc[index,'track_url'] = url
            df.loc[index, 'popularity'] = pop
            push = json.loads(df.iloc[index].to_json())
            # print(push)
            targ_songs.insert_one(push)
            time.sleep(1)
        except:
            not_found.append(json.loads(df.iloc[index].to_json()))

df = df[~df['track_url'].isnull()]     
df.to_json(os.path.join('..', 'Outputs', 'cleaned_data.json'),orient='records')