"""Testing things related to getting artist data."""
from api_keys import spotify_client_id, spotify_client_secret
import pitchfork
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

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


def get_pitchfork_reviews(artist_name, album_names):
    """Get the artists reviews from pitchfork."""
    reviews = []
    for album_name in album_names:
        try:
            review = pitchfork.search(artist_name, album_name)
            reviews.append(review)
        except IndexError:
            print("Couldn't find {}".format(album_name))
    return reviews
