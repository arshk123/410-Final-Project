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