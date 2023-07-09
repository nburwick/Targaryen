from flask import Flask, render_template
from flask import request
import simple  # assuming you've converted your notebook to a .py file

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

    recSongs = request.form.get('recommendation')

    # Now, pass song name and recommendation to python function    



    result = simple.getDataset(songName, recSongs)  # Call the function from your notebook
    return render_template('songs.html', result=result)  # Pass the result to your HTML file
    

if __name__ == '__main__':
    app.run(debug=True)
