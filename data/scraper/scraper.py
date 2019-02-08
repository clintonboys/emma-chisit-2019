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
STATES = ['vic', 'nsw', 'wa', 'sa', 'tas', 'act', 'nt', 'qld']
PARTIES = ['lib', 'nat', 'l/np', 'alp', 'grn', 'on', 'oth', 'others', 'ca', 'ind']

def get_party_vote(party, word_list, logger):
    try:
        vote = float(word_list[word_list.index(party) + 1])
        return vote
    except:
        logger.info('Parsing error: {}, {}'.format(party, word_list))
        return None


def write_poll(cursor, pollster, date, scope, scope_name, is_primary, is_tpp, party, result):
    query = 'insert into emma.polls ( pollster, start_date, end_date, median_date, sample_size,'\
            'scope, scope_name, is_primary, is_tpp, party, result) values (\'{}\', \'{}\', \'{}\','\
            '\'{}\', null, \'{}\', \'{}\', {}, {}, \'{}\', {});'.format(pollster, date, date, date, scope,
                                                                        scope_name, is_primary, is_tpp, party, result)
    cursor.execute(query)


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
        self._max_id = None
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
            if self._max_id:
                results = twitter.statuses.user_timeline(screen_name=GHOST_NAME,
                                                         since_id=self._latest_tweet,
                                                         max_id=self._max_id - 1,
                                                         count=10)
            else:
                results = twitter.statuses.user_timeline(screen_name=GHOST_NAME,
                                                         since_id=self._latest_tweet,
                                                         count=10)
            try:
                self._max_id = results[-1]["id"]
            except IndexError:
                tweets_remaining = False
                pass
            for status in results:
                try:
                    status['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.strptime(status['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))

                    self.tweets.append({'id': status["id"],
                                        'text': str(status["text"]).encode('utf-8')
                                            .replace(',', '').replace('\n', '').replace('\t', ''),
                                        'created_at': status["created_at"]})
                except UnicodeEncodeError:
                    pass
            length = len(results)
            if length == 0:
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

    @staticmethod
    def parse_tweets(tweet_list, logger):
        logger.info('Total tweets {}'.format(len(tweet_list)))
        poll_tweets = [tweet for tweet in tweet_list if tweet['text'][0] == '#']
        logger.info('Total tweets to parse {}'.format(len(poll_tweets)))
        cnx = mysql.connector.connect(user='root', password='password',
                                      host='localhost',
                                      database='emma')
        cursor = cnx.cursor()
        for tweet in poll_tweets:
            words = [x.lower() for x in tweet['text'].split(' ')[1:]]
            pollster = tweet['text'].split(' ')[0][1:]
            if any(i in STATES for i in words) and 'federal' in words and 'quarterly' not in words and ('primaries' not in words and 'primaries:' not in words):
                state = [i for i in STATES if i in words][0]
                logger.info('State {}'.format(state))
                if 'primary' in words:
                    logger.info('Parsing poll of type federal primary by state {}'.format(state))
                    is_primary, is_tpp = True, False
                elif 'party' in words and ('preferred' in words or 'preferred:' in words):
                    logger.info('Parsing poll of type federal TPP by state {}'.format(state))
                    is_primary, is_tpp = False, True
                else:
                    logger.info('Unable to determine poll type for {}'.format(words))
                    pass
                for party in PARTIES:
                    votes = get_party_vote(party, words, logger)
                    if votes:
                        logger.info('Parsed party {}: {} from tweet'.format(party, votes))
                        write_poll(cursor, pollster, tweet['created_at'], 'federal', state,
                                   is_primary, is_tpp, party, votes)
            elif 'state' in words and 'economy' not in words and 'seat' not in words:
                try:
                    state = [i for i in STATES if i in words][0]
                except:
                    logger.info('Could not find state in {}'.format(words))
                    pass
                if 'primary' in words:
                    logger.info('Parsing poll of type state primary {}'.format(state))
                    is_primary, is_tpp = True, False
                elif 'party' in words and 'party' in words and 'preferred' in words:
                    logger.info('Parsing poll of type state TPP {}'.format(state))
                    is_primary, is_tpp = False, True
                else:
                    logger.info('Unable to determine poll type for {}'.format(words))
                    pass
                for party in PARTIES:
                    votes = get_party_vote(party, words, logger)
                    if votes:
                        logger.info('Parsed party {}: {} from tweet'.format(party, votes))
                        write_poll(cursor, pollster, tweet['created_at'], 'federal', state,
                                   is_primary, is_tpp, party, votes)
            elif 'federal' in words and 'seat' not in words:
                if 'primary' in words:
                    is_primary, is_tpp = True, False
                    logger.info('Parsing poll of type federal primary')
                elif 'party' in words and 'preferred' in words:
                    logger.info('Parsing poll of type federal TPP')
                    is_primary, is_tpp = False, True
                else:
                    logger.info('Unable to determine poll type for {}'.format(words))
                    pass
                for party in PARTIES:
                    votes = get_party_vote(party, words, logger)
                    if votes:
                        logger.info('Parsed party {}: {} from tweet'.format(party, votes))
                        write_poll(cursor, pollster, tweet['created_at'], 'federal', 'aus',
                                   is_primary, is_tpp, party, votes)
            elif 'preferred' in words and ('pm' in words or 'pm:' in words):
                logger.info('Skipping parsing poll of type preferred PM')
            elif 'preferred' in words and ('premier' in words or 'premier:' in words):
                state = [i for i in STATES if i in words][0]
                logger.info('Skipping parsing poll of type preferred premier {}'.format(state))
            elif 'quarterly' in words:
                logger.info('Skipping parsing poll of type quarterly Newspoll')
            elif any(i in STATES for i in words) and 'seat' in words:
                state = [i for i in STATES if i in words][0]
                logger.info('Skipping parsing poll of type state marginal {}'.format(state))
            elif 'seat' in words:
                if 'primary' in words:
                    logger.info('Parsing poll of type federal marginal primary')
                    is_primary, is_tpp = True, False
                elif 'party' in words and 'preferred' in words:
                    is_primary, is_tpp = False, True
                    logger.info('Parsing poll of type federal marginal TPP')
            elif any(i in STATES for i in words) and 'approve' in words:
                state = [i for i in STATES if i in words][0]
                logger.info('Skipping parsing poll of type state approval {}'.format(state))
            elif 'approve' in words:
                logger.info('Skipping parsing poll of type federal approval')
            else:
                logger.info('Poll unsupported; text {}'.format(words))
        cnx.commit()
        cnx.close()


def main():
    logger = logging.getLogger('emma-chisit-2019')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    scraper = GhostScraper(get_latest_tweet(), logger)
    scraper.scrape_ghost(ACCESS_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_SECRET)
    scraper.write_tweets()
    scraper.parse_tweets(scraper.tweets, scraper.logger)
    # tweet_df = pd.read_csv('/Users/clinton/Documents/dev/elections/aus_model/data/ghost_who_votes/tweet_database.csv')
    # tweet_df['time'] = pd.to_datetime(tweet_df['time'])
    # tweet_list = []
    # for i in range(0,len(tweet_df)):
    #     tweet_list.append({'id': tweet_df['tweet_id'].iloc[i],
    #                        'text': str(tweet_df['tweet_text'].iloc[i]),
    #                        'created_at': tweet_df['time'].iloc[i]})
    # GhostScraper.parse_tweets(tweet_list, logger)


if __name__ == '__main__':
    main()
