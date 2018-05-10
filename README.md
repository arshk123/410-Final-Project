Music Rater
===========

Our CS410 Final Project. It uses sentiment analysis and pitchfork reviews to assign an artist a rating, and allows users to rate artists in order to form a collaborative recommendation system. This project uses the VADER sentiment analysis library available in nltk.

Installation
------------
Clone the repo and install the packages in requirements.txt

After installing, make sure to download the necessary nltk files with the following commands in python:

```python
>> import nltk
>> nltk.download('punkt')
>> nltk.download('vader_lexicon')
```

Setup for running locally
-------------------------
To run the website locally you first need to sign up for a spotify API key [here](https://beta.developer.spotify.com/). You also need to import the postgres database from the "db" folder using the information [here](https://www.a2hosting.com/kb/developer-corner/postgresql/import-and-export-a-postgresql-database). Assuming your main postgres user is "postgres" with no password, the following is the code to run the website locally.

```shell
$ git submodule init
$ git submodule update
$ export FLASK_APP=project.py
$ export FLASK_DEBUG=1
$ export SPOTIFY_CLIENT_ID=<client id from API>
$ export SPOTIFY_CLIENT_SECRET=<client secret from API>
$ export DATABASE_URL=postgres://postgres@localhost/<dbname>
$ flask run
```

Usage
-----
```
Database Import/export

https://www.a2hosting.com/kb/developer-corner/postgresql/import-and-export-a-postgresql-database
```


Using the components
--------------------
To use the components for creating an artist review rating you can do the following.

```python
>> from album_discovery import *
>> from artist_rating import *

>> al = get_artist_list('anderson') # this will get the artists that match a name and print them with indices
0 Anderson .Paak
1 Anderson East
2 Keith Anderson
3 John Anderson
4 Lyrica Anderson
5 Leonard Anderson
6 Coffey Anderson
7 Cherine Anderson
8 Carl Anderson
9 Eric Anderson

>> paak = get_artist(al, 0) # this is basically just indexing a list, probably doesn't need to be its own function

>> albums = get_artist_albums(paak) # get the albums
Total albums: 7
yes lawd! remixes
yes lawd!
malibu
venice

>> reviews = get_pitchfork_reviews(paak['name'], albums) # get the reviews
Couldn't find venice

>> get_overall_rating(reviews) # finally, we can use sentiment analysis to get a rating for this artist
7.745075112443779

# Alternatively, there is an easier option in artist_rating that just selects the first artist and spits out a rating
>> get_rating_from_query('anderson')
0 Anderson .Paak
1 Anderson East
2 Keith Anderson
3 John Anderson
4 Lyrica Anderson
5 Leonard Anderson
6 Coffey Anderson
7 Cherine Anderson
8 Carl Anderson
9 Eric Anderson
Total albums: 7
yes lawd! remixes
yes lawd!
malibu
venice
Couldn't find venice
7.745075112443779

# The function above in turn calls a streamlined function for getting a rating directly from the artist object
>> get_rating_from_artist(paak)
Total albums: 7
yes lawd! remixes
yes lawd!
malibu
venice
Couldn't find venice
7.745075112443779
```

It's infeasible to use the recommender unless you have the database set up properly and it actually has some data in it. Once you do, we have included the code to get recommendations below.

```python
>>> import recommender
>>> rec = recommender.Recommender()
Computing the cosine similarity matrix...
Done computing similarity matrix.
# There's a lot more debugging output after this
>>> rec.recommend(7) # it's as simple as calling the recommend function with an argument of user id
# This returns a list of recommended artists
['16yUpGkBRgc2eDMd3bB3Uw', '2h93pZq0e7k5yf4dywlkpM', '14x0FyR1UMUO1Sc8V5TzN6', '3koiLjNrgRTNbOwViDipeA', '329iU5aUf9pGiYFbjE9xqQ', '1U1el3k54VvEUzo3ybLPlM']
```