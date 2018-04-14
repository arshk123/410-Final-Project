Music Rater
===========

Our CS410 Final Project. It uses sentiment analysis and pitchfork reviews to assign an artist a rating, and allows users to rate artists in order to form a content based recommendation system. This project uses the VADER sentiment analysis library available in nltk.

Installation
------------
Clone the repo and install the packages in requirements.txt

After installing, make sure to download the necessary nltk files with the following commands in python:

```python
>> nltk.download('punkt')
>> nltk.download('vader_lexicon')
```

Usage
-----

```python
>> from album_discovery import *
>> from artist_rating import *

>> al = get_artist_list('anderson') # this will get the artists that match a name and print them with indices
u'0 Anderson .Paak'
u'1 Anderson East'
u'2 Keith Anderson'
u'3 John Anderson'
u'4 Lyrica Anderson'
u'5 Leonard Anderson'
u'6 Coffey Anderson'
u'7 Cherine Anderson'
u'8 Carl Anderson'
u'9 Eric Anderson'

>> paak = get_artist(al, 0) # this is basically just indexing a list, probably doesn't need to be its own function

>> albums = get_artist_albums(paak) # get the albums
u'Total albums: 7'
u'yes lawd! remixes'
u'yes lawd!'
u'malibu'
u'venice'

>> reviews = get_pitchfork_reviews(paak['name'], albums) # get the reviews
u'Couldn\'t find venice'

>> get_overall_rating(reviews) # finally, we can use sentiment analysis to get a rating for this artist
u'7.745075112443779'
```
