"""The flasks server that runs our project."""
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import os
# import credentials
import album_discovery
import artist_rating

app = Flask(__name__)
app.secret_key = 'super_secret_key'

sp = album_discovery.sp
DATABASE_URL = os.environ['DATABASE_URL']


@app.route('/')
def index():
    """Endpoint for the home page."""
    # test_db()
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    """Login method."""
    session['email'] = request.form['email']
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email=%s', [request.form['email']])

    rows = cur.fetchall()
    if len(rows) != 0:
        db_password = rows[0][1]
        password_entered = request.form['password']

        if check_password_hash(db_password, password_entered):
            return redirect(url_for('user'))

    return render_template('index.html'), 400



@app.route('/logout', methods=['POST'])
def logout():
    """Logout method"""
    session.pop('email')
    return url_for('index')

@app.route('/signup', methods=['POST'])
def signup():
    """Sign a user up."""
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM users WHERE email=%s', [request.form['email']])

    if len(cur.fetchall()) != 0:
        return render_template('index.html'), 400

    hashed_password = generate_password_hash(request.form['password'])
    cur.execute('INSERT INTO users VALUES (%s, %s, %s)', [request.form['email'], hashed_password, request.form['username']])
    session['email'] = request.form['email']
    conn.commit()
    conn.close()

    return jsonify(redirect_url='/user')


@app.route('/user')
def user():
    """Show the user some recommendations."""
    if 'email' not in session:
        return render_template('index.html')

    return render_template('user.html', email=session['email'], recs=get_user_recommendations(1))


@app.route('/user/<id>/recommendations')
def get_user_recommendations(id):
    """Get recommendations based on a user's id."""
    # print(artist_rating.get_rating_from_query('Drake'))

    # return json object of hard coded artist for now
    return jsonify([sp.artist('4xRYI6VqpkE3UwrDrAZL8L'), sp.artist('3TVXtAsR1Inumwj472S9r4'), sp.artist('26VFTg2z8YR0cCuwLzESi2'), sp.artist('1Bl6wpkWCQ4KVgnASpvzzA'), sp.artist('536BYVgOnRky0xjsPT96zl'), sp.artist('4kI8Ie27vjvonwaB2ePh8T')])


@app.route('/artist/<id>')
def artist(id):
    """Endpoint for artist page"""
    artist = sp.artist(id)
    albums = album_discovery.get_artist_albums(artist, full_album_info=True)

    return render_template("artist.html", artist=artist, albums=albums, email=session['email'])

@app.route('/new_artist', methods=['GET', 'POST'])
def new_artist():
    """Search page for adding a new artist to the db."""
    return render_template("new_artist.html")


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Autocomplete endpoint used for adding a new artist."""
    search = request.args.get('q')
    print(search)
    artist_list = album_discovery.get_artist_list(search)
    results = [artist['name'] for artist in artist_list]
    return jsonify(matching_results=results)


@app.route('/handledata/', methods=['POST'])
def handledata():
    """Used to handle an artist request."""
    artist_name = request.form['artist_name']
    artist_rate = artist_rating.get_rating_from_query(artist_name)
    print(artist_name, artist_rate)
    return jsonify(artist=artist_name, rating=artist_rate)


def connect_to_db():
    """Test that the postegres database is setup and working properly."""
    # dbname = 'musicrater'
    # user = credentials.login['user']
    # password = credentials.login['password']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM test")
    # print(cur.fetchall())
    # cur.close()
    return conn
