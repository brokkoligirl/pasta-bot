import unittest
from unittest import mock
from io import StringIO
import tweet_compiler
import os


class TestTweetCompiler(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        config = "[TWITTER]\nconsumer_key = ckey\nconsumer_secret = csecret\n" \
                 "access_token = atoken\naccess_token_secret = atokensecret"
        with open("testconfig.ini", "w") as f:
            f.write(config)

    def tearDown(self):
        os.remove("testconfig.ini")

    def test_get_twitter_tokens(self):
        keys = tweet_compiler.get_twitter_tokens(filename="testconfig.ini")
        self.assertEqual(len(keys), 4)
        self.assertEqual(keys, ("ckey", "csecret", "atoken", "atokensecret"))
        with self.assertRaises(KeyError):
            tweet_compiler.get_twitter_tokens(filename="fakefile.ini")

    def test_twitter_auth(self):
        with mock.patch("tweet_compiler.tweepy.OAuthHandler") as mocked_auth:
            tweet_compiler.twitter_auth("a", "b", "c", "d")
            mocked_auth.assert_called_once_with("a", "b")
        with mock.patch("tweet_compiler.tweepy.OAuthHandler.set_access_token") as mocked_api:
            tweet_compiler.twitter_auth("a", "b", "c", "d")
            mocked_api.assert_called_once_with("c", "d")
        with mock.patch("tweet_compiler.tweepy.API", return_value="ww"):
            tweet_compiler.twitter_auth("a", "b", "c", "d")
            self.assertEqual(tweet_compiler.twitter_auth("a", "b", "c", "d"), "ww")

    @mock.patch("tweet_compiler.tweepy.API")
    def test_get_twitter_media_id(self, mock_api):
        with self.assertRaises(FileNotFoundError):
            tweet_compiler.get_twitter_media_id(mock_api, "fakefile.jpg")
        mock_api.media_upload.return_value.media_id_string = "id"
        self.assertIsInstance(tweet_compiler.get_twitter_media_id(mock_api, "testconfig.ini"), list)
        self.assertEqual(tweet_compiler.get_twitter_media_id(mock_api, "testconfig.ini"), ['id'])
        with mock.patch('tweet_compiler.open') as mock_open:
            file = mock_open.return_value.__enter__.return_value = 'testing'
            tweet_compiler.get_twitter_media_id(mock_api, file)
            mock_api.media_upload.assert_called_with(filename="testing", file="testing")

    @mock.patch.object(tweet_compiler.tweepy.API, "trends_place")
    def test_get_local_trends(self, mock_api):
        fake_trends = [{'trends': [{'name': 'TheVoice', 'url': 'url.com/'},
                                   {'name': 'KUWTK', 'url': 'url.com'}]}]
        mock_api.trends_place.return_value = fake_trends
        self.assertEqual(tweet_compiler.get_local_trends(mock_api), ['TheVoice', 'KUWTK'])
        mock_api.trends_place.assert_called_with(id=23424977)
        tweet_compiler.get_local_trends(mock_api, woeid=1)
        mock_api.trends_place.assert_called_with(id=1)

    def test_filter_non_offensive_hashtags(self):
        test_input = ["#deathspiral", "#cute", "othertopic",
                      "#rippikachu", "#someonedied", "#terribleshooting"]
        test_output = tweet_compiler.filter_non_offensive_hashtags(test_input)
        self.assertIsInstance(test_output, list)
        self.assertNotIn('#deathspiral', test_output)
        self.assertNotIn('othertopic', test_output)
        self.assertNotIn('#rippikachu', test_output)
        self.assertNotIn('#someonedied', test_output)
        self.assertNotIn('#terribleshooting', test_output)
        self.assertIn('#cute', test_output)
        self.assertEqual(tweet_compiler.filter_non_offensive_hashtags([]), [])

    def test_select_tweet(self):
        with self.assertRaises(FileNotFoundError):
            tweet_compiler.select_tweet('fakefile.txt')
        with mock.patch('tweet_compiler.open') as mock_open:
            mock_open.return_value.__enter__.return_value = StringIO('testing')
            self.assertEqual(tweet_compiler.select_tweet(), 'testing')

    @mock.patch("tweet_compiler.datetime.datetime")
    def test_compile_status(self, mock_date):
        hashtag = "#hello"
        start = tweet_compiler.compile_status("hashtag as first word", hashtag)
        self.assertEqual("#hello as first word", start)
        middle = tweet_compiler.compile_status("here, hashtag is in the middle", hashtag)
        self.assertEqual("here, #hello is in the middle", middle)
        end = tweet_compiler.compile_status("last word is hashtag", hashtag)
        self.assertEqual("last word is #hello", end)

        # testing exception handling
        mock_date.today.return_value = "today"
        mock_date.strftime.return_value = "October 15"
        nosplit = tweet_compiler.compile_status("word not used", hashtag)
        mock_date.today.assert_called_once()
        mock_date.strftime.assert_called_once_with("today", "%B %d")
        self.assertEqual(f"As a bot, I can't do much. But I can read a calendar. "
                         f"October 15, what an amazing day to look at some pasta ...", nosplit)

    @mock.patch("tweet_compiler.tweepy.API")
    def test_update_status(self, mock_api):
        media_id, status = 3, "hello"
        tweet_compiler.update_status(mock_api, media_id, status)
        mock_api.update_status.assert_called_once()
        mock_api.update_status.assert_called_with(media_ids=3, status="hello")
        with self.assertRaises(AttributeError):
            tweet_compiler.update_status("trash", media_id, status)


if __name__ == '__main__':

    unittest.main()
