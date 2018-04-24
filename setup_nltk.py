"""This module runs on every new heroku release to download required nltk files."""
import nltk

nltk.download('punkt')
nltk.download('vader_lexicon')
