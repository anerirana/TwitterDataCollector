#!/usr/bin/env python

import requests
from TweetProcessor import TweetParser

BEARER_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAAFZkIwEAAAAAukM9PY5a8Z0K1U3X4frDp%2BeZX4o%3Dv2Ir1HreMt9HvqjKJWaWT6Jx7gWnbCkKyiDbANzeqfQ84B2piL"


def get_keyword_string():
    keyword_string = ""
    whitespace = " "

    file_obj = open(KEYWORD_FILE_PATH, "r")
    keywords = file_obj.readlines()
    for keyword in keywords:
        # keyword = keyword[:-1]
        keyword_string = keyword_string+str(keyword)+str(whitespace)
    return keyword_string


def fetch_tweets(keyword_string, next_token):
    payload1 = '{"query":"'
    payload2 = 'has:videos","maxResults":"15"'
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


try :
    keyword_string = get_keyword_string()
    response = fetch_tweets(keyword_string, None)
    tweet_parser = TweetParser(response["results"], debug_scope=0)
    tweet_parser.store_tweet_data()
    if "next" in response.keys():
        next_token = response["next"]
    else :
        next_token = None
    while next_token :
        print("Logging next_token in case processing fails : ")
        print(next_token)
        response = fetch_tweets(keyword_string,next_token)
        tweet_parser = TweetParser(response["results"], debug_scope=0)
        tweet_parser.store_tweet_data()
        if "next" in response.keys():
            next_token = response["next"]
        else : 
            next_token = None
    print("Logging end of tweet search; no further next token found")
except KeyError:
    print("Error fetching tweets")
    print(response["error"])
except Exception as e:
    print("Unknown exception")
    print(e)
