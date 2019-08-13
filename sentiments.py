
from tweet_compiler import get_twitter_tokens, twitter_auth
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


def grab_trending_tweets_tweepy(trend_topic, number_of_tweets, api=None):

    try:

        if api is None:
            # securing the credentials for logging in
            consumer_key, consumer_secret, access_token, access_token_secret = get_twitter_tokens()
            api = twitter_auth(consumer_key, consumer_secret, access_token, access_token_secret)

        # setting up our search query
        query = tweepy.Cursor(api.search, q=trend_topic, lang="en").items(number_of_tweets)

        # and saving the tweets into a list
        list_of_current_tweets = [tweet.text for tweet in query]
        logger.info(f"Grabbed trending tweets about {trend_topic} with Tweepy. "
                     f"Returning list with {len(list_of_current_tweets)} tweets")
        return list_of_current_tweets

    except TweepError as e:
        logger.exception(f"Unable to grab trending tweets for {trend_topic} because of the "
                         "following error: ", e.response.text)
        return []


def grab_tweets_by_topic_alt(topic, num_of_tweets):

    # this is an alternative function for grabbing tweets on a current hashtag
    # just in case twitter is throwing an error with the tweepy approach
    # it is not preferable tho, because tweets can't be filtered by language

    tweet_criteria = got.manager.TweetCriteria().setQuerySearch(topic) \
                                                .setMaxTweets(num_of_tweets)

    tweets = got.manager.TweetManager.getTweets(tweet_criteria)

    topical_tweet_list = [tweet.text for tweet in tweets]

    return topical_tweet_list


def tweet_cleaner(tweet):
    
    # removing @mentions allng with RTs and
    # #-characters (keeping the word/tag itself tho)
    tweet = re.sub(r"(?<!\w)RT|@[A-Za-z0-9]+(_[A-Za-z0-9]+)?", "", tweet)
    tweet = re.sub("#", "", tweet)
    
    # this is just substituting the weird ’ with a
    # regular ' since it is not properly detected otherwise
    tweet = re.sub("’", "'", tweet)
    
    # removing some typical urls
    tweet = re.sub(r"(https?:\/\/)(\s)*(www\.)?(\s)*((\w|\s)+\.)*([\w\-\s]+\/)*([\w\-]+)((\?)?[\w\s]*=\s*[\w\%&]*)*",
                   "", tweet)
    tweet = re.sub(r"pic\.twitter\.com\S*\s?", "", tweet)
    tweet = re.sub(r"bit\.ly.*\s?", "", tweet)
    tweet = re.sub(r"instagr\.am.*\s?", "", tweet)
    tweet = re.sub(r"t\.co.*\s?", "", tweet)
    tweet = re.sub(r"twitter\.com.*\s?", "", tweet)
    tweet = re.sub(r"[\w/\-?=%.]+\.[\(com)/\-?=%.]+", "", tweet)  # removes urls without http or www (hopefully lol)
    
    # removing all numbers and also times (i.e. "12 PM PST"), 
    tweet = re.sub(r"[0-9]+\s*([AaPp][Mm])?\s*([Pp][Ss][Tt])?\s*", "", tweet)
    tweet = re.sub(r"\…", "", tweet)
    
    # removing punctuation and extra spaces between words
    tweet = "".join([char for char in tweet if char not in string.punctuation])
    tweet = " ".join(tweet.split())
    
    return tweet


def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return 'n'


def tokenize_lemmatize(tweet):
    wn = nltk.WordNetLemmatizer()

    lemmatized_tweet = []

    tokens = nltk.word_tokenize(tweet)
    tagged = nltk.pos_tag(tokens)  # returns a list of (word, tag)-tuples

    for item in tagged:
        word = item[0]
        tag = item[1]
        lemmatized = wn.lemmatize(word, pos=get_wordnet_pos(tag))
        lemmatized_tweet.append(lemmatized)

    return lemmatized_tweet


def remove_stopwords(tweet):
    stop_words = stopwords.words('english')
    more_noise = ['i’m', "im", "w", "u"]
    stop_words.extend(more_noise)
    # first condition removes stopwords, second condition removes empty strings
    # which for some reason turned up when I tried this the first time around
    tweet = [word for word in tweet if word.lower() not in stop_words and word]

    return tweet


def analyze_tweet_list(tweet_list):

    sentiments = []

    for tweet in tweet_list:
        blob = TextBlob(tweet)
        sentiments.append(blob.polarity)

    logger.info(f"Grabbed sentiments... mean polarity was {np.mean(sentiments)}")

    return sentiments


if __name__ == "__main__":

    logging.basicConfig(filename='myapp.log', level=logging.INFO)

    hashtag = '#kkwbeauty'
    num_of_tweets = 50

    logging.info(f"The hashtag we're working with is {hashtag}, we're looking at {num_of_tweets} tweets")

    # tweet_list = grab_tweets_by_topic_alt(hashtag, num_of_tweets)
    tweet_list = grab_trending_tweets_tweepy(hashtag, num_of_tweets)
    og_sentiments = analyze_tweet_list(tweet_list)

    first_cleanse = [tweet_cleaner(tweet) for tweet in tweet_list]

    lemmatized_tweets = [tokenize_lemmatize(tweet) for tweet in first_cleanse]

    no_stopwords = [remove_stopwords(tweet) for tweet in lemmatized_tweets]
    cleaned_tweets = [" ".join(tweet) for tweet in no_stopwords]
    clean_sentiments = analyze_tweet_list(cleaned_tweets)

    for og_tweet, og_sent, cl_tweet, cl_sent in zip(tweet_list,
                                                    og_sentiments,
                                                    cleaned_tweets,
                                                    clean_sentiments):
        print("og tweet: ", og_tweet)
        print("og sent: ", og_sent)
        print("clean tweet: ", cl_tweet)
        print("clean sent: ", cl_sent)
        print(np.mean(og_sentiments), np.mean(clean_sentiments))
        print(20*"-")
