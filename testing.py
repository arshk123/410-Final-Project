"""Testing things related to getting artist data."""
import musicbrainzngs as mbz
import discogs_client as discog
from api_keys import spotify_client_id, spotify_client_secret, discogs_token
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

mbz.set_useragent('Music Rater', '0.1')
mbz.set_hostname('beta.musicbrainz.org')
d = discog.Client('Music Rater/0.1', user_token=discogs_token)
spotify_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                                       client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=spotify_credentials_manager)


# def get_artist_list(query):
#     """Search for artists based on a query."""
#     result = mbz.search_artists(artist=query)
#     artist_list = result['artist-list']
#     for i, artist in enumerate(artist_list):
#         print(i, artist['name'])
#     return artist_list


# def get_artist_id(artist_list, idx):
#     """Get the id of the artist at index idx in artist_list."""
#     return artist_list[idx]['id']


# def get_albums(artist_id):
#     """Get the albums from an artist based on their id."""
#     results = mbz.browse_release_groups(artist=artist_id,
#                                   release_status=['official'],
#                                   includes=['labels'],
#                                   release_type=['album', 'ep'],
#                                   limit=100)
#     releases = results['release-group-list']
#     return releases

# def get_artist_list(query):
#     """Search for artists based on a query."""
#     result = d.search(query, type='artist')
#     if len(result) > 15:
#         artist_list = [result[i] for i in range(15)]
#     else:
#         artist_list = result
#     for i, artist in enumerate(artist_list):
#         print(i, artist.name)
#     return artist_list


# def get_artist_id(artist_list, idx):
#     """Get the id of the artist at index idx in artist_list."""
#     return artist_list[idx]['id']


# def get_albums(artist_id):
#     """Get the albums from an artist based on their id."""
#     results = mbz.browse_releases(artist=artist_id,
#                                   release_status=['official'],
#                                   includes=['labels'],
#                                   release_type=['album', 'ep'],
#                                   limit=100)
#     releases = results['release-list']
#     return releases

def get_artist_list(name):
    """Search for artists based on a query."""
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        for i, artist in enumerate(items):
            print(i, artist['name'])
        return items
    return None


def get_artist_id(artist_list, idx):
    """Get the id of the artist at index idx in artist_list."""
    return artist_list[idx]


def get_artist_albums(artist):
    """Get the albums of the artist."""
    albums = []
    results = sp.artist_albums(artist['id'], album_type='album')
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
    print('Total albums:', len(albums))
    unique = set()  # skip duplicate albums
    for album in albums:
        name = album['name'].lower()
        if name not in unique:
            print(name)
            unique.add(name)
    return unique
