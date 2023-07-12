from flask import Flask, render_template
from flask import request
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from songRecommender import songRecommender
import os
    
# Set Environment
cid = "99b3295c313d45088cb4f8fe0f8dbb81"
secret = "d6ef161517e24039bab481b7b0b99732"
sp_uri = "http://localhost:8080"
os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = sp_uri

# Create mongo
mdb_uri = 'mongodb+srv://nburwick:Swim_Fast01@cluster0.nvujnf4.mongodb.net/?retryWrites=true&w=majority'
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
        if result != 0:
            return True
        else:
            return False
    except:
        return False

#Initiate App
app = Flask(__name__)
CORS(app)

#this is loaded when page is loaded
@app.route('/')
def home():
   # result = simple.getDataset('ABC')  # Call the function from your notebook
    #return render_template('songs.html', result=result) 
    
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

    # Search Spotify for song
    result = spotify.search(f'track:{songName} artist:{artistName}')
    
    # Get Attributes
    songID = result['tracks']['items'][0]['id']
    explicit = result['tracks']['items'][0]['explicit']
    pop = result['tracks']['items'][0]['popularity']
    name = result['tracks']['items'][0]['name']
    track_art = result['tracks']['items'][0]['artists'][0]['name']
    url = result['tracks']['items'][0]['external_urls']['spotify']
    
    # Test MongoDB for DataPoint
    if in_mongo(songID) == False:
        # print("DB Check returned False")
        traits_dictionary = spotify.audio_features(songID)[0]
        print(traits_dictionary)
        traits_dictionary['popularity'] = pop
        traits_dictionary['explicit'] = explicit
        traits_dictionary['track_name'] = name
        traits_dictionary['track_url'] = url
        targ_songs.insert_one(traits_dictionary)
        delete_list = ['analysis_url','id','duration_ms','track_href','type','uri', 'track_name']
        for trait in delete_list:
            del traits_dictionary[trait]
    else:
        # print("DB Check returned True")
        traits_dictionary = list(targ_songs.find({'track_id': songID}))[0]
    
    # vectorize values for Machine Learning 
    for trait in traits_dictionary.keys():
        traits_dictionary[trait] = [traits_dictionary[trait]]


    # Now, pass song name and recommendation to python function    
    result = songRecommender(songID, songs, traits_dictionary, recSongs)  # Call the function from your notebook
    return render_template('songs.html', tables=[result.to_html(classes='data',header='true', index=False, justify='left', escape=False)])  # Pass the result to your HTML file
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
