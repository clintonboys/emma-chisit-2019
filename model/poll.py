import numpy as np
import pandas as pd
from utils import Parties


def load_polls(poll_database):
    poll_data = pd.read_csv(poll_database)
    others_cols = [col for col in poll_data.columns if 'oth_' in col]
    poll_data['start_date'] = pd.to_datetime(poll_data['start_date'])
    poll_data['end_date'] = pd.to_datetime(poll_data['end_date'])
    poll_data['median_date'] = poll_data['start_date'] + (poll_data['end_date'] - poll_data['start_date'])/2
    polls = []
    for index, row in poll_data.iterrows():
        poll_pollster = row['pollster']
        poll_scope = row['scope']
        poll_median_date = row['median_date']
        poll_sample_size = int(row['sample'])
        poll_lnp = row['lnp']
        poll_alp = row['alp']
        poll_results = {Parties.ALP: poll_alp, Parties.LIB: poll_lnp}
        poll_others_results = {Parties(col.split('_')[1]): row[col] for col in others_cols if row[col] != np.nan}
        poll_results.update(poll_others_results)
        poll_results[Parties.OTH] = 100 - sum(poll_results.values())
        poll_others_list = poll_others_results.keys()
        poll_tpp_coa = row['lnp2pp']
        poll_tpp_alp = row['alp2pp']
        # if row['lnp2pp'] != np.nan:
        #     assert poll_tpp_alp == 100 - poll_tpp_coa, 'TPP does not sum to 100 (sum {})'.format(poll_tpp_alp + poll_tpp_coa)
        poll_tpp = {Parties.ALP: poll_tpp_alp, Parties.LIB: poll_tpp_coa}
        polls.append(Poll(poll_pollster, poll_scope, poll_median_date, poll_sample_size, 
                          poll_results, poll_tpp, poll_others_list))
    return polls


class Poll(object):
    def __init__(self, pollster, scope, median_date, sample_size, results, tpp=None, others=[]):
        self.pollster = pollster
        self.scope = scope
        self.median_date = median_date
        self.sample_size = sample_size
        self.results = results
        self.tpp = tpp
        self.others = others

