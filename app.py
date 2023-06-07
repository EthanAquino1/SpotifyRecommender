import time
import spotipy
import requests
import urllib3
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import SpotifyOAuth
from spotipy.exceptions import SpotifyException

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ast
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity



######This can be implemented, however for the sake of the project I will be showcasing one of my playlists. It has been tested
#and successfully run on other playlists once given access to spotify's API.

client_id = "XXXXX"
client_secret = "XXXXX"
redirect_uri= "http://localhost:XXXX/callback/"
username = 'XXXXX'
scope = 'user-top-read playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read playlist-read-private'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri, scope=scope))


my_ids = []
def track_ids(playlist_id):
    playlist1 = sp.user_playlist('footballer100', playlist_id)
    for x in playlist1['tracks']['items'][:100]:
        track = x['track']
        if track is not None and 'id' in track:
            my_ids.append(track['id'])
        else:
            print("Track ID not available")
  

        
my_tracks = []      
def getTrackFeaturesBatch(track_ids):
    tracks = sp.tracks(track_ids)['tracks']
    features = sp.audio_features(track_ids)

    track_features = []
    for i in range(len(tracks)):
        track = tracks[i]
        feature = features[i]
        if track and feature is not None and 'acousticness' in feature:

            track_id = track['id']
            name = track['name']
            album = track['album']['name']
            artist = track['album']['artists'][0]['name']
            release_date = track['album']['release_date']
            length = track['duration_ms']
            popularity = track['popularity']

            acousticness = feature['acousticness']
            danceability = feature['danceability']
            energy = feature['energy']
            instrumentalness = feature['instrumentalness']
            liveness = feature['liveness']
            loudness = feature['loudness']
            speechiness = feature['speechiness']
            tempo = feature['tempo']
            time_signature = feature['time_signature']

            track_info = [track_id, name, album, artist, release_date, length, popularity,
                          danceability, acousticness, energy, instrumentalness,
                          liveness, loudness, speechiness, tempo, time_signature]

            track_features.append(track_info)
        
        else:
            print("Features not available")

    return track_features
 
    
    
###


def get_track_genres(track_ids):
    data = []
    
    for i in range(0, len(track_ids), 50):
        print(f"Processing batch {i//50+1} of {len(track_ids)//50+1}")
        batch_track_info = sp.tracks(track_ids[i:i+50])
        
        for track_info in batch_track_info['tracks']:
            track_id = track_info['id']
            
            artist_id = track_info['artists'][0]['id']
            
            artist_info = sp.artist(artist_id)
            genres = artist_info['genres']
            followers = artist_info['followers']['total']
            popularity = artist_info['popularity']
            
            data.append({'track_id': track_id, 'genres': genres, 'followers': followers, 'popularity': popularity})
            print(f"Processed {track_info}")
            time.sleep(2)
            
        time.sleep(2)
        
        
    
    df = pd.DataFrame(data)
    return df



##########################################

dfspotifyall = pd.read_csv("Data/dfspotifyall.csv")
dfmyspotifyall = pd.read_csv("Data/dfmyspotifyall.csv") #Not needed if we have a user implementing their own playlist


genre_counts = Counter()
for x in range(len(dfspotifyall['genres'])):
    better_list = ast.literal_eval(dfspotifyall['genres'][x])
    genre_counts.update(better_list)
    
popular = genre_counts.most_common(20)

genre_names = []
for x in popular:
    genre_names.append(x[0])
    
genres_key = {}
key = 1
for genre in genre_names:
    genres_key[genre] = key
    key += 1
    
def filter_popular_genres(df, column_name, num_genres=20):
    # Convert genre column to lists
    df[column_name] = df[column_name].apply(ast.literal_eval)
    
    # Count genre occurrences
    genre_counts = Counter()
    for genres in df[column_name]:
        genre_counts.update(genres)
    
    # Get the most popular genres
    popular = genre_counts.most_common(num_genres)
    popular_genres = [genre for genre, _ in popular]
    
    # Add new column with genre classification number
    df['genre_classification'] = df[column_name].apply(lambda x: tuple([popular_genres.index(genre) + 1 for genre in x if genre in popular_genres]))
    
    # Filter the dataframe based on popular genres
    filtered_df = df[df[column_name].apply(lambda x: any(genre in x for genre in popular_genres))]
    
    return filtered_df

filtered_df = filter_popular_genres(dfspotifyall, 'genres')
top_20_genres = filtered_df.reset_index()
top_20_genres = top_20_genres.drop('index', axis=1)

top_20_genres_artists = top_20_genres[top_20_genres['artist'] != "Various Artists"]

def recommondations_on_genre(df1, df2, genre_number):
    vector_columns = ["danceability", "acousticness", "energy", "instrumentalness", "liveness", "loudness", "speechiness", "tempo", "time_signature"]
    
    dataframe1 = df1[vector_columns]
    
    dataframe2temp = df2[df2['genre_classification'].apply(lambda x: genre_number in x)]
    dataframe2 = dataframe2temp[vector_columns]
    
    similarity_matrix = cosine_similarity(dataframe1.values, dataframe2.values)
    
    average_similarity_scores = np.mean(similarity_matrix, axis=0)
    
    top_similar_indices = np.argsort(average_similarity_scores)[-10:][::-1]
    
    top_similar_rows = dataframe2temp.iloc[top_similar_indices]
    
    return top_similar_rows

def get_artist(df, genre_number):
    df_multiple_columns = top_20_genres_artists[['artist', 'followers', 'genre_classification']]
    df = df_multiple_columns.drop_duplicates()
    test_1 = df[df['genre_classification'].apply(lambda x: genre_number in x)]
    lowest_followers = test_1.sort_values('followers').head(5)
    lowest_followers = lowest_followers[['artist', 'followers']]
    return lowest_followers

playlist = ['Pop Playlist']
playlist_id_temp = '4BFmMCmr1lbWgC10XepNic'

#The code commented out would be implemented if a user were to access the spotify API directly, but for the sake of this project one playlist will
#be used to avoid breaching a client secret/running the api too much.

def app():
    
    st.title("Spotify New Genre/Artist Recommender System")
    
    #playlists = sp.current_user_playlists()['items']
    #playlist_names = [playlist['name'] for playlist in playlists]
    #playlist_ids = [playlist['id'] for playlist in playlists]
    
    
    selected_playlist = st.selectbox('Select a playlist', playlist) #Should be: playlist_names

    #selected_playlist_id = playlist_ids[playlist_names.index(selected_playlist)]

    st.write('Selected Playlist ID:', playlist_id_temp) #Should be: selected_playlist_id
    
    #playlist_ids_needed = [selected_playlist_id]
    

    #for playlist_id in playlist_ids_needed:
        #if playlist_id is not None:
            #track_ids(playlist_id)
        #else:
            #continue
            
    #batch_size = 50
    #request_interval = 2  

    #for i in range(0, len(my_ids), batch_size):
        #batch_ids = my_ids[i:i+batch_size]
        #batch_tracks = getTrackFeaturesBatch(batch_ids)
        #my_tracks.extend(batch_tracks)

        #time.sleep(request_interval)

    #df = pd.DataFrame(my_tracks, columns = ['track_id', 'name', 'album', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature']) 
    
    
    #df2 = get_track_genres(my_ids)

    #df = df[~df.duplicated('track_id')]
    #df2 = df2[~df2.duplicated('track_id')]
    #dfmyspotifyall = pd.merge(df, df2, on='track_id')
    #dfmyspotifyall = dfmyspotifyall.reset_index(drop=True)
    
    st.write('Your Playlist')
    
    st.dataframe(dfmyspotifyall)
    
    selected_genre = st.selectbox("Select a genre", genre_names)
    
    
    thegenre = genres_key[selected_genre]   
    
    artistdata = get_artist(top_20_genres, thegenre)
    
    recdata = recommondations_on_genre(dfmyspotifyall, top_20_genres, thegenre)
    
    recdata = recdata[['name', 'album', 'artist', 'release_date', 'genres']]
    
    col1, col2 = st.columns(2)

    col1.subheader("Newer Artists For You to Check Out")
    col1.write(artistdata)

    col2.subheader("Recommended Songs")
    col2.write(recdata)
    

    

if __name__ == '__main__':
    app()
    
