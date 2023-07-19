from flask import Flask, render_template, url_for
from flask import request
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
<<<<<<< HEAD
from spotipy.cache_handler import MemoryCacheHandler
=======
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
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
<<<<<<< HEAD
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret, cache_handler=MemoryCacheHandler())
=======
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed

# Create mongo
mdb_uri = mdb_uri
server = ServerApi('1')
# Create a new client and connect to the server
mongo = MongoClient(mdb_uri, server_api=server)
database = mongo['targ_data']
targ_songs = database['song_data']
<<<<<<< HEAD


#Define DataBase Search
def in_mongo(track_name, artists):
    try:    
        result = list(targ_songs.find({'track_name' : track_name, 'artists' : artists}))
        if len(result) > 0:
=======
songs = list(targ_songs.find({}))

#Define DataBase Search
def in_mongo(track_id):
    try:    
        result = list(targ_songs.find({'track_id' : track_id}))
        if len(result) != 0 or pd.isnull(result) == False:
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
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
<<<<<<< HEAD
    songs = list(targ_songs.find({}))
    #Initiate Spotify Client
    spotify = spotipy.Spotify(auth_manager=client_credentials_manager)
=======
    #Initiate Spotify Client
    client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    spotify = spotipy.Spotify(auth_manager=client_credentials_manager, retries=1, requests_timeout=3)
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed

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
<<<<<<< HEAD
    artists = []
    track_arts = result['tracks']['items'][0]['artists']
    for art in track_arts:
        artists.append(art['name'])
    url = result['tracks']['items'][0]['external_urls']['spotify']
    preview = result['tracks']['items'][0]['preview_url']
    
    # Test MongoDB for DataPoint
    if in_mongo(name, artists) == False:
=======
    track_art = result['tracks']['items'][0]['artists'][0]['name']
    url = result['tracks']['items'][0]['external_urls']['spotify']
    
    # Test MongoDB for DataPoint
    if in_mongo(songID) == False:
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
        # in_mongo returned False Add Song to MongoDB with Attributes
        traits_dictionary = spotify.audio_features(songID)[0]
        traits_dictionary['popularity'] = pop
        traits_dictionary['explicit'] = explicit
        traits_dictionary['track_name'] = name
        traits_dictionary['track_url'] = url
<<<<<<< HEAD
        traits_dictionary['artists'] = artists
        traits_dictionary['track_id'] = songID
        traits_dictionary['preview_url'] = preview
        keep_traits = ['track_id', 'track_name', 'artists', 'track_url', 'preview_url',
=======
        traits_dictionary['artists'] = track_art
        traits_dictionary['track_id'] = songID
        keep_traits = ['track_id', 'artists', 'track_name',
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
                       'popularity', 'duration_ms', 'explicit', 'danceability',
                       'energy', 'key', 'loudness', 'mode','speechiness',
                       'acousticness','instrumentalness','liveness','valence',
                       'tempo','time_signature']
        
        # Establish Traits to remove from API Response for Push
        delete_list = set(traits_dictionary.keys()) - set(keep_traits)
        for trait in delete_list:
            del traits_dictionary[trait]
<<<<<<< HEAD
        
        # Push Song into MongoDB to "Smarten" Model    
        targ_songs.insert_one(traits_dictionary)
        print("NEW TRACK ADDED")
        print(traits_dictionary)
=======
            
        # Push Song into MongoDB to "Smarten" Model    
        targ_songs.insert_one(traits_dictionary)
        print("NEW TRACK ADDED")
        global songs 
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
        songs = list(targ_songs.find({}))

    else:
        # in_mongo returned True extract data from MongoDB
        print(list(targ_songs.find({'track_id': songID})))
        traits_dictionary = list(targ_songs.find({'track_id': songID}))[0]
    
    # vectorize values for Machine Learning 
    for trait in traits_dictionary.keys():
        traits_dictionary[trait] = [traits_dictionary[trait]]
<<<<<<< HEAD
        
    searched = pd.DataFrame(traits_dictionary)
    
        # Create Clickable Links & Clean Artists
    for index, track in searched.iterrows():
      searched.loc[index,'track_name'] = f'<a href={track["track_url"]}>{track["track_name"]}</a>'
      arts = str(track['artists']).strip("][").split(", ")
      searched.loc[index, 'artists'] = ", ".join(arts).replace("'","")
      if not pd.isnull(track['preview_url']):
        searched.loc[index, 'preview'] = f"<audio src='{track['preview_url']}' controls type='audio/mpeg'>"
      else:
        searched.loc[index,'preview'] = "Preview Unavailable"
    
    searched = searched[['track_name', 'artists', 'preview']].to_html(classes='mystyle', header='true',index=False, justify='left', escape=False)
    search="<h1>SongVue Search</h1>" + searched
=======

>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
    # Now, pass songID, Song DB, Song Attributes, and number of recommendations to ML Model Function   
    result = songRecommender(songID, songs, traits_dictionary, recSongs, explicit_filter)
    
    # Return Recommended Songs as Pandas DataFrame
<<<<<<< HEAD
    return render_template('songs.html', search=[search],tables=[result.to_html(classes='mystyle',header='true', 
=======
    return render_template('songs.html', tables=[result.to_html(classes='mystyle',header='true', 
>>>>>>> e3dce1ed9c6d71ad67025bd28c561c3dfadafaed
                                                                index=True, justify='left', escape=False)])
    
# Run Application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
