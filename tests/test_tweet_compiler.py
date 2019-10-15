import unittest
import tweet_compiler
import os
import unittest.mock as mock


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
            mocked_auth.assert_called_with("a", "b")
        with mock.patch("tweet_compiler.tweepy.OAuthHandler.set_access_token") as mocked_api:
            tweet_compiler.twitter_auth("a", "b", "c", "d")
            mocked_api.assert_called_with("c", "d")

    @mock.patch("tweet_compiler.tweepy.API")
    def test_get_twitter_media_id(self, mock_api):
        with self.assertRaises(FileNotFoundError):
            tweet_compiler.get_twitter_media_id(mock_api, "fakefile.jpg")
        mock_api.media_upload.return_value.media_id_string = "id"
        self.assertIsInstance(tweet_compiler.get_twitter_media_id(mock_api, "testconfig.ini"), list)
        self.assertEqual(tweet_compiler.get_twitter_media_id(mock_api, "testconfig.ini"), ['id'])

    @mock.patch("tweet_compiler.tweepy.API")
    def test_get_local_trends(self, mock_api):
        fake_trends = [{'trends': [{'name': 'TheVoice', 'url': 'url.com/'},
                                   {'name': 'KUWTK', 'url': 'url.com'}]}]
        mock_api.trends_place.return_value = fake_trends
        self.assertEqual(tweet_compiler.get_local_trends(mock_api), ['TheVoice', 'KUWTK'])

    def test_filter_non_offensive_hashtags(self):
        test_input = ["#deathspiral", "#cute", "othertopic",
                      "#rippikachu", "#someonedied", "#terribleshooting"]
        test_output = tweet_compiler.filter_non_offensive_hashtags(test_input)
        self.assertNotIn('#deathspiral', test_output)
        self.assertNotIn('othertopic', test_output)
        self.assertNotIn('#rippikachu', test_output)
        self.assertNotIn('#someonedied', test_output)
        self.assertIn('#cute', test_output)

    def test_select_tweet(self):
        pass

    def test_compile_status(self):
        pass

    def test_update_status(self):
        pass


if __name__ == '__main__':
    unittest.main()
