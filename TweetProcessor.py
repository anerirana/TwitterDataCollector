#!/usr/bin/env python
import pandas as pd
from pandas.errors import EmptyDataError
import CustomLogger

TWEETS_FILE_PATH = './Data/Tweets.csv'
logger = CustomLogger.getCustomLogger()


class Tweet():

	def __init__(self, tweet_id):
		self.tweet_id = tweet_id
		self.tweet_url = None
		self.media_id = None
		self.video_url = None
		self.mpeg_url = None
		
	def as_dict(self):
		return {'TweetID': self.tweet_id, 'TweetURL': self.tweet_url, 'MediaID': self.media_id, 'VideoURL': self.video_url, 'MpegURL': self.mpeg_url}

	# Extended entities will have media info
	def search_extended_entities(self, tweet):
		logger.debug("Start: search_extended_entities()")
		try:
			extended_entities = tweet['extended_entities']
			self.search_video_info(extended_entities)
		except KeyError:
			self.search_extended_tweet(tweet)
		except Exception:
			logger.error("Unknown Exception", exc_info=True)
		logger.debug("End: search_extended_entities()")

	# If tweet was longer than 140 charchters then information is stored in extended tweet
	def search_extended_tweet(self, tweet):
		logger.debug("Start: search_extended_tweet()")
		try:
			extended_tweet = tweet['extended_tweet']
			self.search_extended_entities(extended_tweet)
		except KeyError:
			self.search_retweeted_status(tweet)
		except Exception:
			logger.error("Unknown Exception", exc_info=True)
		logger.debug("End: search_extended_tweet()")

    # If it was a retweet, then entities will be stored in retweeted status
	def search_retweeted_status(self, tweet):
		logger.debug("Start: search_retweeted_status()")
		try:
			retweeted_status = tweet['retweeted_status']
			self.search_extended_entities(retweeted_status)
		except KeyError:
			logger.error(
			"Loop exhausted. Could not find video url for tweet id %s", self.tweet_id)
		except Exception:
			logger.error("Unknown Exception", exc_info=True)
			logger.debug("End: search_retweeted_status()")

	# Parse entities to search video media type and fetch video info
	def search_video_info(self, entities):
		logger.debug("Start: search_video_info()")
		for media in entities['media']:
			try:
				if media['type'] == "video":
					self.media_id = media['id_str']
					video_info = media['video_info']
					self.video_url = self.fetch_video_url(
						video_info)
					self.mpeg_url = self.fetch_mpeg_url(
						video_info)
					self.tweet_url = media['expanded_url']
			except KeyError:
				continue
			except Exception:
				logger.error("Unknown Exception", exc_info=True)
		logger.debug("End: search_video_info()")

    # Return video url from video  info
	def fetch_video_url(self, video_info):
		logger.debug("Start: fetch_video_url()")
		min_bitrate = 1000000000000000000
		video_url = ""
		try:
			variants = video_info['variants']
			for variant in variants:
				if variant['content_type'] == "video/mp4":
					bitrate = variant['bitrate']
					# Storing url for smallest bitrate to optimize memory
					if bitrate < min_bitrate:
						min_bitrate = bitrate
						video_url = variant['url']
			return video_url
		except KeyError:
			logger.error("Key Exception", exc_info=True)
			return None
		except Exception:
			logger.error("Unknown Exception", exc_info=True)
			return None
		logger.debug("End: fetch_video_url()")

	# Return mpeg url from video  info
	def fetch_mpeg_url(self, video_info):
		logger.debug("Start: fetch_mpeg_url()")
		mpeg_url = ""
		try:
			variants = video_info['variants']
			for variant in variants:
				if variant['content_type'] == "application/x-mpegURL":
					mpeg_url = variant['url']
			return mpeg_url
		except KeyError:
			logger.error("Key Exception", exc_info=True)
			return None
		except Exception:
			logger.error("Unknown Exception", exc_info=True)
			return None
		logger.debug("End: fetch_mpeg_url()")


class TweetParser:

	def __init__(self, results):
		self.results = results

	# Collect data for each tweet
	def store_tweet_data(self):
		logger.debug("Start: store_tweet_data()")
		tweets = []
		logger.info("Parsing %d tweets", len(self.results))
		for tweet_data in self.results:
			tweet_id = tweet_data['id_str']
			logger.debug("Parsing tweet ID: %s", tweet_id)
			tweet = Tweet(tweet_id)
			tweet.search_extended_entities(tweet_data)
			if (tweet.tweet_id != None) and (tweet.tweet_url != None) and (tweet.media_id != None) and (tweet.video_url != None) and (tweet.mpeg_url != None):
				tweets.append(tweet.as_dict())
			else:
				logger.info(
					"Could not find all values, skipping tweet ID: %s", tweet_id)

		logger.info("Storing %d tweets in csv", len(tweets))
		try:
			old_df = pd.read_csv(TWEETS_FILE_PATH, index_col=0)
			logger.debug("Data read from csv file:")
			logger.debug(old_df)
			new_df = pd.DataFrame(tweets)
			logger.debug("New data collected from tweets:")
			logger.debug(new_df)
			new_df = old_df.append(new_df, ignore_index=True)
			new_df.to_csv(TWEETS_FILE_PATH)
		except (EmptyDataError, FileNotFoundError):
			# When storing tweets first time, file will be empty. Directly write new tweets in csv.
			new_df = pd.DataFrame(tweets)
			logger.debug("New data collected from tweets:")
			logger.debug(new_df)
			new_df.to_csv(TWEETS_FILE_PATH)
		except Exception:
			logger.error("Unknown Exception", exc_info=True)
		logger.debug("End: store_tweet_data()")
