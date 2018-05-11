"""This module contains the recommendation library."""
import psycopg2
from surprise import Dataset, Reader
from surprise import KNNBasic
from collections import defaultdict
import pandas as pd
import os
import json

pickle_file = "data.pickle"
ON_HEROKU = os.environ.get('ON_HEROKU', 'False') == 'True'
DATABASE_URL = os.environ['DATABASE_URL']


class Recommender:
    """Recommender object."""

    def __init__(self, pg=None, testing=False):
        """Initialize and train a new recommender."""
        self.labels = {}
        self.trained = False
        self.pg = pg
        self.testing = testing
        self.knn = None
        self.periodicTrain()

    def fit(self, data):
        """Fit this object to data."""
        df = pd.DataFrame.from_dict(data)
        reader = Reader(line_format='user item rating', rating_scale=(1, 10))
        data = Dataset.load_from_df(df[['u_id', 'a_id', 'ratings']], reader)
        train = data.build_full_trainset()
        sim_options = {
            'name': 'cosine',
            'user_based': True
        }
        self.knn = KNNBasic(sim_options=sim_options)
        self.knn.fit(train)
        return train

    def recommend(self, u_id, fullRetrain=False):
        """Recommend artists for a user."""
        if fullRetrain:
            self.periodicTrain()
            self.recommend(u_id, fullRetrain=False)
        data = self.checkDB(u_id)
        if data != []:
            return data
        else:
            return self.avgTopArtists(u_id)

    def checkDB(self, u_id):
        """Check the database to see if data exists for u_id."""
        # called by predict
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute('SELECT * from users where id=%s', [u_id])
        row = cur.fetchone()
        if not row:
            return []
        cur.execute('SELECT recommendations, computing FROM recommendations where u_id=%s;', (u_id,))
        row = cur.fetchone()
        if not row:
            cur.execute('INSERT into recommendations (u_id) VALUES (%s)', (u_id,))
            cur.close()
            conn.close()
            return []
        cur.close()
        conn.close()
        return row[0]['recommendations']

    def avgTopArtists(self, u_id):
        """Return top artists."""
        query = 'SELECT id, review FROM artists WHERE review IS NOT NULL and s_id NOT IN (select s_id from artists, reviews where artists.id=reviews.a_id and reviews.u_id=%s) ORDER BY review DESC LIMIT 25;'
        vals = (u_id,)
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(query, vals)
        rows = cur.fetchmany(6)
        ret = []
        for row in rows:
            ret.append(row[0])
        ret = self.get_s_ids(ret)
        # data = { u_id :  ret }
        # self.pushAllToDB(data)
        # possibly insert into db
        # print(ret)
        return ret

    def get_s_ids(self, data):
        """Get spotify ids from artist ids."""
        conn = connect_to_db()
        cur = conn.cursor()
        ret = []
        for d in data:
            # print(d)
            cur.execute('SELECT s_id from artists where id=%s', [d])
            s_id = cur.fetchone()
            s_id = s_id[0]
            ret.append(s_id)
        # print(ret)
        return ret

    def pullAllFromDB(self):
        """Pull all reviews from db."""
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute('select * from reviews;')
        data = {
            'u_id': [],
            'a_id': [],
            'ratings': []
        }
        users = []
        artists = []
        ratings = []
        rows = cur.fetchmany(10)
        while rows != []:
            for row in rows:
                users.append(row[0])
                artists.append(row[1])
                ratings.append(row[2])
            rows = cur.fetchmany(10)
        data['u_id'] = users
        data['a_id'] = artists
        data['ratings'] = ratings
        cur.close()
        conn.close()
        return data

    def periodicTrain(self):
        """Train the model."""
        data = self.pullAllFromDB()
        train = self.fit(data)
        test = train.build_anti_testset()
        predictions = self.knn.test(test)
        top_predictions = self.top3(predictions)
        # print(top_predictions)
        self.pushAllToDB(top_predictions)
        # We should be able to use this now? yes

    def pushAllToDB(self, data):
        """Push recommendations to the database."""
        conn = connect_to_db()
        cur = conn.cursor()
        query = 'INSERT INTO recommendations (u_id, recommendations, computing) VALUES (%s, %s, %s) ON CONFLICT (u_id) DO UPDATE SET recommendations=%s'
        for key in data.keys():
            recommendations = []
            for d in data[key]:
                if d[1] >= 5.5:
                    recommendations.append(d[0])
            if recommendations != []:
                # print(recommendations)
                recommendations = self.get_s_ids(recommendations)
                dic = {'recommendations': recommendations}
                vals = (key, json.dumps(dic), "False", json.dumps(dic))
                cur.execute(query, vals)
        conn.commit()
        cur.close()
        conn.close()

    def top3(self, predictions, topN=6):
        """Get top 3."""
        top_recs = defaultdict(list)
        for uid, iid, rid, est, _ in predictions:
            top_recs[uid].append((iid, est))
        for uid, user_ratings in top_recs.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_recs[uid] = user_ratings[:topN]
        return top_recs


def connect_to_db():
    """Create a connection to the DB."""
    if ON_HEROKU:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    else:
        conn = psycopg2.connect(DATABASE_URL)
    return conn

"""
data = {
    'itemID' : [1, 5, 4, 3, 2],
    'userID' : [9, 32, 16, 4, 31],
    'rating' : [1, 2, 3, 5, 8]
}
"""

recommender = Recommender()
recommender.periodicTrain()
# recommender.recommend(7, fullRetrain=True)
