Music Rater
===========

Our CS410 Final Project. It uses sentiment analysis performed on pitchfork reviews to assign an artist a rating, and allows users to rate artists. Our system uses a combination of content-based filtering and collaborative filterting to recommend new artists to users. More specifically, the recommender system uses the k-nearest neighbors algorithm with cosine similarity metrics .This project uses the VADER sentiment analysis library available in nltk.

The project is implemented as a web app using python and Flask for everything on the backend. Most of the frontend was created using the Bootstrap framework along with basic HTML, CSS, and JavaScript. The code for the recommendation system can be found in the recommender.py file, and the code that performs sentiment analysis and generates a rating for each artist is in the artist_rating.py file. Most of the functions in these files are called from the project.py. This file is where each of the endpoints for the website live, and it is where the majority of the data formatting and serving of the webpages occurs.

Individual Contributions

Ryan (rgates3): Design and implementation of front end, initial setup and deployment to Heroku, helping create and edit video presentation

Tejas (tsharm5): Writing code that performs sentiment analysis on pitchfork, creation of webpages on the front end, writing various scripts for database population, helping create and edit video presentation

Arsh (khndlwl3): Design and implementation of recommendation system (Hybrid Collaborative and Content Based), design and implementation of database, helping create video presentation

Overview of all Technology Used
------------
### Programming Languages Used
Python

HTML and CSS

JavaScript

### Frameworks
Flask

Bootstrap

### Libraries Used
Spotipy (for access to Spotify API)

Pitchfork submodule (for access to Pitchfork reviews)

NLTK (for VADER sentiment analysis)

Surprise (for recommender system)

Psycopg2 (for Database Queries)

Pandas

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

It's infeasible to use the recommender unless you have the database set up properly and it actually has some data in it. Once you do, we have included the code to get recommendations below. Upon creation of a new Recommender object, the whole database is
queried and the recommender is retrained and evaluated, all recommendations are then inserted into the database recommendations table. The reason we did it this way is because we know we don't have too much data, and we wanted to ensure the most up to date
recommendations are given to our users. As such, we wrote this recommender such that whenever a recommendation isn't found in the database e.g. a new user signs up, we reevaluate the recommendations to update them.

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
