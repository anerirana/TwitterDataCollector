#!/usr/bin/env python


import argparse
import requests
import json
import urllib.parse
import m3u8
from pathlib import Path
import re
import ffmpeg
import shutil
import copy
import subprocess
import pandas as pd
import CustomLogger
import time

logger = CustomLogger.getCustomLogger()
OUTPUT_DIR = '../Data/Audios'
TWEETS_FILE_PATH = '../Data/Non_Offensive_Tweets.csv'
NEW_TWEETS_FILE_PATH = '../Data/ValidTweets.csv'

class AudioDownloader:
	video_player_prefix = 'https://twitter.com/i/videos/tweet/'
	video_api = 'https://api.twitter.com/1.1/videos/tweet/config/'

	def __init__(self, mpeg_url):
		self.mpeg_url = mpeg_url

		self.media_id = self.mpeg_url.split('/')[4]

		storage_dir = Path(OUTPUT_DIR)
		Path.mkdir(storage_dir, parents=True, exist_ok=True)
		self.storage = str(storage_dir)
		self.requests = requests.Session()

	# Downloads audio files for a tweet
	# Return Type : Bool
	# returns True for successful download, otherwise returns False
	def download(self):
		logger.debug("Start: download()")
		logger.debug("Downloading Media ID %s", self.media_id)
		
		# Get the bearer token
		self.set_bearer_token()

		# Get the M3u8 file - contains streaming information
		video_host, playlist = self.get_m3u8_file()

		# Get lowest resolution video to save memory
		video_info = self.get_lowest_resolution_video(playlist)
		if video_info is None:
			return False

		video_file_name = Path(self.storage) / Path(self.media_id + '.mp4')
		video_url = video_host + video_info.uri

		ts_m3u8_response = self.requests.get(
			video_url, headers={'Authorization': None})
		ts_m3u8_parse = m3u8.loads(ts_m3u8_response.text)

		ts_list = []
		for ts_uri in ts_m3u8_parse.segments.uri:
			ts_file = requests.get(video_host + ts_uri)
			fname = ts_uri.split('/')[-1]
			ts_path = Path(self.storage) / Path(fname)
			ts_list.append(ts_path)

			ts_path.write_bytes(ts_file.content)

		ts_full_file = Path(self.storage) / Path(self.media_id + '.ts')
		ts_full_file = str(ts_full_file)

		with open(str(ts_full_file), 'wb') as wfd:
			for f in ts_list:
				with open(f, 'rb') as fd:
					shutil.copyfileobj(fd, wfd, 1024 * 1024 * 10)
		
		try:
			# Converting ts to mp4
			logger.info('[*] Converting byte stream to mp4 format ...')
			ffmpeg\
				.input(ts_full_file)\
				.output(str(video_file_name), acodec='copy', vcodec='libx264', format='mp4', loglevel='error')\
				.overwrite_output()\
				.run()

			# Converting mp4 to wav
			logger.info('[*] Converting mp4 stream to wav format ...')
			audio_file_name = Path(self.storage) / Path(self.media_id + '.wav')
			cmd = "ffmpeg -i " + str(video_file_name) + " -ab 160k -ac 2 -ar 44100 -vn " + str(audio_file_name) + " -loglevel error"
			p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
			stdout, stderr = p.communicate()
			if p.wait()!= 0:
				logger.error("Found some error")
				logger.error(stderr)
				self.clean_up(ts_list, ts_full_file, video_file_name)
				return False
				
		except Exception as e:
			logger.error("Caught Unknown Exception ", exc_info=True)
			self.clean_up(ts_list, ts_full_file, video_file_name)
			return False
		
		self.clean_up(ts_list, ts_full_file, video_file_name)
		logger.debug("End: download()")
		return True
		

	def clean_up(self, ts_list, ts_full_file, video_file_name):
		logger.info('[+] Cleaning up ...')

		for ts in ts_list:
			p = Path(ts)
			p.unlink()

		p = Path(ts_full_file)
		p.unlink()

		p = Path(video_file_name)
		p.unlink()
		

	def set_bearer_token(self):
		logger.debug("Start: set_bearer_token()")
		video_player_url = self.video_player_prefix + self.media_id
		video_player_response = self.requests.get(video_player_url).text
		logger.debug("Video Player Body")
		logger.debug(video_player_response)

		js_file_url = re.findall('src="(.*js)', video_player_response)[0]
		js_file_response = self.requests.get(js_file_url).text

		bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
		bearer_token = bearer_token_pattern.search(js_file_response)
		bearer_token = bearer_token.group(0)
		self.requests.headers.update({'Authorization': bearer_token})
		logger.debug("Bearer Token")
		logger.debug(bearer_token)
		self.set_guest_token()
		logger.debug("End: set_bearer_token()")

	def set_guest_token(self):
		logger.debug("Start: set_guest_token()")
		res = self.requests.post("https://api.twitter.com/1.1/guest/activate.json")
		res_json = json.loads(res.text)
		logger.debug("Guest Token")
		logger.debug(res_json.get('guest_token'))
		self.requests.headers.update({'x-guest-token': res_json.get('guest_token')})
		logger.debug("End: set_guest_token()")

	def get_m3u8_file(self):
		logger.debug("Start: get_m3u8_file()")
		m3u8_response = self.requests.get(self.mpeg_url)
		logger.debug("M3U8 Response: %s", m3u8_response.text)

		m3u8_url_parse = urllib.parse.urlparse(self.mpeg_url)
		video_host = m3u8_url_parse.scheme + '://' + m3u8_url_parse.hostname

		m3u8_parse = m3u8.loads(m3u8_response.text)
		logger.debug("End: get_m3u8_file()")
		return [video_host, m3u8_parse]	

	def get_lowest_resolution_video(self, playlist):
		logger.debug("Start: get_lowest_resolution_video()")
		# Arbitrary high number
		min_resolution = 99999999999
		if len(playlist.playlists) > 0:
			for instance in playlist.playlists:
				if instance.stream_info.resolution[0] < min_resolution:
					min_resolution = instance.stream_info.resolution[0]
					video_info = instance
		else:
			logger.info("Found empty playlist. Media is no longer available")
			logger.debug("End: get_lowest_resolution_video()")
			return None
		logger.debug("End: get_lowest_resolution_video()")
		return video_info

df = pd.read_csv(TWEETS_FILE_PATH, index_col=0)
num_tweets = len(df)
for url in df['MpegURL']:
	audio_dw = AudioDownloader(url)	
	# Retain tweet data only for successful downloads
	if not audio_dw.download():
		df = df[df['MpegURL']!= url]
	time.sleep(5)

# Sequential re-indexing to accommodate deleted rows
df = df.reset_index(drop=True)
logger.info("Discarded %d tweets", (num_tweets-len(df)))
df.to_csv(NEW_TWEETS_FILE_PATH)