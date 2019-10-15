import unittest
from unittest.mock import patch
import os
import reddit_images


class TestRedditImages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove("url_tracking.txt")
        except FileNotFoundError:
            pass

    def setUp(self):
        config = "[REDDIT]\nclient_id = id\nclient_secret = secret\nuser_agent = agent"
        with open("testconfig.ini", "w") as f:
            f.write(config)

    def tearDown(self):
        os.remove("testconfig.ini")

    def test_get_reddit_tokens(self):
        self.assertEqual((reddit_images.get_reddit_tokens(filename="testconfig.ini")), ("id", "secret", "agent"))
        with self.assertRaises(KeyError):
            reddit_images.get_reddit_tokens(filename="fakefile.ini")

    def test_extract_image_urls(self):
        client_id, client_secret, user_agent = "id", "secret", "agent"  # fake api keys
        urls = reddit_images.extract_image_urls(client_id, client_secret, user_agent, sub="pasta", amount=10)
        self.assertIsInstance(urls, list)
        self.assertEqual(urls, [])
        with patch("reddit_images.praw.Reddit") as mocked_praw:
            reddit_images.extract_image_urls(client_id, client_secret, user_agent, sub="pasta", amount=10)
            mocked_praw.assert_called_with(client_id="id", client_secret="secret", user_agent="agent")

    def test_get_new_file_number(self):
        pass

    def test_filter_unused_pics(self):
        self.assertEqual(reddit_images.filter_unused_pics([]), [])
        self.assertRaises(FileNotFoundError)
        image_list = ["a.jpg", "b.jpg", "c.jpg", "d.jpg"]
        new_img_list = reddit_images.filter_unused_pics(image_list)
        self.assertEqual(new_img_list, image_list[::-1])
        self.assertTrue(os.path.exists("url_tracking.txt"))
        with open("url_tracking.txt", "r") as f:
            url = f.read()
            self.assertEqual(url, image_list[-1])

    def test_save_new_images(self):
        pass


if __name__ == '__main__':
    unittest.main()
