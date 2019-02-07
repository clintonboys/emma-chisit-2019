from twitter import *
from keys import keys
import time
import numpy as np
import pandas as pd
import os
import logging
import mysql.connector

GHOST_NAME = "GhostWhoVotes"
ACCESS_TOKEN = keys['access_token']
CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN_SECRET = keys['access_token_secret']


def get_latest_tweet():
    cnx = mysql.connector.connect(user='root', password='password',
                                  host='localhost',
                                  database='emma')
    cursor = cnx.cursor()
    latest_tweet_query = 'select max(id) as id from emma.tweets;'
    cursor.execute(latest_tweet_query)
    latest_tweet_id = [row for row in cursor][0][0]
    return latest_tweet_id


def ordinal_string(n):
    if len(str(n)) == 1:
        if n == 1:
            return '1st'
        elif n == 2:
            return '2nd'
        elif n == 3:
            return '3rd'
        else:
            return str(n) + 'th'
    else:
        if str(n)[-1] == '1' and str(n)[-2] != '1':
            return str(n) + 'st'
        elif str(n)[-1] == '2' and str(n)[-2] != '1':
            return str(n) + 'nd'
        elif str(n)[-1] == '3' and str(n)[-2] != '1':
            return str(n) + 'rd'
        else:
            return str(n) + 'th'


class GhostScraper(object):
    def __init__(self, latest_tweet, logger):
        self._latest_tweet = latest_tweet
        self._max_id = latest_tweet + 99999999999999999
        self.logger = logger
        self.tweets = []

    def scrape_ghost(self, access_token, consumer_key, consumer_secret, access_token_secret):
        start_time = time.time()
        twitter = Twitter(auth=OAuth(access_token, access_token_secret, consumer_key, consumer_secret))
        tweets_remaining = True
        n = 1
        while tweets_remaining:
            self.logger.info('Now scraping ' + ordinal_string(n) + ' page ' +
                              str(np.round(time.time() - start_time, 3)) + ' seconds elapsed...')
            results = twitter.statuses.user_timeline(screen_name=GHOST_NAME,
                                                     since_id=self._latest_tweet,
                                                     count=10)
            print results
            try:
                self._max_id = results[-1]["id"]
            except IndexError:
                tweets_remaining = False
                pass
            for status in results:
                try:
                    self.tweets.append({'id': status["id"],
                                        'text': str(status["text"]).encode('utf-8')
                                            .replace(',', '').replace('\n', '').replace('\t', ''),
                                        'created_at': status["created_at"]})
                except UnicodeEncodeError:
                    pass
            length = len(results)
            if length < 2:
                tweets_remaining = False
            n += 1

    def write_tweets(self):
        cnx = mysql.connector.connect(user='root', password='password',
                                      host='localhost',
                                      database='emma')
        cursor = cnx.cursor()
        for tweet in self.tweets:
            insert_query = '''insert into emma.tweets values({id}, \'{text}\', \'{created_at}\')'''.format(**tweet)
            cursor.execute(insert_query)
        cnx.commit()
        cnx.close()

def main():
    logger = logging.getLogger('emma-chisit-2019')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    latest_tweet = get_latest_tweet()
    scraper = GhostScraper(latest_tweet, logger)
    scraper.scrape_ghost(ACCESS_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_SECRET)
    scraper.write_tweets()


if __name__ == '__main__':
    main()
