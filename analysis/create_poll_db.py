import numpy as np
import pandas as pd
import mysql.connector

historical_primary_polls = pd.read_csv('raw_data/FED_polls_primary.csv')
ghost_tweets = pd.concat([pd.read_csv('raw_data/poll_database.csv'),
                          pd.read_csv('raw_data/poll_database_2.csv')], axis=0)\
    .drop_duplicates().reset_index()

insert_query = '''
insert into polls values ({}, \'{}\', \'{}\', \'{}\', \'{}\', {}, \'{}\', \'{}\', {}, {}, \'{}\', {});
'''

cnx = mysql.connector.connect(user='root', password='password',
                              host='localhost',
                              database='emma')

historical_parties = historical_primary_polls.columns[2:]
historical_primary_polls['PollMedianDate'] = pd.to_datetime(historical_primary_polls['PollMedianDate'])
for i in range(0, len(historical_primary_polls)):
    for party in historical_parties:
        if not np.isnan(historical_primary_polls[party].iloc[i]):
            this_insert_query = insert_query.format(i,
                                                    historical_primary_polls['Pollster'].iloc[i],
                                                    historical_primary_polls['PollMedianDate'].iloc[i],
                                                    historical_primary_polls['PollMedianDate'].iloc[i],
                                                    historical_primary_polls['PollMedianDate'].iloc[i],
                                                    'null',
                                                    'Federal',
                                                    'AUS',
                                                    1,
                                                    0,
                                                    party,
                                                    historical_primary_polls[party].iloc[i])
            print this_insert_query
            cnx._execute_query(this_insert_query)

ghost_parties = ghost_tweets.columns[5:9]
ghost_tweets['time'] = pd.to_datetime(ghost_tweets['time'])
for j in range(0, len(ghost_tweets)):
    for party in ghost_parties:
        if not np.isnan(ghost_tweets[party].iloc[j]):
            cnx._execute_query(insert_query.format(i+j,
                                                   ghost_tweets['pollster'].iloc[j],
                                                   ghost_tweets['time'].iloc[j],
                                                   ghost_tweets['time'].iloc[j],
                                                   ghost_tweets['time'].iloc[j],
                                                   'null',
                                                   'Federal',
                                                   'AUS',
                                                   int(ghost_tweets['primary'].iloc[j]),
                                                   int(not ghost_tweets['primary'].iloc[j]),
                                                   party,
                                                   ghost_tweets[party].iloc[j]))
cnx.commit()
cnx.close()