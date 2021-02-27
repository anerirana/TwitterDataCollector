#!/usr/bin/env python
from Helper import Helper
import pandas as pd

TWEETS_FILE_PATH = './Data/Tweets.csv'

class Tweet(Helper):

	def __init__(self, tweet_id):
		self.tweet_id = tweet_id
		self.tweet_url = None
		self.media_id = None
		self.video_url = None
		self.mpeg_url = None

	def as_dict(self):
		return {'TweetID': self.tweet_id, 'TweetURL': self.tweet_url, 'MediaID': self.media_id, 'VideoURL': self.video_url, 'MpegURL': self.mpeg_url}

	# Extended entities will have media info
	def search_extended_entities(self, tweet, debug_scope = 0):
		Helper.debug(debug_scope, "Searching extended entities", "", "")
		try:
			extended_entities = tweet['extended_entities']
			self.search_video_info(extended_entities, debug_scope)
		except KeyError:
			self.search_extended_tweet(tweet, debug_scope)
		except Exception as e:
			print("caught unknown exception !!")
			print(e)

	# If tweet was longer than 140 charchters then information is stored in extended tweet
	def search_extended_tweet(self, tweet, debug_scope):
		Helper.debug(debug_scope, "Searching extended tweet", "", "")
		try:
			extended_tweet = tweet['extended_tweet']
			self.search_extended_entities(extended_tweet, debug_scope)
		except KeyError:
			self.search_retweeted_status(tweet, debug_scope)
		except Exception as e:
			print("caught unknown exception !!")
			print(e)

	# If it was a retweet, then entities will be stored in retweeted status
	def search_retweeted_status(self, tweet, debug_scope):
		Helper.debug(debug_scope, "Searching retweeted status", "", "")
		try:
			retweeted_status = tweet['retweeted_status']
			self.search_extended_entities(retweeted_status, debug_scope)
		except KeyError:
			print("Loop exhausted. Could not find video url.")
		except Exception as e:
			print("caught unknown exception !!")
			print(e)

	# Parse entities to search video media type and fetch video info
	def search_video_info(self, entities, debug_scope):
		Helper.debug(debug_scope, "Searching video info", "", "")
		for media in entities['media']:
			try:
				if media['type'] == "video":
					self.media_id = media['id_str']
					video_info = media['video_info']
					self.video_url = self.fetch_video_url(video_info, debug_scope)
					self.mpeg_url = self.fetch_mpeg_url(video_info, debug_scope)
					self.tweet_url = media['url']
			except KeyError:
				continue
			except Exception as e:
				print("caught unknown exception !!")
				print(e)

	# Return video url from video  info
	def fetch_video_url(self, video_info, debug_scope):
		Helper.debug(debug_scope, "Fetching video url", "", "")
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
		except KeyError as e:
			print(e, " key not found in video_info")
			return None
		except Exception as e:
			print("caught unknown exception !!")
			print(e)
			return None

	# Return mpeg url from video  info
	def fetch_mpeg_url(self, video_info, debug_scope):
		Helper.debug(debug_scope, "Fetching mpeg url", "", "")
		mpeg_url = ""
		try:
			variants = video_info['variants']
			for variant in variants:
				if variant['content_type'] == "application/x-mpegURL":
					mpeg_url = variant['url']
			return mpeg_url
		except KeyError as e:
			print(e, " key not found in video_info")
			return None
		except Exception as e:
			print("caught unknown exception !!")
			print(e)
			return None

class TweetParser:

	def __init__(self, results, debug_scope):
		self.results = results
		self.debug_scope = debug_scope		

	# Collect data for each tweet
	def store_tweet_data(self):	
		tweets = []	
		for tweet_data in self.results:
			tweet_id = tweet_data['id_str']
			tweet = Tweet(tweet_id)
			tweet.search_extended_entities(tweet_data, self.debug_scope)
			if (tweet.tweet_id != None) and (tweet.tweet_url != None) and (tweet.media_id != None) and (tweet.video_url != None) and (tweet.mpeg_url != None):
				tweets.append(tweet.as_dict())
			else:
				print("Skipping tweet ID: ", tweet_id)   # to-do: change to info log
		
		old_df = pd.read_csv(TWEETS_FILE_PATH, index_col=0)
		print(old_df) # to-do: change to debug log
		new_df = pd.DataFrame(tweets)
		print(new_df) # to-do: change to debug log
		new_df = old_df.append(new_df, ignore_index=True)
		new_df.to_csv(TWEETS_FILE_PATH)
		