Music Rater
===========

Our CS410 Final Project. It uses sentiment analysis performed on pitchfork reviews to assign an artist a rating, and allows users to rate artists. Our system uses a combination of content-based filtering and collaborative filterting to recommend new artists to users. More specifically, the recommender system uses the k-nearest neighbors algorithm with cosine similarity metrics .This project uses the VADER sentiment analysis library available in nltk.

Installation
------------
Clone the repo and install the packages in requirements.txt

After installing, make sure to download the necessary nltk files with the following commands in python:

```python
>> import nltk
>> nltk.download('punkt')
>> nltk.download('vader_lexicon')
```

To run the website locally:
```shell
$ git submodule init
$ git submodule update
$ export FLASK_APP=project.py
$ export FLASK_DEBUG=1
$ flask run
```

Usage
-----
```
Database Import/export

https://www.a2hosting.com/kb/developer-corner/postgresql/import-and-export-a-postgresql-database
```
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
