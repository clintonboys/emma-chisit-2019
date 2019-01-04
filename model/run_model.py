import pandas as pd
import datetime as dt
from seat import load_seats
from poll import load_polls
from poll_aggregator import PollAggregator
from utils import get_logger, Parties, get_swing, apply_swing

NUM_ITERATIONS = 1
DEFAULT_PREF_FLOW = {Parties.GRN: {Parties.ALP: 0.85, Parties.LIB: 0.15, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.CDM: {Parties.ALP: 0.30, Parties.LIB: 0.70, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.FFS: {Parties.ALP: 0.40, Parties.LIB: 0.60, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.ANJ: {Parties.ALP: 0.40, Parties.LIB: 0.60, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.IND: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.ONP: {Parties.ALP: 0.20, Parties.LIB: 0.80, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.OTH: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.LDM: {Parties.ALP: 0.65, Parties.LIB: 0.35, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.NXT: {Parties.ALP: 0.60, Parties.LIB: 0.40, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.ODD: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.PIR: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.ART: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.SCI: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.SOC: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.NAT: {Parties.ALP: 0.00, Parties.LIB: 1.00, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.LBA: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.CEC: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.NCP: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.DFV: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.MAT: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.SMR: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.DLR: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.SEX: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.RNE: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.CYC: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.BUL: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.JUS: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.AUF: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.SFF: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.COM: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.SUS: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.SEN: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.C21: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.COU: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.AFF: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.DLP: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00},
                     Parties.APD: {Parties.ALP: 0.50, Parties.LIB: 0.50, Parties.GRN: 0.00, Parties.NXT: 0.00}
                     }
PREVIOUS_ELECTION_RESULTS = {Parties.ALP: 34.73, Parties.LIB: 42.04, Parties.GRN: 10.23,
                             Parties.NXT: 1.85, Parties.KAP: 0.54, Parties.IND: 2.81,
                             Parties.OTH: 7.79}
DEFAULT_POLL_RESULTS = {Parties.ALP: 0.45, Parties.LIB: 0.45, Parties.GRN: 0.10}
DEFAULT_WEIGHTS = {'Essential Research (two-week)': 1, 'Newspoll': 1, 'Ipsos': 1,
                   'YouGov/Fifty Acres': 1, 'ReachTEL': 1, 'Essential Research': 1}
SEATS_CONFIG = '/Users/clinton/Documents/dev/emma-chisit-2019/data/seats-2019.json'
POLL_DATABASE = '/Users/clinton/Documents/dev/emma-chisit-2019/data/poll_bludger_national.csv'


def main():
    logger = get_logger()
    polls = load_polls(POLL_DATABASE, logger)
    poll_aggregator = PollAggregator(polls, DEFAULT_WEIGHTS)
    poll_aggregate = poll_aggregator.aggregate_polls(dt.datetime.today(), 60, logger)
    overall_swing = get_swing(PREVIOUS_ELECTION_RESULTS, poll_aggregate.results)
    # fundamentals_index = utils.load_fundamentals_index()
    # additional_features = fundamentals_index
    seats = load_seats(SEATS_CONFIG, logger)
    i = 0
    while i < NUM_ITERATIONS:
        results_dict = {'seat': [], 'winner': [], 'coa_tpp': []}
        for seat in seats:
            logger.debug('Result last election: {}'.format(seat.last_result))
            seat.runoff(apply_swing(seat.last_result, overall_swing), DEFAULT_PREF_FLOW)
            results_dict['seat'].append(seat.name)
            results_dict['winner'].append(seat.winner.name)
            results_dict['tpp'].append(seat.winning_margin)
        i += 1
        results = pd.DataFrame.from_dict(results_dict)
        results.to_csv('/Users/clinton/Documents/dev/emma-chisit-2019/data/iteration{}.csv'.format(i))


if __name__ == '__main__':
    main()
