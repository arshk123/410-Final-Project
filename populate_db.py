"""This module will be used to prepopulate the db with a set of artists using the billboard api."""
import album_discovery
import artist_rating
import billboard
import os
import psycopg2
from psycopg2.extras import execute_batch
from time import sleep
from urllib.error import URLError

chart_names = ['artist-100']#, 'greatest-hot-100-women-artists',
               # 'greatest-of-all-time-pop-songs-artists', 'greatest-top-dance-club-artists',
               # 'greatest-r-b-hip-hop-artists', 'greatest-hot-100-artists']

DATABASE_URL = os.environ['DATABASE_URL']


def get_artists_from_charts():
    """Get a list of artists from different charts."""
    artists = set()
    for i, chart_name in enumerate(chart_names):
        print("Collecting chart {}".format(i))
        chart = billboard.ChartData(chart_name)
        for entry in chart:
            artists.add(entry.artist)
    artists = list(artists)
    return artists


def get_batches(artists, batch_size=5):
    """Separate the artists into batches."""
    batch_size = max(1, batch_size)
    return [artists[i:i + batch_size] for i in range(0, len(artists), batch_size)]


def populate_db(artists):
    """Populate the db using the billboard artist charts."""
    rated_artists = []
    unrated_artists = []
    while artists:
        artist = artists.pop()
        try:
            artist_list = album_discovery.get_artist_list(artist)
            artist_json = artist_list[0]
            rating = artist_rating.get_rating_from_artist(artist_json)
            if rating > 0:
                rated_artists.append((artist_json['name'], rating, artist_json['id'], rating))
            else:
                print("Couldn't find any album reviews for {}".format(artist))
                unrated_artists.append((artist_json['name'], artist_json['id']))
        except (TimeoutError, URLError):
            print("error, trying {} again".format(artist))
            artists.append(artist)
            sleep(0.5)

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    insert_query = 'INSERT INTO artists (name, review, s_id) VALUES (%s, %s, %s) ON CONFLICT (s_id) DO UPDATE SET review=%s, lastupdated=DEFAULT'
    execute_batch(cur, insert_query, rated_artists)
    conn.commit()
    unrated_query = 'INSERT INTO artists (name, s_id) VALUES (%s, %s) ON CONFLICT (s_id) DO UPDATE SET lastupdated=DEFAULT'
    execute_batch(cur, unrated_query, unrated_artists)
    conn.commit()
    cur.close()
    conn.close()


def add_single_artist(artist):
    """Add a single artist by name. Only to be used with the name we get from spotify."""
    artist_list = album_discovery.get_artist_list(artist)
    artist_json = artist_list[0]
    rating = artist_rating.get_rating_from_artist(artist_json)

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    if rating > 0:
        vals = (artist_json['name'], rating, artist_json['id'], rating)
        query = 'INSERT INTO artists (name, review, s_id) VALUES (%s, %s, %s) ON CONFLICT (s_id) DO UPDATE SET review=%s, lastupdated=DEFAULT'
    else:
        print("Couldn't find any album reviews for {}".format(artist))
        vals = (artist_json['name'], artist_json['id'])
        query = 'INSERT INTO artists (name, s_id) VALUES (%s, %s) ON CONFLICT (s_id) DO UPDATE SET lastupdated=DEFAULT'

    cur.execute(query, vals)
    conn.commit()
    cur.close()
    conn.close()


if __name__ == '__main__':
    # artists = get_artists_from_charts()
    artists = ['Janelle Monae', 'Anderson .Paak']
    print("Found {} artists using the billboard API".format(len(artists)))
    batches = get_batches(artists)
    n = len(batches)
    failed_artists = []
    for i, batch in enumerate(batches):
        print("Beginning population with batch {}/{}".format(i, n))
        try:
            populate_db(batch)
        except Exception as e:
            failed_artists.extend(batch)
            print(e)
            print("Failed batch {} containing {}".format(i, batch))
    print("Failed to add the following artists to the db:\n{}".format(failed_artists))
    # add_single_artist(artists[1])
