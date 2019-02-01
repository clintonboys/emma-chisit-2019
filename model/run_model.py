import pandas as pd
import datetime as dt
from seat import load_seats
from poll import load_polls
from poll_aggregator import PollAggregator
from utils import get_logger, Parties, get_swing, apply_swing, load_pref_flows


NUM_ITERATIONS = 1
PREVIOUS_ELECTION_RESULTS = {Parties.ALP: 34.73, Parties.LIB: 42.04, Parties.GRN: 10.23,
                             Parties.NXT: 1.85, Parties.KAP: 0.54, Parties.IND: 2.81,
                             Parties.OTH: 7.79}
DEFAULT_POLL_RESULTS = {Parties.ALP: 0.45, Parties.LIB: 0.45, Parties.GRN: 0.10}
DEFAULT_WEIGHTS = {'Essential Research (two-week)': 1, 'Newspoll': 1, 'Ipsos': 1,
                   'YouGov/Fifty Acres': 1, 'ReachTEL': 1, 'Essential Research': 1}
SEATS_CONFIG = '/Users/clinton/Documents/dev/emma-chisit-2019/data/seats-2019.json'
PREF_FLOW_CONFIG = '/Users/clinton/Documents/dev/emma-chisit-2019/data/pref_flows.json'
POLL_DATABASE = '/Users/clinton/Documents/dev/emma-chisit-2019/data/poll_bludger_national.csv'


def main():
    logger = get_logger()
    polls = load_polls(POLL_DATABASE, logger)
    poll_aggregator = PollAggregator(polls, DEFAULT_WEIGHTS)
    pref_flows = load_pref_flows(PREF_FLOW_CONFIG)
    poll_aggregate = poll_aggregator.aggregate_polls(dt.datetime.today(), 60, logger)
    overall_swing = get_swing(PREVIOUS_ELECTION_RESULTS, poll_aggregate.results, logger)
    # fundamentals_index = utils.load_fundamentals_index()
    # additional_features = fundamentals_index
    seats = load_seats(SEATS_CONFIG, logger)
    i = 0
    while i < NUM_ITERATIONS:
        results_dict = {'seat': [], 'winner': [], 'tpp': [], 'loser': [], 'losing_margin': []}
        for seat in [seat for seat in seats]:# if seat.name == 'Cowper']:
            logger.debug('Result last election: {}'.format(seat.last_result))
            seat.runoff(apply_swing(seat.last_result, overall_swing), pref_flows)
            results_dict['seat'].append(seat.name)
            results_dict['winner'].append(seat.winner.name)
            results_dict['tpp'].append(seat.winning_margin)
            results_dict['loser'].append(seat.loser.name)
            results_dict['losing_margin'].append(seat.losing_margin)
        i += 1
        results = pd.DataFrame.from_dict(results_dict)
        results.to_csv('/Users/clinton/Documents/dev/emma-chisit-2019/data/iteration{}.csv'.format(i))
        print results.groupby('winner').agg('count')


if __name__ == '__main__':
    main()
