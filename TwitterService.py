#!/usr/bin/env python

import os
import requests
from TweetProcessor import TweetParser
import CustomLogger

BEARER_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAAAA2JQEAAAAA2mlhZpa5zBG2PqvL%2BGoADWDO5GA%3Dk50Ddhm8r7GsCNUF3uhgX95BTbMCgpAPQhn8ds1o9KBtp6HUD6"
URL = "https://api.twitter.com/1.1/tweets/search/fullarchive/development.json?tweet_mode='extended'"
KEYWORD_FILE_PATH = "./Data/Keywords.txt"
logger = CustomLogger.getCustomLogger()


def get_keyword_string():

    logger.debug("Start : get_keyword_string()")
    opening_bracket = "("
    closing_bracket = ")"
    keyword_string = opening_bracket
    whitespace = " "

    file_obj = open(KEYWORD_FILE_PATH, "r")
    keywords = file_obj.readlines()
    num_keywords = len(keywords)
    for (i,keyword) in enumerate(keywords):
        logger.info("keyword directly after fetching from the file : %s", keyword)
        keyword = keyword[:-1]
        logger.info("keyword after trimming the last character : %s", keyword)
        if i == num_keywords - 1:
          keyword_string = keyword_string+str(keyword)+str(closing_bracket)+str(whitespace)
        else:
          keyword_string = keyword_string+str(keyword)+str(whitespace)+"OR"+str(whitespace)
    logger.info("Keyword string generated : %s", keyword_string)
    logger.debug("End  : get_keyword_string()")
    return keyword_string


def fetch_tweets(keyword_string, next_token):
    logger.debug("Start : fetch_tweets(%s,%s)", keyword_string, next_token)
    payload1 = '{"query":"'
    payload2 = 'has:videos lang:en","maxResults":"15"'
    payload3 = ',"next":"'+str(next_token)+'"'
    payload4 = '}'
    if next_token:
      payload = str(payload1)+str(keyword_string)+str(payload2)+str(payload3)+str(payload4)
    else :
      payload = str(payload1)+str(keyword_string)+str(payload2)+str(payload4)
    logger.info("Payload : %s", payload)
    headers = {"Authorization": BEARER_TOKEN}
    response = requests.post(URL, data=payload, headers=headers)
    json_response = response.json()
    logger.info(json_response.keys())
    if "results" in json_response.keys():
        logger.info("Response result : %s", json_response["results"])
    else :
        logger.warning("No results key present in the Response json")
    logger.debug("End : fetch_tweets(%s,%s)", keyword_string, next_token)
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
        logger.debug("Getting tweets from the next page with the token : %s", next_token)
        curr_next = next_token
        response = fetch_tweets(keyword_string, next_token)
        tweet_parser = TweetParser(response["results"], debug_scope=0)
        tweet_parser.store_tweet_data()
        if "next" in response.keys():
            next_token = response["next"]
        else : 
            next_token = None
    logger.debug("Logging end of tweet search; no further next token found")
except KeyError:
    logging.error("Logging next_token : %s", curr_next)
    logging.error("Error fetching tweets", exc_info=True)
    logging.error(response["error"])
except Exception as e:
    logging.error("Logging next_token : %s", curr_next)
    logging.error("Unknown Exception", exc_info=True)
