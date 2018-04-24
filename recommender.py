from album_discovery import *
from artist_rating import *
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from api_keys import spotify_client_id, spotify_client_secret
from surprise import evaluate
from surprise import KNNBasic
import random

sample_artists = [ 'Goldlink', 'Cage the elephant', 'DNCE', 'T-pain', 'Kings of Leon', 'Hurley Mower', 'Shallou', 'Khalid', 'Ramin Djawadi', 'Ed Sheeran', 'Kid Cudi', 'Vengaboys', 'Calvin Harris', 'The Weekend', 'Drake', 'Lil Dicky', 'Bowling for Soup', 'XXXTentacion', 'Post Malone', 'A$ap rocky', 'Illenium', 'Logic']
scm = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=scm)

class Recommender:
    def __init__(self, pg=None, testing=False):
        self.labels = []
        self.trained = False
        self.pg = pg
        self.testing = testing

    def top3(self, predictions, topN = 3):
        top_recs = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_recs[uid].append((iid, est))

        for uid, user_ratings in top_recs.items():
            user_ratings.sort(key = lambda x: x[1], reverse = True)
            top_recs[uid] = user_ratings[:topN]

        return top_recs

    def setup(self, data):
        sim_options = {
            'name': 'cosine',
            'user_based': False
        }
        self.knn = KNNBasic(sim_options=sim_options)
        self.knn.fit(data)
        testSet = data.build_anti_testset()
        predictions = knn.test(testSet)
        topPreds = self.top3(predictions)
        print(topPreds)

    def loadData(self):
        pass

    def buildSampleDataset(self, numSamples=100):
        ret = []
        labels = []
        for artist in sample_artists:
            results = sp.search(q='artist:' + artist, type='artist')
            items = results['artists']['items']
            if(len(items) > 0):
                for i, a in enumerate(items):
                    print(i, a['name'])
                self.labels.append(a['name'])
            for a in range(numSamples):
                for artist in self.labels:
                    ret.append([artist, random.randint(1,11)])
            # self.labels = labels
            return ret, labels

    def recommend(self, artist):
        pass


recommender = Recommender()
data, labels = recommender.buildSampleDataset()
print(data[0])
recommender.setup(data)
