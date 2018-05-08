from album_discovery import sp
import psycopg2
from surprise import evaluate, Dataset, Reader
from surprise import KNNBasic
from collections import defaultdict
import random
import pandas as pd
import os

sample_artists = [ 'Goldlink', 'Cage the elephant', 'DNCE', 'T-pain', 'Kings of Leon', 'Hurley Mower', 'Shallou', 'Khalid', 'Ramin Djawadi', 'Ed Sheeran', 'Kid Cudi', 'Vengaboys', 'Calvin Harris', 'The Weekend', 'Drake', 'Lil Dicky', 'Bowling for Soup', 'XXXTentacion', 'Post Malone', 'A$ap rocky', 'Illenium', 'Logic']
pickle_file = "data.pickle"
running_local = False

class Recommender:
    def __init__(self, pg=None, testing=False):
        self.labels = {}
        self.trained = False
        self.pg = pg
        self.testing = testing

    def fit(self):
        pass

    def predict(self, u_id):
        # Query recommendations and cross reference with previously reviewed items by u_id, if not empty, then return recs
        
        # 1. Check if compute bool is False, then Set compute bool to True, if true then do nothing?

        # 2. Check if already computed and in db return if so, make sure to flip compute bool to False
        computing, data = self.checkDB(u_id)
        if data != []:
            # flip compute bool
            return data

        # 3. check last updated on pickle_file
        # 4. If greater than 24 hrs then retrain and predict, return highest avg reviews by users and tailored flag to false
        # 5. Else predict and return with tailored flag to true

        pass

    def periodicTrain(self):
        # TODO
        pass

    def loadPickle(self):
        # TODO once recommender integrated with db
        pass

    def unloadPickle(self):
        # TODO once recommender integrated with db
        pass

    def pushAllToDB(self, data):
        pass

    def pushToDB(self, u_id, recommendations):
        # from periodicTrain
        pass

    def checkDB(self, u_id):
        # called by predict
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute('SELECT recommendations, computing FROM recommendations where u_id=%s;', (u_id,))
        row = cur.fetchone()
        if not row:
            cur.execute('INSERT into recommendations (u_id) VALUES (%s)', (u_id,))
            cur.close()
            conn.close()
            return False, []
        return row[1], row[0]


    """ Doesn't work """
    def top3(self, predictions, topN=3):
        top_recs = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_recs[uid].append((iid, est))

        for uid, user_ratings in top_recs.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_recs[uid] = user_ratings[:topN]

        return top_recs

    def setup(self, data):
        df = pd.DataFrame.from_dict(data)
        reader = Reader(line_format='user item rating', rating_scale=(1, 10))
        data = Dataset.load_from_df(df[['userID', 'itemID', 'ratings']], reader)
        train = data.build_full_trainset()
        sim_options = {
            'name': 'cosine',
            'user_based': True
        }
        self.knn = KNNBasic(sim_options=sim_options)
        self.knn.fit(train)
        test = train.build_anti_testset()
        predictions = self.knn.test(test)
        print(predictions)
        topPreds = self.top3(predictions)
        print(topPreds)

    def loadData(self):
        pass

    def buildSampleDataset(self, numSamples=10):
        data = {
            'userID' : [],
            'itemID' : [],
            'ratings' : []
        }
        users = []
        ratings = []
        items = []
        labels = []
        for artist in sample_artists:
            results = sp.search(q='artist:' + artist, type='artist')
            r = results['artists']['items']
            if(len(r) > 0):
                for i, a in enumerate(r):
                    # print(i, a['name'])
                    self.labels.append(a['name'])

        for ind, art in enumerate(self.labels):
            for num in range(numSamples):
                if random.randint(1,11)%2 != 0:
                    users.append(num)
                    items.append(ind)
                    ratings.append(random.randint(1,11))
        data['itemID'] = items
        data['userID'] = users
        data['ratings'] = ratings
        return data, labels

"""
data = {
    'itemID' : [1, 5, 4, 3, 2],
    'userID' : [9, 32, 16, 4, 31],
    'rating' : [1, 2, 3, 5, 8]
}
"""

# recommender = Recommender()
# data, labels = recommender.buildSampleDataset()
# recommender.setup(data)

def connect_to_db():
    """Create a connection to the DB."""
    if running_local:
        conn = psycopg2.connect(DATABASE_URL)
    else:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn
