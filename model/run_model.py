import utils
import logging
from poll_aggregator import PollAggregator

NUM_ITERATIONS = 1000
SEATS_CONFIG = '/Users/clinton/Documents/dev/emma-chisit-2019/data/seats-2019.json'


def main():
    logger = logging.getLogger('emma-chisit-2019')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)

    poll_aggregator = PollAggregator()
    poll_aggregate = poll_aggregator.aggregate_polls()
    fundamentals_index = utils.load_fundamentals_index()
    additional_features = fundamentals_index
    seats = utils.load_seats(SEATS_CONFIG, logger)
    results_dicts = []
    i = 0
    while i < NUM_ITERATIONS:
        results_dict = {}
        for seat in seats:
            runoff = seat.runoff(poll_aggregate, additional_features)
            runoff.get_result()
            results_dict[seat.name] = runoff.result
            results_dicts.append(results_dict)
        i += 1


if __name__ == '__main__':
    main()
