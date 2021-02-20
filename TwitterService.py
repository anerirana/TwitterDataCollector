#!/usr/bin/env python

import requests
from TweetHandler import TweetParser

BEARER_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAAFZkIwEAAAAAukM9PY5a8Z0K1U3X4frDp%2BeZX4o%3Dv2Ir1HreMt9HvqjKJWaWT6Jx7gWnbCkKyiDbANzeqfQ84B2piL"

def fetch_tweets(keyword):
  url = "https://api.twitter.com/1.1/tweets/search/fullarchive/HushUp.json?tweet_mode='extended'"
  payload1='{"query":"'
  payload2=' has:videos","maxResults":"15"}'
  payload = str(payload1)+str(keyword)+str(payload2)
  print(payload)
  headers = {"Authorization": BEARER_TOKEN}
  response = requests.post(url, data=payload, headers=headers)
  json_response = response.json()
  print(json_response.keys()) 
  return json_response

response = fetch_tweets("white people")
tweet_parser = TweetParser(response["results"], debug_scope=1)
tweet_parser.fetch_tweet_data()