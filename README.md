# TwitterDataCollector
Collects Tweets with attached videos and contains the given keywords. It also downloads videos attached to the tweets in the output folder.

## Installation
To install all the required packages run
`pip install -r requirements.txt`
  
Additional packages :-
1. You need to install ffmpeg according to underlying enviornments.
    * For anaconda virtual environment use: `conda install ffmpeg`
    * For MacOS use: `brew install ffmpeg`
    * For Windows OS use: `pip install ffmpeg`

## Tweet Parser
Refer the official twitter API documentation for latest tweet object information : https://developer.twitter.com/en/docs/twitter-api/premium/data-dictionary/overview

Recursive calls have been implemented, as the extended entities object containing media information can be encapsulated inside different objects depending on nature of the tweet.

Samples for reference :
```
results[0]['extended_entities']['media'][0]['video_info']['variants'][0]['url']
results[0]['extended_tweet']['extended_entities']['media'][0]['video_info']['variants'][0]['url']
results[0]['retweeted_status']['extended_entities']['media'][0]['video_info']['variants'][0]['url']
results[0]['retweeted_status']['extended_tweet']['extended_entities']['media'][0]['video_info']['variants'][0]['url']
```
