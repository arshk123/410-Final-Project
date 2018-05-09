"""The flasks server that runs our project."""
from flask import Flask, abort, render_template, session, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import unquote_plus
import psycopg2
import os
import threading
import album_discovery
from populate_db import add_single_artist_from_json, artist_queue
# import recommender

app = Flask(__name__)
app.secret_key = 'super_secret_key'

sp = album_discovery.sp
DATABASE_URL = os.environ['DATABASE_URL']
running_local = False


@app.route('/')
def index():
    """Endpoint for the home page."""
    # test_db()
    if 'email' in session:
        return redirect(url_for('user'))
    return render_template('index.html')


@app.route('/about')
def about():
    """Endpoint for the about page."""
    return render_template('about.html')


@app.route('/login', methods=['POST'])
def login():
    """Login method."""
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email=%s', [request.form['email']])

    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        db_password = row[1]
        password_entered = request.form['password']

        if check_password_hash(db_password, password_entered):
            session['email'] = request.form['email']
            session['id'] = row[3]
            session['username'] = row[2]
            return redirect(url_for('user'))

    return render_template('index.html'), 400


@app.route('/logout', methods=['POST'])
def logout():
    """Logout method."""
    session.pop('email')
    session.pop('username')
    return url_for('index')


@app.route('/search')
def search():
    """Search for an artist."""
    conn = connect_to_db()
    cur = conn.cursor()
    query = unquote_plus(request.args['navsearch'])
    query = query.lower()
    query = '%{}%'.format(query)
    cur.execute('SELECT name, s_id FROM artists WHERE LOWER(name) LIKE %s;', (query,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    result_dicts = []
    if results:
        for result in results:
            result_dicts.append({'name': result[0], 'id': result[1]})
    return render_template('search.html', artists=result_dicts)


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
    session['username'] = request.form['email']
    conn.commit()
    conn.close()

    return jsonify(redirect_url='/user')


@app.route('/user')
def user():
    """Show the user some recommendations."""
    if 'email' not in session:
        return render_template('index.html')

    return render_template('user.html', email=session['email'], recs=get_user_recommendations(1))


@app.route('/user/<u_id>/recommendations')
def get_user_recommendations(u_id):
    """Get recommendations based on a user's id."""
    # print(artist_rating.get_rating_from_query('Drake'))

    # conn = connect_to_db()
    # cur = conn.cursor()
    #
    # cur.execute('SELECT a_id, u_id, rating FROM reviews')
    # rows = cur.fetchall()
    # artist_ids = [i[0] for i in rows]
    # user_ids = [i[1] for i in rows]
    # ratings = [i[2] for i in rows]
    #
    # data = {'itemID': artist_ids,
    #         'userID': user_ids,
    #         'ratings': ratings }
    #
    # rec = recommender.Recommender()
    # rec.setup(data)

    # return json object of hard coded artist for now
    return jsonify([sp.artist('4xRYI6VqpkE3UwrDrAZL8L'), sp.artist('3TVXtAsR1Inumwj472S9r4'),
                    sp.artist('26VFTg2z8YR0cCuwLzESi2'), sp.artist('1Bl6wpkWCQ4KVgnASpvzzA'),
                    sp.artist('536BYVgOnRky0xjsPT96zl'), sp.artist('4kI8Ie27vjvonwaB2ePh8T')])


@app.route('/artist/<s_id>')
def artist(s_id):
    """Endpoint for artist page."""
    artist = sp.artist(s_id)
    albums = album_discovery.get_artist_albums(artist, full_album_info=True)
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute('SELECT review, lastupdated, id FROM artists WHERE s_id=%s;', (artist['id'],))
    rating_row = cur.fetchone()
    cur.close()
    conn.close()

    rating = None
    lastupdated = None
    if rating_row is None:
        rating = "This artist is pending addition to our database"
        if artist not in artist_queue:
            print("Adding {} to the queue".format(artist['name']))
            t = threading.Thread(target=add_single_artist_from_json, args=(artist,))
            t.start()
    elif rating_row[0] is None:
        rating = "We couldn't find any reviews for this artist on pitchfork. You can still rate this artist in order to improve your recommendations."
        if artist not in artist_queue:
            print("Adding {} to the queue".format(artist['name']))
            t = threading.Thread(target=add_single_artist_from_json, args=(artist,))
            t.start()
        lastupdated = {'date': rating_row[1].strftime("%Y-%m-%d"), 'time': rating_row[1].strftime("%H:%M")}
    else:
        rating = rating_row[0]
        lastupdated = {'date': rating_row[1].strftime("%Y-%m-%d"), 'time': rating_row[1].strftime("%H:%M")}

    user_rating = None
    if 'id' in session:
        user_rating = get_user_rating(session['id'], s_id)

    avg_user_rating = '-'
    user_count = '0'
    if rating_row is not None:
        avg_user_rating, user_count = get_avg_user_rating(rating_row[2])

    return render_template("artist.html", artist=artist, albums=albums,
                           rating=rating, lastupdated=lastupdated, s_id=s_id,
                           user_rating=user_rating, avg_user_rating=avg_user_rating,
                           user_count=user_count)


def get_user_rating(user_id, artist_id):
    """Get a user rating from the db."""
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute('SELECT id FROM artists WHERE s_id=%s', [artist_id])
    row = cur.fetchone()
    if not row:
        return None  # artist is not yet in database so return

    artist_id = row[0]

    cur.execute('SELECT rating FROM reviews WHERE u_id=%s AND a_id=%s', [user_id, artist_id])
    row = cur.fetchone()
    if not row:
        return None
    cur.close()
    conn.close()
    return row[0]


def get_avg_user_rating(artist_id):
    """Get the average rating for an artist for all users that have rated that artist."""
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(rating) FROM reviews WHERE a_id=%s', [artist_id])
    count = int(cur.fetchone()[0])
    if count:
        cur.execute('SELECT AVG(rating) FROM reviews WHERE a_id=%s', [artist_id])
        rating = cur.fetchone()[0]
    else:
        rating = '-'
    cur.close()
    conn.close()

    return rating, count


@app.route('/new_artist', methods=['GET', 'POST'])
def new_artist():
    """Search page for adding a new artist to the db."""
    return render_template("new_artist.html")


@app.route('/navsearch', methods=['GET'])
def navsearch():
    """Autocomplete endpoint used for navbar search."""
    search = request.args.get('q')
    search = search.lower()
    search = '%{}%'.format(search)

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute('SELECT name, s_id FROM artists WHERE LOWER(name) LIKE %s;', (search,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = []
    if rows:
        results = [{'label': row[0], 'value': row[1]} for row in rows]
    return jsonify(matching_results=results)


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Autocomplete endpoint used for adding a new artist."""
    search = request.args.get('q')
    artist_list = album_discovery.get_artist_list(search)
    results = []
    if artist_list:
        results = [{'label': artist['name'], 'value': artist['id']} for artist in artist_list]
    return jsonify(matching_results=results)


@app.route('/handledata/', methods=['POST'])
def handledata():
    """Used to handle an artist request."""
    s_id = request.form['s_id']
    artist_json = sp.artist(s_id)
    try:
        if artist_json not in artist_queue:
            print("Adding {} to the queue".format(artist_json['name']))
            t = threading.Thread(target=add_single_artist_from_json, args=(artist_json,))
            t.start()
    except Exception as e:
        print(e)
        abort(418)

    return jsonify(redirect_url='/artist/{}'.format(artist_json['id']))


@app.route('/artist/rate/<s_id>', methods=['GET', 'POST'])
def rate_artist(s_id):
    """Submit a rating for the artist."""
    if 'id' not in session:
        return jsonify(success=False), 400
    rating = request.form['rating']

    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM artists WHERE s_id=%s', [s_id])
    rows = cur.fetchall()
    artist_id = rows[0][1]

    cur.execute('SELECT * FROM reviews WHERE u_id=%s and a_id=%s', [session['id'], artist_id])
    rows = cur.fetchall()
    if len(rows) == 0:
        cur.execute('INSERT INTO reviews (u_id, a_id, rating) VALUES (%s, %s, %s)', [session['id'], artist_id, rating])
    else:
        cur.execute('UPDATE reviews SET rating=%s WHERE u_id=%s and a_id=%s', [rating, session['id'], artist_id])

    conn.commit()
    conn.close()

    return jsonify(success=True), 200


def connect_to_db():
    """Create a connection to the DB."""
    if running_local:
        conn = psycopg2.connect(DATABASE_URL)
    else:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn
