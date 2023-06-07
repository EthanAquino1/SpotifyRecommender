#!/usr/bin/env python
# coding: utf-8

# In[45]:


get_ipython().system('pip install altair')


# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity


# In[ ]:


#Merging song and genre/artist data


# In[2]:


dfspotify = pd.read_csv("playlist_songs_spotify.csv")
dfgenres = pd.read_csv("track_genres.csv")
dfmyspotify = pd.read_csv("my_spotify.csv")
dfmygenres = pd.read_csv("my_genres.csv")


# In[10]:


dfspotify


# In[11]:


dfgenres


# In[12]:


dfmyspotify


# In[13]:


dfmygenres


# In[20]:


dfspotify = dfspotify[~dfspotify.duplicated('track_id')]


# In[21]:


dfgenres = dfgenres[~dfgenres.duplicated('track_id')]


# In[22]:


dfspotifyall = pd.merge(dfspotify, dfgenres, on='track_id')
dfspotifyall = dfspotifyall.reset_index(drop=True)


# In[23]:


dfspotifyall


# In[35]:


dfmyspotify = dfmyspotify[~dfmyspotify.duplicated('track_id')]
dfmygenres = dfmygenres[~dfmygenres.duplicated('track_id')]
dfmyspotifyall = pd.merge(dfmyspotify, dfmygenres, on='track_id')
dfmyspotifyall = dfmyspotifyall.reset_index(drop=True)
dfmyspotifyall


# In[2]:


dfspotifyall.to_csv('dfspotifyall.csv', index=False)
dfmyspotifyall.to_csv('dfmyspotifyall.csv', index=False)


# In[2]:


dfspotifyall = pd.read_csv("dfspotifyall.csv")
dfmyspotifyall = pd.read_csv("dfmyspotifyall.csv")


# In[ ]:


#Getting most common genres in the data


# In[4]:


genre_counts = Counter()
for x in range(len(dfspotifyall['genres'])):
    better_list = ast.literal_eval(dfspotifyall['genres'][x])
    genre_counts.update(better_list)
    
popular = genre_counts.most_common(20)


# In[5]:


popular = genre_counts.most_common(20)


# In[76]:


popular


# In[7]:


genre_names = []
for x in popular:
    genre_names.append(x[0])


# In[8]:


genre_counts = []
for x in popular:
    genre_counts.append(x[1])


# In[78]:


genres_key = {}
key = 1
for genre in genre_names:
    genres_key[genre] = key
    key += 1


# In[84]:


genres_key["classical"]


# In[9]:


sns.barplot(x=genre_names, y=genre_counts)
plt.xlabel('Items')
plt.ylabel('Frequencies')
plt.title('Item Frequencies')
plt.xticks(rotation=90)
plt.show()


# In[ ]:


#Filtering based on popular genres


# In[10]:


def filter_popular_genres(df, column_name, num_genres=20):
    df[column_name] = df[column_name].apply(ast.literal_eval)
    
    genre_counts = Counter()
    for genres in df[column_name]:
        genre_counts.update(genres)
    
    popular = genre_counts.most_common(num_genres)
    popular_genres = [genre for genre, _ in popular]
    
    df['genre_classification'] = df[column_name].apply(lambda x: tuple([popular_genres.index(genre) + 1 for genre in x if genre in popular_genres]))
    
    filtered_df = df[df[column_name].apply(lambda x: any(genre in x for genre in popular_genres))]
    
    return filtered_df


# In[11]:


filtered_df = filter_popular_genres(dfspotifyall, 'genres')


# In[12]:


top_20_genres = filtered_df.reset_index()


# In[13]:


top_20_genres = top_20_genres.drop('index', axis=1)


# In[14]:


top_20_genres


# In[ ]:


#Exploring Artist data and removing "Various Artists" from data


# In[72]:


def plots(df, genre_number):
    filtered_data = df[df['genre_classification'].apply(lambda genre: genre_number in genre)]
    df['highlight'] = df.index.isin(filtered_data.index)

    sns.scatterplot(data=df, x='followers', y='popularity_y', hue='highlight')
    plt.xlabel('Followers')
    plt.ylabel('Popularity')

    df = df.drop('highlight', axis=1)
    
    return plt.gcf()


# In[75]:


my_plot = plots(top_20_genres, 3)
plt.show()


# In[15]:


top_20_genres_artists = top_20_genres[top_20_genres['artist'] != "Various Artists"]


# In[16]:


top_20_genres_artists


# In[ ]:


#Creating a function to recommend the 5 artists with the lowest follower count


# In[19]:


def get_artist(df, genre_number):
    df_multiple_columns = top_20_genres_artists[['artist', 'followers', 'genre_classification']]
    df = df_multiple_columns.drop_duplicates()
    test_1 = df[df['genre_classification'].apply(lambda x: genre_number in x)]
    lowest_followers = test_1.sort_values('followers').head(5)
    lowest_followers = lowest_followers[['artist', 'followers']].reset_index()
    return lowest_followers


# In[20]:


get_artist(top_20_genres, 20)


# In[ ]:


#Content based filtering using cosine similarity on genre


# In[34]:


#df1 is users playlist, and df2 is the spotify data
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
    


# In[86]:


recommondations_on_genre(dfmyspotifyall, top_20_genres, 2)

