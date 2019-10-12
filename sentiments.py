
import re
from textblob import TextBlob
import tweepy
from tweepy import TweepError
import GetOldTweets3 as got
import string
import numpy as np
import logging
import nltk
from nltk.corpus import wordnet, stopwords

logger = logging.getLogger("pastabot.sentiments")


def grab_trending_tweets(api, trend_topic, number_of_tweets, language='en'):

    """
    grabs a certain number_of_tweets about a trend_topic
    in a specific language and returns them as a list
    :param api: tweepy api object
    :param trend_topic: a topic; tweets on which are grabbed
    :param number_of_tweets: number of tweets to be grabbed
    :param language: language of the tweets to grab, defaults to english
    :return: list of current tweets about the selected topic
    """

    try:

        # setting up search query
        query = tweepy.Cursor(api.search, q=trend_topic, lang=language).items(number_of_tweets)

        # and saving the tweets into a list
        list_of_current_tweets = [tweet.text for tweet in query]

        logger.debug(f"Grabbed trending tweets about {trend_topic} with Tweepy. "
                     f"Returning list with {len(list_of_current_tweets)} tweets")

        return list_of_current_tweets

    except TweepError as e:

        logger.exception(f"Unable to grab trending tweets for {trend_topic} because of the "
                         "following error: ", e.response.text)

        return []


def grab_tweets_by_topic_alt(topic, num_of_tweets):
    """
    alternative function for grabbing tweets on a current hashtag.
    NOT PREFERABLE, because tweets can't be filtered by language.
    not currently being used
    :param topic: a topic; tweets on which are grabbed
    :param num_of_tweets: number of tweets to be grabbed
    :return: list of current tweets about the selected topic
    """

    tweet_criteria = got.manager.TweetCriteria().setQuerySearch(topic) \
                                                .setMaxTweets(num_of_tweets)

    tweets = got.manager.TweetManager.getTweets(tweet_criteria)

    topical_tweet_list = [tweet.text for tweet in tweets]

    return topical_tweet_list


def cleanse_tweet(tweet):
    """
    removes urls, numbers, punctuation etc.
    :param tweet: a tweet
    :returns cleaned tweet
    """
    
    # removing @mentions along with RTs and #-characters
    tweet = re.sub(r"(?<!\w)RT|@[A-Za-z0-9]+(_[A-Za-z0-9]+)?", "", tweet)
    tweet = re.sub("#", "", tweet)
    
    # this is just substituting ’ with a ' since it is not properly detected in removing punctuation
    tweet = re.sub("’", "'", tweet)
    
    # removing some typical urls
    tweet = re.sub(r"(https?:\/\/)(\s)*(www\.)?(\s)*((\w|\s)+\.)*([\w\-\s]+\/)*([\w\-]+)((\?)?[\w\s]*=\s*[\w\%&]*)*",
                   "", tweet)
    tweet = re.sub(r"pic\.twitter\.com\S*\s?", "", tweet)
    tweet = re.sub(r"bit\.ly.*\s?", "", tweet)
    tweet = re.sub(r"instagr\.am.*\s?", "", tweet)
    tweet = re.sub(r"t\.co.*\s?", "", tweet)
    tweet = re.sub(r"twitter\.com.*\s?", "", tweet)
    tweet = re.sub(r"[\w/\-?=%.]+\.[\(com)/\-?=%.]+", "", tweet)  # removes urls without http or www
    
    # removing all numbers and also times (i.e. "12 PM PST"), 
    tweet = re.sub(r"[0-9]+\s*([AaPp][Mm])?\s*([Pp][Ss][Tt])?\s*", "", tweet)
    tweet = re.sub(r"\…", "", tweet)
    
    # removing punctuation and extra spaces between words
    tweet = "".join([char for char in tweet if char not in string.punctuation])
    tweet = " ".join(tweet.split())
    
    return tweet


def convert_pos_tag(treebank_tag):

    """
    helper function that converts the pos-tags nltk.pos_tag() returns
    into pos tags nltk.WordNetLemmatizer can understand.
    """

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return 'n'  # default tag to fall back on


def tokenize_lemmatize_tweet(tweet):

    """
    function for tokenizing and lemmatizing tweets
    uses nltk wordnet lemmatizer
    includes part of speech tagging for more accurate lemmatization
    """

    wn = nltk.WordNetLemmatizer()

    lemmatized_tweet = []

    tokens = nltk.word_tokenize(tweet)
    tagged = nltk.pos_tag(tokens)  # returns a list of (word, tag)-tuples

    for item in tagged:
        word = item[0]
        tag = item[1]
        lemmatized = wn.lemmatize(word, pos=convert_pos_tag(tag))
        lemmatized_tweet.append(lemmatized)

    return lemmatized_tweet


def remove_stopwords(tweet):
    """
    removes stopwords from tweet. uses nltk.corpus stopwords.
    :param tweet: tweet, still containing stopwords
    :return: tweet, free of stopwords
    """

    stop_words = stopwords.words('english')
    more_noise = ['i’m', "im", "w", "u"]
    stop_words.extend(more_noise)
    tweet = [word for word in tweet if word.lower() not in stop_words and word]

    return tweet


def analyze_tweet_list(tweet_list):

    """
    uses TextBlob to extract polarity of each tweet in a list of tweets
    :returns: list of polarity values (between -1 and 1)
    """

    sentiments = []

    for tweet in tweet_list:
        blob = TextBlob(tweet)
        sentiments.append(blob.polarity)

    logger.debug(f"Grabbed sentiments... mean polarity was {np.mean(sentiments)}")

    return sentiments

