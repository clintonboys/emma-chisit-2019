import json
from enum import Enum


class Parties(Enum):
    ALP = "ALP"
    LIB = "LIB"
    GRN = "GRN"
    CDM = "CDM"
    FFS = "FFS"
    ANJ = "ANJ"
    IND = "IND"


def load_fundamentals_index():
    raise NotImplementedError()

