from album_discovery import *
from artist_rating import *
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from api_keys import spotify_client_id, spotify_client_secret

class Recommender:
    def __init__(self):
        return self

    def buildSampleDataset(numUsers=10):
        pass

scm = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=scm)
