<h3><b><a href="https://twitter.com/p_a_s_t_a_b_o_t">@p_a_s_t_a_b_o_t</a></b></h3>

Twitter bot that downloads images from <a href="https://www.reddit.com/r/pasta/">r/pasta</a> and tweets them 
in combination with a pre-written tweet and a currently trending hashtag.

<h4>Usage:</h4>

Install requirements.txt with pip:

`pip install -r requirements.txt`

Before running pastabot.py, a few nltk corpora need to be downloaded:

```
import nltk
nltk.download('stopwords', 'wordnet', 'punkt', 'averaged_perceptron_tagger')
```

Start the bot:

`$ python3 pastabot.py`

<ul>
<li>
Automatically creates <i>config.ini</i> file on the first run.</li>
<li>
Fill in API keys for Twitter and Reddit and run again.</li>
<li>
Creates a working directory containing the downloaded images as <i>pastapics</i>.</li>
<li>
Sleeps for 12-18 hours after each tweet.</li>
<li>
<i>tweet.txt</i> file contains tweet templates that can be added upon/edited. </li>
</ul>


<h6>Info on how to acquire API keys for twitter and reddit:</h6>
<ul>
<li><a href="https://projects.raspberrypi.org/en/projects/getting-started-with-the-twitter-api">
Getting started with the Twitter API</a></li>
<li><a href="https://alpscode.com/blog/how-to-use-reddit-api/">How to use Reddit API</a></li>
<li><a href="https://developer.twitter.com/en/docs">Official Twitter API documentation</a></li>
<li><a href="https://www.reddit.com/dev/api">Official Reddit API documentation</a></li>
</ul>

