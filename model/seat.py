import json
import numpy as np
from utils import Parties


def load_seats(seats_config_file, logger):
    seats = []
    with open(seats_config_file) as f:
        seats_data = json.load(f)
        for seat in seats_data:
            seat_name = seat['name']
            seat_state = seat['state']
            seat_features = {"electors": seat["electors"],
                             "type": seat["type"]}
            seat_held_by = seat["held_by"]
            seat_candidates = seat["candidates"]
            seat_last_result = seat["last_result"]
            this_seat = Seat(seat_name, seat_state, seat_features, seat_held_by,
                             seat_candidates, seat_last_result, logger)
            seats.append(this_seat)
            logger.info('Loaded seat {} into memory'.format(seat_name))
    return seats


class Seat(object):
    def __init__(self, name, state, features, held_by, candidates, last_result, logger):
        self.name = name
        self.state = state
        self.features = features
        self.held_by = held_by
        self.candidates = candidates
        self.last_result = last_result
        self.logger = logger
        self.winner = None

    def runoff(self, primary_results, pref_flows):
        """
        While there are more than two candidates remaining, we take the candidate
         with the fewest votes and eliminate them from the count, distributing their
         votes among the remaining candidates according to the preference flow data.
        :param primary_results: A dictionary 
                {
                  "party1": primary_votes,
                  "party2": primary_votes,
                  ...
                 }
        :param pref_flows: A dictionary
                {
                  "party1": {
                             "party2": 0.4,
                             "party3: 0.6
                             },
                   ...
                }
        :return: A dictionary of the two-party preferred result
                {
                  "party1": 0.5,
                  "party2": 0.5
                }
        """

        total = np.sum(primary_results.values())

        try:
            del primary_results['Informal']
        except KeyError:
            pass

        remaining_candidates = {Parties(party): vote for party, vote in primary_results.copy().iteritems()}
        round_no = 0

        while len(remaining_candidates) > 2:
            self.logger.info('Runoff for {}, round #{}. Current candidates: {}'.format(self.name,
                                                                                       round_no + 1,
                                                                                       zip(remaining_candidates.keys(),
                                                                                           remaining_candidates.values()
                                                                                           )))
            round_no = round_no + 1
            to_eliminate = min(remaining_candidates, key=remaining_candidates.get)
            votes = remaining_candidates[to_eliminate]
            del remaining_candidates[to_eliminate]
            try:
                to_dist = pref_flows[Parties(to_eliminate)]
            except KeyError:
                to_dist = {}
                for party in remaining_candidates:
                    if Parties(party) in Parties:
                        to_dist[party] = 0.4595
                    elif party == Parties.ALP:
                        to_dist[party] = 0.5405
                    else:
                        to_dist[party] = 0
            fixed_preferences = {}
            for party in remaining_candidates:
                if Parties(party) in to_dist.keys():
                    fixed_preferences[Parties(party)] = to_dist[Parties(party)]
            preference_sum = np.sum([fixed_preferences[key] for key in fixed_preferences])
            for party in fixed_preferences:
                fixed_preferences[party] = fixed_preferences[party] / preference_sum

            for party in remaining_candidates:
                if Parties(party) in to_dist:
                    remaining_candidates[Parties(party)] = np.round(remaining_candidates[Parties(party)] +
                                                                    to_dist[Parties(party)] * votes, 2)
                else:
                    if float(remaining_candidates[party]) / float(total) > 0.1:
                        raise KeyError('Runoff Error: Missing preference data for important contest: {}'.format(party))
        self.logger.info('Runoff for {} complete. Final results: {}'.format(self.name, zip(remaining_candidates.keys(),
                                                                                           remaining_candidates.values())))
        self.winner = max(remaining_candidates, key=remaining_candidates.get)
        return remaining_candidates
