#!/usr/bin/env python

import pandas as pd
import CustomLogger

logger = CustomLogger.getCustomLogger()
TWEETS_FILE_PATH = '../Data/Tweets.csv'


def remove_duplicate_tweets():
    df = pd.read_csv(TWEETS_FILE_PATH, index_col=0)
    num_rows = len(df)

    # Drop rows with same media ID
    df.drop_duplicates(subset='MediaID', inplace=True)
    logger.info("Dropped %s media ID duplicates", (num_rows-len(df)))
    num_rows = len(df)

    # Drop rows with same tweet URL
    df.drop_duplicates(subset='TweetURL', inplace=True)
    logger.info("Dropped %s tweet URL duplicates", (num_rows-len(df)))

	# Sequential re-indexing to accommodate deleted rows
    df = df.reset_index(drop=True)
    df.to_csv(TWEETS_FILE_PATH)


remove_duplicate_tweets()
