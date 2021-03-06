"""This module will be used to get a list of albums based on an artist's name."""
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

spotify_client_id = os.environ.get('SPOTIFY_CLIENT_ID', '')
spotify_client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
spotify_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                                       client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=spotify_credentials_manager)


def get_artist_list(name):
    """Search for artists based on a query."""
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        for i, artist in enumerate(items):
            print(i, artist['name'])
        return items
    return None


def get_artist(artist_list, idx):
    """Get the id of the artist at index idx in artist_list."""
    return artist_list[idx]


def get_artist_albums(artist, full_album_info=False):
    """Get the albums of the artist."""
    albums = []
    results = sp.artist_albums(artist['id'], album_type='album')
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    print('Total albums:', len(albums))
    unique = set()  # skip duplicate albums
    album_list = []
    for album in albums:
        name = album['name'].lower()
        if name not in unique:
            print(name)
            unique.add(name)
            album_list.append(album)

    if full_album_info:
        return album_list
    return unique
