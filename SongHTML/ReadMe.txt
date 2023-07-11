# Targaryen

This 'SongHTML' folder contains 2 python files, 1 html, and 1 csv file. 
I made it so that the HTML can pull the data from Python using Flask (app.py). 
app.py calls simple.py, which is the exported code from jupyter notebook that Lorena just completed for ML.
You can find the exported code in 'Jupyter to Python' folder.

When the HTML page is loaded, it calls Flask to display the form. When user enter information and submit,
it calls Flask again with the /submit, passing in the information user enter.

This call python function called 'getDataset', which takes in 2 parameters : songName and recSongs.
These 2 parameters are used in the python code to produce the outcome.


Instruction on how to run it.
1. download files to your drive
2. open command promp 
3. change directory to where the files are 
4. type: python app.py

	wait until you see the following line: Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
	
5. open a browser and enter the URL above

	Now you should see a webpage with the form with 2 fields
	one for the song name and the other is optional number of recommendations.
	
6. enter a song name, making sure the case matches what is in the csv file.

7. enter number of recommendations, this step is optional. If left blank, 5 will be used for top 5 songs.


