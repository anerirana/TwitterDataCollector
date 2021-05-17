# TwitterDataCollector
Collects Tweets that contians the given keywords and were posted with a video. It also downloads and extracts the audios from videos attached to these tweets.

## Installation
To install all the required packages run
`pip install -r requirements.txt`
  
Additional packages :-
1. You need to install ffmpeg according to underlying enviornments.
    * For anaconda virtual environment use: `conda install ffmpeg`
    * For MacOS use: `brew install ffmpeg`
    * For Windows OS use: `pip install ffmpeg`

## Twitter Service
To interact with twitter API edit `TwitterService`
1. Insert the Bearer token 
2. Edit dev and test URLs with your project name
3. Run `python3 TwitterService.py -e dev`

This extracts tweets using the specified keyword string, parses tweet response and stores required deatils in csv file.

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

## Audio Downloader
Run `python3 AudioDownloader.py` to download audios in wav format of media posted with tweets. The data collected using `TwitterSerivce` will be used.
