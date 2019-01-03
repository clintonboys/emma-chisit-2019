import utils
import pandas as pd
import logging
import datetime as dt
from seat import load_seats
from utils import Parties
from poll import load_polls
from poll_aggregator import PollAggregator

NUM_ITERATIONS = 1
SEATS_CONFIG = '/Users/clinton/Documents/dev/emma-chisit-2019/data/seats-2019.json'
POLL_DATABASE = '/Users/clinton/Documents/dev/emma-chisit-2019/data/poll_bludger_national.csv'
DEFAULT_PREF_FLOW = {Parties.GRN: {Parties.ALP: 0.85, Parties.LIB: 0.15},
                     Parties.CDM: {Parties.ALP: 0.3, Parties.LIB: 0.7},
                     Parties.FFS: {Parties.ALP: 0.4, Parties.LIB: 0.6},
                     Parties.ANJ: {Parties.ALP: 0.4, Parties.LIB: 0.6},
                     Parties.IND: {Parties.ALP: 0.5, Parties.LIB: 0.5}
                     }
DEFAULT_WEIGHTS = {'Essential Research (two-week)': 1, 'Newspoll': 1, 'Ipsos': 1, 'YouGov/Fifty Acres': 1, 'ReachTEL': 1, 'Essential Research': 1}

def main():
    logger = logging.getLogger('emma-chisit-2019')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)
    polls = load_polls(POLL_DATABASE)
    poll_aggregator = PollAggregator(polls, DEFAULT_WEIGHTS)
    poll_aggregate = poll_aggregator.aggregate_polls(dt.datetime.today(), 30)#{Parties.ALP: 0.45, Parties.LIB: 0.45, Parties.GRN: 0.10} 
    # fundamentals_index = utils.load_fundamentals_index()
    # additional_features = fundamentals_index
    seats = load_seats(SEATS_CONFIG, logger)
    results_dicts = []
    i = 0
    while i < NUM_ITERATIONS:
        results_dict = {'seat': [], 'winner': []}
        for seat in seats:
            seat.runoff(poll_aggregate.results, DEFAULT_PREF_FLOW)#seat.last_result["primary"], DEFAULT_PREF_FLOW)
            results_dict['seat'].append(seat.name)
            results_dict['winner'].append(seat.winner.name)
        i += 1
        results = pd.DataFrame.from_dict(results_dict)
        results.to_csv('/Users/clinton/Documents/dev/emma-chisit-2019/data/iteration{}.csv'.format(i))


if __name__ == '__main__':
    main()
