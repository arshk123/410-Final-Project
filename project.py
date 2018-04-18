"""The flasks server that runs our project."""
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import psycopg2
# import credentials
import album_discovery
import artist_rating

app = Flask(__name__)
app.secret_key = 'super_secret_key'

sp = album_discovery.sp


@app.route('/')
def index():
    """Endpoint for the home page."""
    # test_db()
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    """Login method."""
    session['email'] = request.form['email']
    return redirect(url_for('user'))


@app.route('/logout', methods=['POST'])
def logout():
    """Logout method"""
    session.pop('email')
    return url_for('index')

@app.route('/signup', methods=['POST'])
def signup():
    """Sign a user up."""
    session['email'] = request.form['email']
    return redirect(url_for('user'))


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


def test_db():
    """Test that the postegres database is setup and working properly."""
    dbname = 'cs410project'
    user = credentials.login['user']
    password = credentials.login['password']
    conn = psycopg2.connect(dbname=dbname, user=user, password=password)
    cur = conn.cursor()
    cur.execute("SELECT * FROM test")
    print(cur.fetchall())
    cur.close()
    conn.close()
