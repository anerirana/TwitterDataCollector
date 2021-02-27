#!/usr/bin/env python

import os
import requests
from TweetProcessor import TweetParser

BEARER_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAAFZkIwEAAAAAukM9PY5a8Z0K1U3X4frDp%2BeZX4o%3Dv2Ir1HreMt9HvqjKJWaWT6Jx7gWnbCkKyiDbANzeqfQ84B2piL"
FILENAME = "/content/drive/MyDrive/OffensiveLanguageClassification/sensiive_keywords.txt"
URL = "https://api.twitter.com/1.1/tweets/search/fullarchive/HushUp.json?tweet_mode='extended'"
KEYWORD_FILE_PATH = "./Data/Keywords.txt"


def get_keyword_string():
    keyword_string = ""
    whitespace = " "

    file_obj = open(KEYWORD_FILE_PATH, "r")
    keywords = file_obj.readlines()
    for keyword in keywords:
        keyword_string = keyword_string+str(keyword)+str(whitespace)
    return keyword_string


def fetch_tweets(keyword_string):
    payload1 = '{"query":"'
    payload2 = 'has:videos lang:en","maxResults":"15"}'
    payload = str(payload1)+str(keyword_string)+str(payload2)
    print(payload)
    headers = {"Authorization": BEARER_TOKEN}
    response = requests.post(URL, data=payload, headers=headers)
    json_response = response.json()
    print(json_response.keys())
    return json_response


keyword_string = get_keyword_string()
response = fetch_tweets(keyword_string)
tweet_parser = TweetParser(response["results"], debug_scope=0)
tweet_parser.store_tweet_data()
