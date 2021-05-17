#!/usr/bin/env python

import os
import argparse
import requests
from TweetProcessor import TweetParser
import CustomLogger

BEARER_TOKEN = "Bearer YOUR_BEARER_TOKEN"
DEV_URL = "https://api.twitter.com/1.1/tweets/search/30day/development.json?tweet_mode='extended'"
TEST_URL = "https://api.twitter.com/1.1/tweets/search/fullarchive/test.json?tweet_mode='extended'"
KEYWORD_FILE_PATH = "./Data/Keywords.txt"
logger = CustomLogger.getCustomLogger()


def get_keyword_string():
    logger.debug("Start : get_keyword_string()")
    opening_bracket = "("
    closing_bracket = ")"
    keyword_string = opening_bracket
    whitespace = " "
    negation_keyword = "-porn "

    file_obj = open(KEYWORD_FILE_PATH, "r")
    keywords = file_obj.readlines()
    num_keywords = len(keywords)
    for (i,keyword) in enumerate(keywords):
        logger.info("keyword directly after fetching from the file : %s", keyword)
        keyword = keyword[:-1]
        logger.info("keyword after trimming the last character : %s", keyword)
        if i == num_keywords - 1:
          keyword_string = keyword_string+str(keyword)+str(closing_bracket)+str(whitespace)+negation_keyword
        else:
          keyword_string = keyword_string+str(keyword)+str(whitespace)+"OR"+str(whitespace)
    keyword_string = "(feminazi OR sexist OR Sexism OR misogyny OR feminist OR objectification OR (Penis envy) OR Patriarchy OR (Purity Culture) OR (Slut Shaming) OR Manterrupting OR Mansplaining OR TERF OR (Hostile Sexism) OR (Toxic masculinity)) " + negation_keyword 
    # Sample keywords that can be used together to search for a particular type of hate speech :-
    # (Ugly OR extremist OR terrorist OR whore OR bigot OR bastard) 
    # (Merkin OR Buckra OR Hick OR Honky OR Peckerwood OR Redneck OR (Country Bumpkin) OR (Hillbilly Bumpkin) OR (Trailer trash) OR (White trash))
    # (feminazi OR sexist OR Racist OR Nationalist OR Superiority OR Bigot OR Sexism OR extremist OR leftist OR misogyny)
    logger.info("Keyword string generated : %s", keyword_string)
    logger.debug("End  : get_keyword_string()")
    return keyword_string


def fetch_tweets(url, keyword_string, next_token):
    logger.debug("Start : fetch_tweets(%s,%s)", keyword_string, next_token)
    payload1 = '{"query":"'
    payload2 = 'has:videos lang:en","maxResults":"100"'
    payload3 = ',"next":"'+str(next_token)+'"'
    payload4 = '}'
    if next_token:
      payload = str(payload1)+str(keyword_string)+str(payload2)+str(payload3)+str(payload4)
    else :
      payload = str(payload1)+str(keyword_string)+str(payload2)+str(payload4)
    logger.info("Payload : %s", payload)
    headers = {"Authorization": BEARER_TOKEN}
    response = requests.post(url, data=payload, headers=headers)
    json_response = response.json()
    logger.info("Dictionary keys from response:")
    logger.info(json_response.keys())
    if "results" in json_response.keys():
        logger.info("Response result : %s", json_response["results"])
    else :
        logger.warning("No results key present in the Response json")
    logger.debug("End : fetch_tweets(%s,%s)", keyword_string, next_token)
    return json_response


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', dest='env', default='dev', help='The environment for twitter endpoint. Right now only \'dev\' and \'test\' are supported')
    args = parser.parse_args()
    url = ''
    if args.env == 'dev':
        url = DEV_URL
    elif args.env == 'test':
        url = TEST_URL

    curr_next=''
    try :
        keyword_string = get_keyword_string()
        response = fetch_tweets(url, keyword_string, None)
        tweet_parser = TweetParser(response["results"])
        tweet_parser.store_tweet_data()
        if "next" in response.keys():
            next_token = response["next"]
            curr_next = next_token
        else :
            next_token = None
        while next_token :
            logger.debug("Getting tweets from the next page with the token : %s", next_token)
            curr_next = next_token
            response = fetch_tweets(url, keyword_string, next_token)
            tweet_parser = TweetParser(response["results"])
            tweet_parser.store_tweet_data()
            if "next" in response.keys():
                next_token = response["next"]
            else : 
                next_token = None
        logger.debug("Logging end of tweet search; no further next token found")
    except KeyError:
        logger.error("Logging next_token : %s", curr_next)
        logger.error("Error fetching tweets", exc_info=True)
        logger.error(response["error"])
    except Exception:
        logger.error("Logging next_token : %s", curr_next)
        logger.error("Unknown Exception", exc_info=True)
