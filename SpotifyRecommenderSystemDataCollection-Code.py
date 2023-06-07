#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('pip install spotipy')


# In[ ]:


import time
import spotipy
import requests
import urllib3
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import SpotifyOAuth
from spotipy.exceptions import SpotifyException


# In[ ]:


#This is where the token information goes in


# In[ ]:


client_id = "XXXX"
client_secret = "XXXX"
redirect_uri= "http://localhost:XXXX/callback/"
username = 'XXXX'
scope = 'user-top-read playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read playlist-read-private'


# In[ ]:


#Creating the token


# In[ ]:


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri, scope=scope))
                     


# In[ ]:


#This is to to test API rate limiting, if you get rate limited and code stops running this is ran to be able
#to see how much time is left until you can call the API again. 


# In[ ]:


client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

session = requests.Session()
retry = urllib3.Retry(
    respect_retry_after_header=False
)
adapter = requests.adapters.HTTPAdapter(max_retries=retry)

sp = spotipy.Spotify(auth_manager=client_credentials_manager,
                     requests_session=session)

i = 0
while True:
    try:
        res = sp.track('spotify:track:3HPHPoXFupNZXfnFXmiJI5')
    except SpotifyException as e:
        if e.http_status == 429:
            print("'retry-after' value:", e.headers['retry-after'])
            time.sleep(1)
        else:
            break
    print(res['uri'], str(i))
    i += 1


# In[ ]:


#Spotify Playlists


# In[ ]:


playlists_total = sp.user_playlists('spotify')
spotify_playlist_ids = []
while playlists_total:
    for i, playlist in enumerate(playlists_total['items']):
        spotify_playlist_ids.append(playlist['uri'][-22:])
    if playlists_total['next']:
        playlists_total = sp.next(playlists_total)
    else:
        playlists_total = None

spotify_playlist_ids[:20]


# In[ ]:


len(spotify_playlist_ids)


# In[ ]:


#My Playlists


# In[ ]:


playlists = sp.current_user_playlists()


# In[ ]:


playlist_id_me = ["4BFmMCmr1lbWgC10XepNic"]


# In[ ]:


#My Songs


# In[ ]:


my_ids = []
def track_ids(playlist_id):
    playlist1 = sp.user_playlist('footballer100', playlist_id)
    for x in playlist1['tracks']['items'][:100]:
        track = x['track']
        if track is not None and 'id' in track:
            my_ids.append(track['id'])
        else:
            print("Track ID not available")
        
for playlist_id in playlist_id_me:
    if playlist_id is not None:
        track_ids(playlist_id)
    else:
        continue
    
len(my_ids)


# In[ ]:


#Spotify Songs


# In[ ]:


ids = []
def track_ids(playlist_id):
    playlist1 = sp.user_playlist('spotify', playlist_id)
    for x in playlist1['tracks']['items'][:50]:
        track = x['track']
        if track is not None and 'id' in track:
            ids.append(track['id'])
        else:
            print("Track ID not available")
        
for playlist_id in spotify_playlist_ids[:200]:
    if playlist_id is not None:
        track_ids(playlist_id)
    else:
        continue
    
len(ids)


# In[ ]:


#Getting Spotify Song Features, and putting it in dataframe


# In[ ]:


import time

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

batch_size = 50
request_interval = 2  

tracks_test = []
for i in range(0, len(ids), batch_size):
    batch_ids = ids[i:i+batch_size]
    batch_tracks = getTrackFeaturesBatch(batch_ids)
    tracks_test.extend(batch_tracks)
    print(f"Processing tracks {i+1}-{i+len(batch_tracks)}")

    time.sleep(request_interval)

print("All tracks processed successfully.")


# In[ ]:


df = pd.DataFrame(tracks_test, columns = ['track_id', 'name', 'album', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature'])
df.to_csv('playlist_songs_spotify.csv',index=False)


# In[ ]:


df = pd.read_csv('playlist_songs_spotify.csv')


# In[ ]:


df


# In[ ]:


#Taking ids for all the songs and now getting genre and artist data, then putting them into a datafram


# In[ ]:


ids_real = []
for x in df['track_id']:
    ids_real.append(x)


# In[ ]:


len(ids_real)


# In[ ]:


import pandas as pd
import time

def get_track_genres(track_ids, save_file):
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
        df.to_csv(save_file, index=False)
        
    
    df = pd.DataFrame(data)
    return df


save_file = 'progress.csv'
df1 = get_track_genres(ids_real, save_file)



# In[ ]:


df1.to_csv('track_genres.csv', index=False)


# In[ ]:


#Getting My Song Features, and putting it in dataframe


# In[ ]:


import time

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

batch_size = 50
request_interval = 2 

my_tracks = []
for i in range(0, len(my_ids), batch_size):
    batch_ids = my_ids[i:i+batch_size]
    batch_tracks = getTrackFeaturesBatch(batch_ids)
    my_tracks.extend(batch_tracks)
    print(f"Processing tracks {i+1}-{i+len(batch_tracks)}")

    time.sleep(request_interval)

print("All tracks processed successfully.")


# In[ ]:


df = pd.DataFrame(my_tracks, columns = ['track_id', 'name', 'album', 'artist', 'release_date', 'length', 'popularity', 'danceability', 'acousticness', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 'time_signature'])
df.to_csv('my_spotify.csv',index=False)


# In[ ]:


df = pd.read_csv('my_spotify.csv')
df


# In[ ]:


#Taking ids for all the songs and now getting genre and artist data, then putting them into a datafram


# In[ ]:


import pandas as pd
import time

def get_track_genres(track_ids, save_file):
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
        df.to_csv(save_file, index=False)
        
    
    df = pd.DataFrame(data)
    return df


save_file = 'progress_2.csv'
df2 = get_track_genres(my_ids, save_file)


# In[ ]:


df2.to_csv('my_genres.csv', index=False)

