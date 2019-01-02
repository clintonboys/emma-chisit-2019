import json
from enum import Enum
from seat import Seat


class Party(Enum):
    ALP = "ALP"
    LIB = "LIB"
    GRN = "GRN"
    CDM = "CDM"
    FFS = "FFS"
    ANJ = "ANJ"
    IND = "IND"


def load_fundamentals_index():
    raise NotImplementedError()


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
            this_seat = Seat(seat_name, seat_state, seat_features,
                             seat_held_by, seat_candidates, seat_last_result)
            seats.append(this_seat)
            logger.info('Loaded seat {} into memory'.format(seat_name))
    return seats
