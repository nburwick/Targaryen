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

os.environ['SPOTIPY_CLIENT_ID'] = "99b3295c313d45088cb4f8fe0f8dbb81"
os.environ['SPOTIPY_CLIENT_SECRET'] = "ac4fa266a80d43e3beb6b31d2b88dcfb"
os.environ['OAUTH_TOKEN_URL'] = 'https://accounts.spotify.com/api/token'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

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
        result = targ_songs.find({'track_name': song, 'artist' : art})
        
    elif song != "" & art == "":
        result = targ_songs.find({'track_name': song})

    elif song == "" & art != "":
        result = targ_songs.find({'artist': art})
    
    else:
        result = 0 
    if result >= 1:
        return True
    else:
        return False
    

# Get Data per state
@app.route("/api/v1.0/<track>,<artist>,<limit>", methods=['GET'])
def song_data(track="", artist="", limit=10):
    song = str(track)
    art = str(artist)
    lim = int(limit)
    
    if song != "" or art != "":
        if in_mongo(track=song, artist=art) == False:
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