# Harmonic Horizons

## Overview
Harmonic Horizons is a personal project I built that aimed to recommend a playlist of tracks to users based on their moods.

The idea is to collect a dataset of tracks using the Spotify API and assigning a mood to each one. By working with this data, I was able to extract and analyze insights from the data by focusing on the tracks' audio features, such as danceability and energy. I was then able to leverage these insights to develop a machine learning model that deliver accurate mood predictions to unseen tracks. With the model built, I was able to utilize the Spotify API to develop a recommendation algorithm that outputs songs matching the user mood.

Overall, this project was a way for me to deepen my understanding of APIs and improve my grasp of the data science workflow and machine learning principles. A notebook documenting my entire process can be viewed [here](src/notebooks/eda.ipynb).

## Technologies & Tools
* **Languages**: Python
* **Libraries**:
  * `spotipy`: For accessing and utilizing the Spotify API.
  * `pandas`: For data preprocessing and manipulation.
  * `seaborn`/`matplotlib`: For data visualizations.
  * `scikit-learn`: For building and training machine learning models.
* **API**: Spotify Web API to extract track data and audio features.
* **Development Tools**: PyCharm and Jupyter Notebook
## Features & Functionality
* **Song Recommendation**: The core feature that pulls song data from Spotify based on user's mood and musical preferences.
* **Audio Feature Analysis**: Uses audio features (e.g., energy, tempo, danceability) to classify moods for unseen Spotify tracks.

## Setup & Installation
1. Clone the repository: `git clone https://github.com/Shadooey/harmonic_horizons.git`
2. Navigate to the project directory: `cd harmonic_horizons`
3. Install relevant dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with the following Spotify API credentials:
```txt
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
```
## How to Use
1. Navigate to the directory: `cd src`
2. Run the script:
```bash
python recommend.py
```
3. Input a mood.
4. View the recommendations printed in the terminal.