# Import Dependencies
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask import Flask, jsonify
from flask_cors import CORS
import datetime as dt
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Database setup
# Create mongo
uri = 'mongodb+srv://nburwick:Swim_Fast01@cluster0.nvujnf4.mongodb.net/?retryWrites=true&w=majority'
server = ServerApi('1')
# Create a new client and connect to the server
mongo = MongoClient(uri, server_api=server)
database = mongo['targ_data']
targ_songs = database['song_data']

app = Flask(__name__)
CORS(app)


def in_mongo(track="", artist=""):
    song = str(track)
    art = str(artist)
    if song != "" & art != "":
        
    elif song != "" & art == "":
        
    else:
         return False
# Get Data per state
@app.route("/api/v1.0/<track>,<artist>,<limit>", methods=['GET'])
def song_data(track="", artist="", limit=10):
    song = str(track)
    art = str(artist)
    lim = int(limit)
    
    if in_mongo(song, art) == False:
        try:
            if song != "" & art != "":
                results = spotify.search(f'track:{song} artist:{art}')
                song_id = results['tracks']['items'][0]['id']
                pop = results['tracks']['items'][0]['popularity']
            elif song != "" & art == "":
                results = spotify.search(f'track:{song}')
                song_id = results['tracks']['items'][0]['id']
                pop = results['tracks']['items'][0]['popularity']
            elif song == "" & art != "":
                results = spotify.search(f'artist:{art}')
                results = spotify.album_tracks(results['tracks']['items'][0]['album']['id'], limit=1)
                song_id = results['items'][0]['id']
                pop = results['tracks']['items'][0]['popularity']
            elif song == "" & art == ""
                df = pd.json_normalize(targ_songs.find({}))
                df = df.sort_values(by='popularity').head(lim)
                return df[['track_name', 'artist']].to_html()
        except:
                df = pd.json_normalize(targ_songs.find({}))
                df = df.sort_values(by='popularity').head(lim)
                return df[['track_name', 'artist']].to_html()
    else:
        df = pd.json_normalize(targ_songs.find({}))
        df = df.sort_values(by='popularity').head(lim)
        return df[['track_name', 'artist']].to_html()        
        




    
    
# Initiate App
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)