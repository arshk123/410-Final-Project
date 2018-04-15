from flask import Flask, render_template
import psycopg2
import credentials

app = Flask(__name__)

@app.route('/')
def index():
    # test_db()
    return render_template('index.html')


"""
This funciton simply serves to test that the postegres database is setup and working properly
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