from album_discovery import sp
import psycopg2
from surprise import evaluate, Dataset, Reader
from surprise import KNNBasic
from collections import defaultdict
import random
import pandas as pd
import os
import json

sample_artists = [ 'Goldlink', 'Cage the elephant', 'DNCE', 'T-pain', 'Kings of Leon', 'Hurley Mower', 'Shallou', 'Khalid', 'Ramin Djawadi', 'Ed Sheeran', 'Kid Cudi', 'Vengaboys', 'Calvin Harris', 'The Weekend', 'Drake', 'Lil Dicky', 'Bowling for Soup', 'XXXTentacion', 'Post Malone', 'A$ap rocky', 'Illenium', 'Logic']
pickle_file = "data.pickle"
running_local = False
DATABASE_URL = os.environ['DATABASE_URL']

class Recommender:
    def __init__(self, pg=None, testing=False):
        self.labels = {}
        self.trained = False
        self.pg = pg
        self.testing = testing
        self.knn = None

    def fit(self, data):
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
        if fullRetrain:
            self.periodicTrain()
            self.recommend(u_id, fullRetrain=False)
        data = self.checkDB(u_id)
        if data != []:
            return data
        else:
            return self.avgTopArtists(u_id)
            #compute top avg and return those

    def checkDB(self, u_id):
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
        query = 'SELECT a_id, AVG(rating) as r FROM reviews group by a_id ORDER BY r DESC;'
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(query)
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
        conn = connect_to_db()
        cur = conn.cursor()
        ret = []
        for d in data:
            print(d)
            cur.execute('SELECT s_id from artists where id=%s', [d])
            s_id = cur.fetchone()
            s_id = s_id[0]
            ret.append(s_id)
        # print(ret)
        return ret

    def pullAllFromDB(self):
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute('select * from reviews;')
        data = {
            'u_id' : [],
            'a_id' : [],
            'ratings' : []
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
        data = self.pullAllFromDB()
        train = self.fit(data)
        test = train.build_anti_testset()
        predictions = self.knn.test(test)
        top_predictions = self.top3(predictions)
        print(top_predictions)
        self.pushAllToDB(top_predictions)
        # We should be able to use this now? yes

    def pushAllToDB(self, data):
        conn = connect_to_db()
        cur = conn.cursor()
        query = 'INSERT INTO recommendations (u_id, recommendations, computing) VALUES (%s, %s, %s) ON CONFLICT (u_id) DO UPDATE SET recommendations=%s'
        for key in data.keys():
            recommendations = []
            for d in data[key]:
                if d[1] >= 5.5:
                    recommendations.append(d[0])
            if recommendations != []:
                print(recommendations)
                recommendations = self.get_s_ids(recommendations)
                dic = { 'recommendations' : recommendations }
                vals = (key, json.dumps(dic), "False", json.dumps(dic))
                cur.execute(query, vals)
        conn.commit()
        cur.close()
        conn.close()

    def top3(self, predictions, topN=6):
        top_recs = defaultdict(list)
        for uid, iid, rid, est, _ in predictions:
            top_recs[uid].append((iid, est))
        for uid, user_ratings in top_recs.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_recs[uid] = user_ratings[:topN]
        return top_recs

def connect_to_db():
    """Create a connection to the DB."""
    if running_local:
        conn = psycopg2.connect(DATABASE_URL)
    else:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
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
