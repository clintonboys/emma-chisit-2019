import utils
import pandas as pd
import logging
from seat import load_seats
from utils import Parties
from poll_aggregator import PollAggregator

NUM_ITERATIONS = 1
SEATS_CONFIG = '/Users/clinton/Documents/dev/emma-chisit-2019/data/seats-2019.json'
DEFAULT_PREF_FLOW = {Parties.GRN: {Parties.ALP: 0.8, Parties.LIB: 0.2}}


def main():
    logger = logging.getLogger('emma-chisit-2019')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)

    # poll_aggregator = PollAggregator()
    poll_aggregate = {Parties.ALP: 0.45, Parties.LIB: 0.45, Parties.GRN: 0.10} 
    # poll_aggregator.aggregate_polls()
    # fundamentals_index = utils.load_fundamentals_index()
    # additional_features = fundamentals_index
    seats = load_seats(SEATS_CONFIG, logger)
    results_dicts = []
    i = 0
    while i < NUM_ITERATIONS:
        results_dict = {'seat': [], 'winner': []}
        for seat in seats:
            seat.runoff(poll_aggregate, DEFAULT_PREF_FLOW)
            results_dict['seat'].append(seat.name)
            results_dict['winner'].append(seat.winner.name)
        i += 1
        results = pd.DataFrame.from_dict(results_dict)
        results.to_csv('/Users/clinton/Documents/dev/emma-chisit-2019/data/iteration{}.csv'.format(i))


if __name__ == '__main__':
    main()
