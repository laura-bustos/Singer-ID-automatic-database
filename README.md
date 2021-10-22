# Singer ID automatic database generator

This repository contains the code to automatically generate a music database from Spotify's API. 

The main purpose of this database generator is to solve the lack of music anotated databases for AI project's development which work with music files. Helping the investigation related to music genre estimation, singer identification, singer recognition...

This repository generates:
  - A log file containing the musical genres, the artists per genre and the title of each song. 
  - A csv file containing information related to general songs' data (artist, musical genre, song title and album) and songs' musical features provided by Spotify's     API such as acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness, tempo and valence.
  - Access to the 30 seconds' preview of each song provided by Spotify's API.
  - Access to the vocals and the accompainment stemms of each song.

The database is set to work with the 5 most popular musical genres women artists': Pop, Rock, Jazz, R&B and Indie. 

## Additional requirements

- Have a Spotify's API developer account and set the parameter values "client_id" and "client_secret" to link the code to your own account.

- Set the number of songs per artists that is required to have in the dataset with "num_songs_artist".

- Set the number of songs that is required to have in the dataset "size_dataset".
