"""This module will be used to prepopulate the db with a set of artists using the billboard api."""
import album_discovery
import artist_rating
import billboard
import os
import psycopg2
from psycopg2.extras import execute_batch
import threading
from time import sleep
from urllib.error import URLError

chart_names = ['artist-100', 'greatest-hot-100-women-artists',
               'greatest-of-all-time-pop-songs-artists', 'greatest-top-dance-club-artists',
               'greatest-r-b-hip-hop-artists', 'greatest-hot-100-artists',
               'billboard-200', 'hot-100']

DATABASE_URL = os.environ['DATABASE_URL']
ON_HEROKU = os.environ.get('ON_HEROKU', 'False') == 'True'
single_artist_lock = threading.Lock()
artist_queue = []


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
            if not artist_list:
                print("Couldn't find artist {}".format(artist))
                continue
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

    conn = connect_to_db()
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
    if not artist_list:
        raise LookupError("Couldn't find artist {}".format(artist))
    artist_json = artist_list[0]
    rating = artist_rating.get_rating_from_artist(artist_json)

    with single_artist_lock:
        conn = connect_to_db()
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
        print("Finished adding {}".format(artist))
        return artist_json['id']


def add_single_artist_from_json(artist_json):
    """Add a single artist by name. Only to be used with the name we get from spotify."""
    artist_queue.append(artist_json)
    artist = artist_json['name']
    rating = artist_rating.get_rating_from_artist(artist_json)

    with single_artist_lock:
        conn = connect_to_db()
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
        print("Finished adding {}".format(artist))
        artist_queue.remove(artist_json)
        return artist_json['id']


def remove_artists_in_db(artists):
    """Filter the artists list and remove ones that are already in the db."""
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute('SELECT name FROM artists;')
    rows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    db_artists = set(row[0] for row in rows)
    artists = [artist for artist in artists if artist not in db_artists]
    return artists


def connect_to_db():
    """Create a connection to the DB."""
    if ON_HEROKU:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        conn = psycopg2.connect(DATABASE_URL)
    return conn


if __name__ == '__main__':
    artists = get_artists_from_charts()
    artists = remove_artists_in_db(artists)
    print("Found {} artists using the billboard API".format(len(artists)))
    batches = get_batches(artists)
    n = len(batches)
    failed_artists = []
    for i, batch in enumerate(batches):
        print("Beginning population with batch {}/{}".format(i + 1, n))
        try:
            populate_db(batch)
        except Exception as e:
            failed_artists.extend(batch)
            print(e)
            print("Failed batch {} containing {}".format(i, batch))
    if len(failed_artists) > 0:
        print("Failed to add the following artists to the db:\n{}".format(failed_artists))
    # add_single_artist(artists[1])
