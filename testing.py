"""Testing things related to getting artist data."""
import musicbrainzngs as mbz

mbz.set_useragent('Music Rater', '0.1')
mbz.set_hostname('beta.musicbrainz.org')


def get_artist_list(query):
    """Search for artists based on a query."""
    result = mbz.search_artists(artist=query)
    artist_list = result['artist-list']
    for i, artist in enumerate(artist_list):
        print(i, artist['name'])
    return artist_list


def get_artist_id(artist_list, idx):
    """Get the id of the artist at index idx in artist_list."""
    return artist_list[idx]['id']


def get_albums(artist_id):
    """Get the albums from an artist based on their id."""
    results = mbz.browse_releases(artist=artist_id,
                                  release_status=['official'],
                                  includes=['labels'],
                                  release_type=['album', 'ep'],
                                  limit=100)
    releases = results['release-list']
    return releases
