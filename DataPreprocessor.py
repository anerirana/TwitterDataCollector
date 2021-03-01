#!/usr/bin/env python

import pandas as pd

TWEETS_FILE_PATH = './Data/Tweets.csv'


def remove_duplicate_tweets():
    df = pd.read_csv(TWEETS_FILE_PATH, index_col=0)
    num_rows = len(df)

    # Drop rows with same media ID
    df.drop_duplicates(subset='MediaID', inplace=True)
    print("Dropped ", (num_rows-len(df)),
          " media ID duplicates")  # to-do: log info
    num_rows = len(df)

    # Drop rows with same tweet URL
    df.drop_duplicates(subset='TweetURL', inplace=True)
    print("Dropped ", (num_rows-len(df)),
          " tweet URL duplicates")  # to-do: log info

	# Sequential re-indexing to accommodate deleted rows
    df = df.reset_index(drop=True)
    df.to_csv(TWEETS_FILE_PATH)


remove_duplicate_tweets()
