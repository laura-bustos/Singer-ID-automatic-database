import spotipy
from spotipy.oauth2 import SpotifyClientCredentials 

from os import environ

import pandas as pd
from typing import List, Dict

import requests

import numpy as np

import os, datetime

from spleeter.separator import Separator

# Use audio loader explicitly for loading audio waveform :
from spleeter.audio.adapter import AudioAdapter

from bs4 import BeautifulSoup as bs
import json

# Spotify API authentication
client_id = ""
client_secret = ""
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Number of tracks available in the playlist
def get_pl_length(sp: spotipy.client.Spotify, pl_uri: str) -> int:
    return sp.playlist_tracks(
        pl_uri,
        offset=0,
        fields="total"
    )["total"]


# Get all the artist info about each track of the playlist.
def get_tracks_artist_info(sp: spotipy.client.Spotify, pl_uri: str) -> List[List[Dict]]:
    artists_info = list()
    # Start retrieving tracks from the beginning of the playlist
    offset = 0
    pl_length = get_pl_length(sp, pl_uri)

    # Playlist track retrieval only fetches 100 tracks at a time, hence
    # the loop to keep retrieving until we reach the end of the playlist
    while offset != pl_length:
        # Get the next batch of tracks
        pl_tracks = sp.playlist_tracks(
            pl_uri,
            offset=offset,
            fields="items.track"
        )

        # Get the list with the info about the artists of each track from the\
        # latest batch and append it to the running list
        [artists_info.append(pl_item["track"]["artists"])
            for pl_item in pl_tracks["items"]]

        # Update the offset
        offset += len(pl_tracks["items"])

    return artists_info

# Calculate the frequency of each artist in the playlist
def get_artist_counts(artists_info: List[List[Dict]]) -> Dict[str, int]:
    artist_counts = dict()

    # Loop through the lists of artist information
    for track_artists in artists_info:
        # Loop through the artists associated with the current track
        for artist in track_artists:
            # Update the current artist's frequency
            artist_name = artist["name"]
            if artist_name in artist_counts:
                artist_counts[artist_name] += 1
            else:
                artist_counts[artist_name] = 1

    return artist_counts

def get_track_features(track_id, token=None): 
    url = "https://api.spotify.com/v1/audio-features/"+track_id
    with requests.session() as sesh:
        header = {"Authorization": "Bearer {}".format(token)}
        response = sesh.get(url, headers=header)
        sfeature = str(bs(response.content, "html.parser"))
        return json.loads(sfeature)

# Playlists URIs to look up:

# WOMEN OF POP
pl_uri1 = "spotify:playlist:37i9dQZF1DX3WvGXE8FqYX"

# WOMEN OF ROCK
pl_uri2 = "spotify:playlist:37i9dQZF1DXd0ZFXhY0CRF"

# WOMEN OF JAZZ
pl_uri3 = "spotify:playlist:37i9dQZF1DX5OepaGriAIm"

# WOMEN OF R&B
pl_uri4 = "spotify:playlist:37i9dQZF1DX1wNY9tfWQsS"

# WOMEN OF INDIE
pl_uri5 = "spotify:playlist:37i9dQZF1DX91UQmVbQYyN"

# Las 5 playlists
pl_uri = [pl_uri1, pl_uri2, pl_uri3, pl_uri4, pl_uri5]

playlist_dict = {
    0: 'POP',
    1: 'ROCK',
    2: 'JAZZ',
    3: 'R&B',
    4: 'INDIE'
}

# Spleeter separator loader
# Using embedded configuration.
separator = Separator('spleeter:2stems')

# RAW waveform based separation
audio_loader = AudioAdapter.default()
sample_rate = 44100

df_genre = []
df_artists = []
df_albums = []
df_songs = []
df_ids = []
df_preview_urls = []
df_acousticness = []
df_danceability = []
df_energy = []
df_instrumentalness = []
df_liveness = []
df_loudness = []
df_speechiness = []
df_tempo = []
df_valence = []

f = open("log.txt", "w")

# Check each playlist
for i in range(len(pl_uri)):

    print('NEW PLAYLIST: '+ playlist_dict[i])
    f.write('\n\nNEW PLAYLIST: '+ playlist_dict[i])

    # Get the artist information for all tracks of the playlist
    artists_info = get_tracks_artist_info(sp, pl_uri[i])

    # Get the frequencies of each artist
    artists_counts = get_artist_counts(artists_info)

    # Get a list of the artists featured in the playlist
    artists_in_playlist = list(artists_counts.keys())

    # Maximum number of artists from each music style 
    num_artists_in_pl = 50

    num_artists_inserted = 0

    # In each playlist check each artist
    for j in range(len(artists_in_playlist)):  

        # Search for the artist's information
        singer = artists_in_playlist[j]
        f.write('\n' + singer)
        result = sp.search(singer)

        #Extract Artist's uri and check if it retrieves an error
        try:
            artists_uris = result['tracks']['items'][0]['artists'][0]['uri']
        except IndexError:
            break

        results = sp.artist_top_tracks(artists_uris)

        count_ok2 = 0
        songs_diferentes = []
        for track in results['tracks']:
            # If a song doesn't have a preview url, take the next
            if track['id'] not in songs_diferentes and track['id'] not in df_ids and track['preview_url'] is not None :
                url = track['preview_url']
                r = requests.get(url, allow_redirects=True)
                if len(r.content) > 0:
                    songs_diferentes.append(track)
                    count_ok2 = count_ok2 + 1
                else:
                    continue
            else:
                continue

        # Number of songs per artist
        num_songs_artist = ""

        # Size of songs in the dataset
        size_dataset = ""

        if count_ok2 >= num_songs_artist:
            # insert singer in the database
            num_artists_inserted = num_artists_inserted + 1
            # check if the number of artists inserted from a playlist is less than max number of artists per genre
            if num_artists_inserted <= num_artists_in_pl and len(songs_diferentes) >= 5:
                in_songs = 0
                for track in songs_diferentes:
                    # If a song doesn't have a preview url, take the next
                    if len(df_artists) < size_dataset and in_songs < num_songs_artist and track['preview_url'] is not None:
                        f.write('\n\t- ' + track['name'])
                        in_songs = in_songs + 1
                        #Track musical genre
                        df_genre.append(playlist_dict[i])
                        # Insert singer name
                        df_artists.append(singer)
                        #Track name
                        df_songs.append(track['name'])
                        # Track id
                        df_ids.append(track['id'])
                        #Track preview url
                        df_preview_urls.append(track['preview_url'])
                        #Download of the mp3 preview
                        url = track['preview_url']
                        r = requests.get(url, allow_redirects=True)
                        open('./originals/' + track['id'] + '.mp3', 'wb').write(r.content)
                        # Source separate the audio track
                        waveform, _ = audio_loader.load('./originals/' + track['id'] + '.mp3', sample_rate=sample_rate)
                        # Perform the separation :
                        prediction = separator.separate(waveform)
                        separator.separate_to_file('./originals/' + track['id'] + '.mp3', './separated/')
                        # Track album
                        df_albums.append(track['album']['name'])  
                        # Musical features
                        features = sp.audio_features(track['id'])
                        # Track Acousticness
                        df_acousticness.append(features[0]['acousticness'])
                        # Track Danceability
                        df_danceability.append(features[0]['danceability'])
                        # Track Energy
                        df_energy.append(features[0]['energy'])
                        # Track Instrumentalness
                        df_instrumentalness.append(features[0]['instrumentalness'])
                        # Track Liveness
                        df_liveness.append(features[0]['liveness'])
                        # Track Loudness
                        df_loudness.append(features[0]['loudness'])
                        # Track Speechiness
                        df_speechiness.append(features[0]['speechiness'])
                        # Track Tempo
                        df_tempo.append(features[0]['tempo'])
                        # Track Valence
                        df_valence.append(features[0]['valence'])
                    else:
                        continue
            else:
                break
        else:
            continue

f.close()

# Create a dictionary for the dataframe with the name of the artists, songs, song ids, song urls and albums
data = {
    "Musical Genre" : df_genre,
    "Artist" : df_artists,
    "Song" : df_songs,
    "Song ID" : df_ids,
    "Song URL" : df_preview_urls,
    "Album" : df_albums,
    "Acousticness" : df_acousticness,
    "Danceability" : df_danceability,
    "Energy" : df_energy,
    "Instrumentalness" : df_instrumentalness,
    "Liveness" : df_liveness,
    "Loudness" : df_loudness,
    "Speechiness" : df_speechiness,
    "Tempo" : df_tempo,
    "Valence" : df_valence
}

# Create the dataframe and save it as CSV (without indices) with the artists from the playlists
df_completo = pd.DataFrame(data=data)

df_completo.to_csv("artists_completo.csv", index=False)
