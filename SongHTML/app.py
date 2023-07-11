from flask import Flask, render_template
from flask import request
import simple  # assuming you've converted your notebook to a .py file
import songRecommender
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

cid = "5ffe619ae7b54de8a74983f0f7663d19"
secret = "c0610f5f0ca04b6d884d9495ce0073c6"
uri = "http://localhost:8080"

os.environ['SPOTIPY_CLIENT_ID'] = cid
os.environ['SPOTIPY_CLIENT_SECRET'] = secret
os.environ['SPOTIPY_REDIRECT_URI'] = uri

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
spotify = spotipy.Spotify(auth_manager=client_credentials_manager, retries=3, requests_timeout=3)

app = Flask(__name__)

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
    # 'songName' is the 'id' value
    songName = request.form.get('songName')

    artistName = request.form.get('artist')

    print(artistName)

    result = spotify.search(f'track:{songName} artist:{artistName}')
    songID = result['tracks']['items'][0]['id']
    pop = result['tracks']['items'][0]['popularity']

    print(songID)

    traits_dictionary = spotify.audio_features(songID)[0]
    traits_dictionary['popularity'] = pop

    delete_list = ['analysis_url','id','duration_ms','track_href','type','uri']
    for trait in delete_list:
        del traits_dictionary[trait]

    #print(traits_dictionary)
    # {
    # 'popularity': [100],
    # 'explicit': [False],
    # 'danceability': [0.714],
    # 'energy': [0.472],
    # 'key': [2],
    # 'loudness':[-7.375],
    # 'mode':1,
    # 'speechiness':[0.0864],
    # 'acousticness': [0.013],
    # 'instrumentalness':[0.00000451],
    # 'liveness':[0.266],
    # 'valence':[0.238],
    # 'tempo':[131.121],
    # 'time_signature':[4]
    # } 

#     {'acousticness': 0.013,
#  'analysis_url': 'https://api.spotify.com/v1/audio-analysis/3nqQXoyQOWXiESFLlDF1hG',
#  'danceability': 0.714,
#  'duration_ms': 156943,
#  'energy': 0.472,
#  'id': '3nqQXoyQOWXiESFLlDF1hG',
#  'instrumentalness': 4.51e-06,
#  'key': 2,
#  'liveness': 0.266,
#  'loudness': -7.375,
#  'mode': 1,
#  'speechiness': 0.0864,
#  'tempo': 131.121,
#  'time_signature': 4,
#  'track_href': 'https://api.spotify.com/v1/tracks/3nqQXoyQOWXiESFLlDF1hG',
#  'type': 'audio_features',
#  'uri': 'spotify:track:3nqQXoyQOWXiESFLlDF1hG',
#  'valence': 0.238}

    recSongs = request.form.get('recommendation')

    # Now, pass song name and recommendation to python function    
    result = songRecommender.songRecommender(songID, traits_dictionary, recSongs)  # Call the function from your notebook
    return render_template('songs.html', tables=[result.to_html(classes='data',header='true', index=False, justify='left')])  # Pass the result to your HTML file
    

if __name__ == '__main__':
    app.run(debug=True)
