"""This module will be used to prepopulate the db with a set of artists using the billboard api."""
import album_discovery
import artist_rating
# import billboard
import psycopg2
from psycopg2.extras import execute_values
from time import sleep
from urllib.error import URLError

chart_names = ['artist-100']#, 'greatest-hot-100-women-artists',
               #'greatest-of-all-time-pop-songs-artists', 'greatest-top-dance-club-artists',
               #'greatest-r-b-hip-hop-artists', 'greatest-hot-100-artists']


def test_db():
    """Test that the postgres database is setup and working properly."""
    dbname = 'cs410project'
    user = 'postgres'
    conn = psycopg2.connect(dbname=dbname, user=user)
    cur = conn.cursor()
    cur.execute("SELECT * FROM test")
    print(cur.fetchall())
    cur.close()
    conn.close()


def populate_db():
    """Populate the db using the billboard artist charts."""
    # artists = set()
    # for chart_name in chart_names:
    #     chart = billboard.ChartData(chart_name)
    #     for entry in chart:
    #         artists.add(entry.artist)
    # artists = list(artists)
    artists = ['Anderson .Paak', 'Kanye West', 'Kali Uchis', 'SZA', 'Janelle Monae']

    rated_artists = []
    while artists:
        artist = artists.pop()
        try:
            artist_list = album_discovery.get_artist_list(artist)
            artist_json = artist_list[0]
            rating = artist_rating.get_rating_from_artist(artist_json)
            if rating > 0:
                rated_artists.append((artist_json['name'], rating, artist_json['id']))
        except (TimeoutError, URLError):
            print("error, trying {} again".format(artist))
            artists.append(artist)
            sleep(0.5)

    dbname = 'cs410project'
    user = 'postgres'
    conn = psycopg2.connect(dbname=dbname, user=user)
    cur = conn.cursor()
    insert_query = 'INSERT INTO artists (name, review, s_id) VALUES %s;'
    execute_values(
        cur, insert_query, rated_artists, template=None, page_size=100
    )
    conn.commit()
    cur.close()
    conn.close()
