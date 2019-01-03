import numpy as np
from poll import Poll
import datetime as dt
from utils import Parties


def exp_decay(days, n=30):
    days = getattr(days, "days", days)
    return np.round(.5 ** (float(days)/float(n)),3)


class PollAggregator(object):
    def __init__(self, polls, weights):
        self.polls = polls
        self.weights = weights

    def aggregate_polls(self, to_date, num_days):
        relevant_polls = []
        from_date = to_date - dt.timedelta(days=num_days)

        for poll in self.polls:
            if to_date >= poll.median_date >= from_date:
                relevant_polls.append(poll)

        results_list = {}

        for poll in relevant_polls:
            for party, vote in poll.results.iteritems():
                results_list[party] = np.round(
                    np.sum(
                        np.trim_zeros(np.array([self.weights[poll.pollster] for poll in relevant_polls]) *
                                      np.array([exp_decay(to_date - poll.median_date, num_days) for poll in relevant_polls]) *
                                      np.array([poll.results[party] for poll in relevant_polls])) /
                        (np.array([self.weights[poll.pollster] for poll in relevant_polls]) *
                         np.array([exp_decay(to_date - poll.median_date, num_days) for poll in relevant_polls]))[
                            np.array([self.weights[poll.pollster] for poll in relevant_polls]) *
                            np.array([exp_decay(to_date - poll.median_date, num_days) for poll in relevant_polls]) *
                            np.array([poll.results[party] for poll in relevant_polls]) > 0].sum()), 2)

        others = [party for party in results_list.keys() if party not in (Parties.ALP, Parties.LIB)]
        aggregated_poll = Poll('aggregate', 'aggregate', (to_date - from_date) / 2, 0, results_list, None, others)
        change = sum([aggregated_poll.results[party] for party in aggregated_poll.results])
        old_others = aggregated_poll.results[Parties.OTH]
        aggregated_poll.results[Parties.OTH] = old_others - change + 100
        print aggregated_poll.results
        return aggregated_poll
