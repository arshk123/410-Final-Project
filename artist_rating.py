"""This module will be used to assign an artist a score based on their albums."""
import pitchfork


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
                temp.append(reviews)
        reviews = temp
    return reviews
