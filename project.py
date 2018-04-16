from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from api_keys import spotify_client_id, spotify_client_secret
import psycopg2
# import credentials
import spotipy
import album_discovery
import artist_rating
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

spotify_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                                       client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=spotify_credentials_manager)

@app.route('/')
def index():
    # test_db()
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    session['email'] = request.form['email']
    return redirect(url_for('user', name=session['email']))

@app.route('/signup', methods=['POST'])
def signup():
    user_name = request.form['name']
    return redirect(url_for('user', name=user_name))

@app.route('/user/<name>')
def user(name):
    get_user_recommendations(1)
    return render_template('user.html', name=name, recs=get_user_recommendations(1))


@app.route('/user/<id>/recommendations')
def get_user_recommendations(id):
    # print(artist_rating.get_rating_from_query('Drake'))

    # return json object of hard coded artist for now
    return jsonify([sp.artist('4xRYI6VqpkE3UwrDrAZL8L'), sp.artist('3TVXtAsR1Inumwj472S9r4'), sp.artist('26VFTg2z8YR0cCuwLzESi2'), sp.artist('1Bl6wpkWCQ4KVgnASpvzzA'), sp.artist('536BYVgOnRky0xjsPT96zl'), sp.artist('4kI8Ie27vjvonwaB2ePh8T')])


"""
This function simply serves to test that the postegres database is setup and working properly
"""
def test_db():
    dbname = 'cs410project'
    user = credentials.login['user']
    password = credentials.login['password']
    conn = psycopg2.connect(dbname=dbname, user=user, password=password)
    cur = conn.cursor()
    cur.execute("SELECT * FROM test")
    print(cur.fetchall())
    cur.close()
    conn.close()