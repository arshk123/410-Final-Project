import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from api_keys import spotify_client_id, spotify_client_secret
from surprise import evaluate, Dataset, Reader
from surprise import KNNBasic
from collections import defaultdict
import random
import pandas as pd
import os

sample_artists = [ 'Goldlink', 'Cage the elephant', 'DNCE', 'T-pain', 'Kings of Leon', 'Hurley Mower', 'Shallou', 'Khalid', 'Ramin Djawadi', 'Ed Sheeran', 'Kid Cudi', 'Vengaboys', 'Calvin Harris', 'The Weekend', 'Drake', 'Lil Dicky', 'Bowling for Soup', 'XXXTentacion', 'Post Malone', 'A$ap rocky', 'Illenium', 'Logic']


spotify_client_id = os.environ.get('SPOTIFY_CLIENT_ID', '')
spotify_client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
spotify_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                                       client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=spotify_credentials_manager)



class Recommender:
    def __init__(self, pg=None, testing=False):
        self.labels = {}
        self.trained = False
        self.pg = pg
        self.testing = testing

    """ Doesn't work """
    def top3(self, predictions, topN = 3):
        top_recs = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_recs[uid].append((iid, est))

        for uid, user_ratings in top_recs.items():
            user_ratings.sort(key = lambda x: x[1], reverse = True)
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

    def recommend(self, artist):
        pass

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
