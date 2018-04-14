"""This module will be used to assign an artist a score based on their albums."""
import pitchfork
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize


def get_pitchfork_reviews(artist_name, album_names):
    """Get the artists reviews from pitchfork."""
    reviews = []
    for album_name in album_names:
        try:
            review = pitchfork.search(artist_name, album_name)
            reviews.append(review)
        except IndexError:
            print("Couldn't find {}".format(album_name))
    if len(reviews) > 0:
        temp = []
        for review in reviews:
            # This is necessary because sometimes albums with similar names
            # get added twice as the pitchfork search is fuzzy
            if review not in temp:
                temp.append(review)
        reviews = temp
    return reviews


def get_sentiment_rating(review_text):
    """Use sentiment analysis to rate a review as positive or negative."""
    sentences = tokenize.sent_tokenize(review_text)
    sid = SentimentIntensityAnalyzer()
    ss = [sid.polarity_scores(sentence) for sentence in sentences]
    avg_sentiment = {k: sum(t[k] for t in ss) / len(ss) for k in ss[0]}
    # Compound score (low = more negative) is scaled from -1 to 1
    # This scales it from 0 to 10 instead
    compound = (avg_sentiment['compound'] + 1) * 5
    return compound


def get_overall_rating(reviews):
    """Get the overall rating based on a set of reviews."""
    for review in reviews:
        review.sentiment = get_sentiment_rating(review.full_text())
        review.overall_rating = 0.8 * review.score() + 0.2 * review.sentiment
    total = sum(review.overall_rating for review in reviews)
    avg = total / len(reviews)
    return avg
