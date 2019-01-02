class Seat(object):
    def __init__(self, name, state, features, held_by, candidates, last_result):
        self.name = name
        self.state = state
        self.features = features
        self.held_by = held_by
        self.candidates = candidates
        self.last_result = last_result

    def runoff(self):
        raise NotImplementedError()