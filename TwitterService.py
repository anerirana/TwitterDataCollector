#!/usr/bin/env python

import os
import requests
from TweetProcessor import TweetParser

BEARER_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAAAA2JQEAAAAA2mlhZpa5zBG2PqvL%2BGoADWDO5GA%3Dk50Ddhm8r7GsCNUF3uhgX95BTbMCgpAPQhn8ds1o9KBtp6HUD6"
URL = "https://api.twitter.com/1.1/tweets/search/fullarchive/development.json?tweet_mode='extended'"
KEYWORD_FILE_PATH = "./Data/Keywords.txt"


def get_keyword_string():
    opening_bracket = "("
    closing_bracket = ")"
    keyword_string = opening_bracket
    whitespace = " "

    file_obj = open(KEYWORD_FILE_PATH, "r")
    keywords = file_obj.readlines()
    num_keywords = len(keywords)
    for (i,keyword) in enumerate(keywords):
        keyword = keyword[:-1]
        if i == num_keywords - 1:
          keyword_string = keyword_string+str(keyword)+str(closing_bracket)+str(whitespace)
        else:
          keyword_string = keyword_string+str(keyword)+str(whitespace)+"OR"+str(whitespace)
    return keyword_string


def fetch_tweets(keyword_string, next_token):
    payload1 = '{"query":"'
    payload2 = 'has:videos lang:en","maxResults":"15"'
    payload3 = ',"next":"'+str(next_token)+'"'
    payload4 = '}'
    if next_token:
      payload = str(payload1)+str(keyword_string)+str(payload2)+str(payload3)+str(payload4)
    else :
      payload = str(payload1)+str(keyword_string)+str(payload2)+str(payload4)
    print(payload)
    headers = {"Authorization": BEARER_TOKEN}
    response = requests.post(URL, data=payload, headers=headers)
    json_response = response.json()
    print(json_response.keys())
    return json_response

curr_next=''
try :
    keyword_string = get_keyword_string()
    response = fetch_tweets(keyword_string, None)
    tweet_parser = TweetParser(response["results"], debug_scope=0)
    tweet_parser.store_tweet_data()
    if "next" in response.keys():
        next_token = response["next"]
        curr_next = next_token
    else :
        next_token = None
    while next_token :
        curr_next = next_token
        response = fetch_tweets(keyword_string, next_token)
        tweet_parser = TweetParser(response["results"], debug_scope=0)
        tweet_parser.store_tweet_data()
        if "next" in response.keys():
            next_token = response["next"]
        else : 
            next_token = None
    print("Logging end of tweet search; no further next token found")
except KeyError:
    print("Logging next_token in case processing fails : ")
    print(curr_next)
    print("Error fetching tweets")
    print(response["error"])
except Exception as e:
    print("Logging next_token in case processing fails : ")
    print(curr_next)
    print("Unknown exception")
    print(e)
