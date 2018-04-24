"""This module will be used to assign an artist a score based on their albums."""
import album_discovery
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import pitchfork
from unidecode import unidecode


def get_pitchfork_reviews(artist_name, album_names):
    """Get the artists reviews from pitchfork."""
    # this line is needed because the python requests library requires values to be ascii
    artist_name = unidecode(artist_name)
    reviews = []
    for album_name in album_names:
        try:
            album_name = unidecode(album_name)
            review = pitchfork.search(artist_name, album_name)
            reviews.append(review)
        except IndexError:
            print("Couldn't find {}".format(album_name))
    if len(reviews) > 0:
        temp = []
        for review in reviews:
            # This is necessary because sometimes albums with similar names
            # get added twice as the pitchfork API does fuzzy search
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
    # This scales it from 0 to 1 instead
    compound = (avg_sentiment['compound'] + 1) / 2
    return compound


def get_overall_rating(reviews):
    """Get the overall rating based on a set of reviews."""
    if len(reviews) < 1:
        return -1
    for review in reviews:
        review.sentiment = get_sentiment_rating(review.full_text())
        rescaled_score = (review.score() * 9) / 10
        review.overall_rating = rescaled_score + review.sentiment
    total = sum(review.overall_rating for review in reviews)
    avg = total / len(reviews)
    return avg


def get_rating_from_artist(artist):
    """Get an overall rating from an artist json."""
    albums = album_discovery.get_artist_albums(artist)
    reviews = get_pitchfork_reviews(artist['name'], albums)
    return get_overall_rating(reviews)


def get_rating_from_query(name):
    """Get an overall rating by selecting the first artist that matches."""
    artist_list = album_discovery.get_artist_list(name)
    if not artist_list:
        return -1
    return get_rating_from_artist(artist_list[0])
