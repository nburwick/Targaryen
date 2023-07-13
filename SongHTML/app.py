from flask import Flask, render_template, url_for
from flask import request
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from songRecommender import songRecommender
import os
from spotify_creds import cid, secret, sp_uri, mdb_uri
import json
    
# Set Environment
cid = cid
secret = secret
sp_uri = sp_uri
os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = sp_uri

# Create mongo
mdb_uri = mdb_uri
server = ServerApi('1')
# Create a new client and connect to the server
mongo = MongoClient(mdb_uri, server_api=server)
database = mongo['targ_data']
targ_songs = database['song_data']
songs = list(targ_songs.find({}))

#Define DataBase Search
def in_mongo(track_id):
    try:    
        result = list(targ_songs.find({'track_id' : track_id}))
        if result != 0 or pd.isnull(result) == False:
            return True
        else:
            return False
    except:
        return False

# set directory
app_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))

#Initiate App
app = Flask(__name__, static_folder=f"{app_dir}")
CORS(app)

#this is loaded when page is loaded
@app.route('/')
def home():
    #use this for just displaying page that does nothing
    return render_template('songs.html')

#this is loaded when user enter song name, etc
@app.route('/submit', methods=['POST'])
def submit():
    #Initiate Spotify Client
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    spotify = spotipy.Spotify(auth_manager=client_credentials_manager, retries=1, requests_timeout=3)

    # Capture user input
    songName = request.form.get('songName')
    artistName = request.form.get('artist')
    recSongs = request.form.get('recommendation')
    explicit_filter = request.form['choice']

    # Search Spotify for song
    result = spotify.search(f'track:{songName} artist:{artistName}')
    
    # Get Attributes To upload to MongoDB if a new track
    songID = result['tracks']['items'][0]['id']
    explicit = result['tracks']['items'][0]['explicit']
    pop = result['tracks']['items'][0]['popularity']
    name = result['tracks']['items'][0]['name']
    track_art = result['tracks']['items'][0]['artists'][0]['name']
    url = result['tracks']['items'][0]['external_urls']['spotify']
    
    # Test MongoDB for DataPoint
    if in_mongo(songID) == False:
        # in_mongo returned False Add Song to MongoDB with Attributes
        traits_dictionary = spotify.audio_features(songID)[0]
        traits_dictionary['popularity'] = pop
        traits_dictionary['explicit'] = explicit
        traits_dictionary['track_name'] = name
        traits_dictionary['track_url'] = url
        traits_dictionary['artists'] = track_art
        traits_dictionary['track_id'] = songID
        keep_traits = ['track_id', 'artists', 'track_name',
                       'popularity', 'duration_ms', 'explicit', 'danceability',
                       'energy', 'key', 'loudness', 'mode','speechiness',
                       'acousticness','instrumentalness','liveness','valence',
                       'tempo','time_signature']
        
        # Establish Traits to remove from API Response for Push
        delete_list = set(traits_dictionary.keys()) - set(keep_traits)
        for trait in delete_list:
            del traits_dictionary[trait]
            
        # Push Song into MongoDB to "Smarten" Model    
        targ_songs.insert_one(traits_dictionary)

    else:
        # in_mongo returned True extract data from MongoDB
        traits_dictionary = list(targ_songs.find({'track_id': songID}))[0]
    
    # vectorize values for Machine Learning 
    for trait in traits_dictionary.keys():
        traits_dictionary[trait] = [traits_dictionary[trait]]

    # Now, pass songID, Song DB, Song Attributes, and number of recommendations to ML Model Function   
    result = songRecommender(songID, songs, traits_dictionary, recSongs, explicit_filter)
    
    # Return Recommended Songs as Pandas DataFrame
    return render_template('songs.html', tables=[result.to_html(classes='mystyle',header='true', 
                                                                index=True, justify='left', escape=False)])
    
# Run Application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
