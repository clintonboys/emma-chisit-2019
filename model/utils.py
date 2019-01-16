import json
import logging
from enum import Enum


class Parties(Enum):
    AFF = "AFF"
    ALP = "ALP"
    ANJ = "ANJ"
    APD = "APD"
    ART = "ART"
    AUF = "AUF"
    BUL = "BUL"
    C21 = "C21"
    CDM = "CDM"
    CEC = "CEC"
    CHR = "CHR"
    COM = "COM"
    CON = "CON"
    COU = "COU"
    CYC = "CYC"
    DFV = "DFV"
    DLP = "DLP"
    DLR = "DLR"
    FFS = "FFS"
    GLZ = "GLZ"
    GRN = "GRN"
    IND = "IND"
    JUS = "JUS"
    KAP = "KAP"
    LBA = "LBA"
    LDM = "LDM"
    LIB = "LIB"
    MAR = "MAR"
    MAT = "MAT"
    NAT = "NAT"
    NCP = "NCP"
    NXT = "NXT"
    ODD = "ODD"
    ONP = "ONP"
    OTH = "OTH"
    PIR = "PIR"
    PRO = "PRO"
    PUP = "PUP"
    RFS = "RFS"
    RNE = "RNE"
    RUA = "RUA"
    SCI = "SCI"
    SEX = "SEX"
    SEN = "SEN"
    SFF = "SFF"
    SMR = "SMR"
    SOC = "SOC"
    SOE = "SOE"
    SUS = "SUS"
    VOL = "VOL"


def load_fundamentals_index():
    raise NotImplementedError()


def get_logger():
    logger = logging.getLogger('emma-chisit-2019')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    return logger


def get_swing(first_poll, second_poll):
    swing_dict = {}
    for party, votes in second_poll.iteritems():
        if party in first_poll.keys():
            swing_dict[party] = votes - first_poll[party]
        else:
            swing_dict[party] = votes
    return swing_dict


def apply_swing(poll, swing):
    swing_applied = {}
    for party, votes in poll.iteritems():
        if party in swing.keys():
            swing_applied[party] = votes + swing[party]
        else:
            swing_applied[party] = votes
    remainder = 100 - sum(swing_applied.values())
    if Parties.OTH in swing_applied.keys():
        swing_applied[Parties.OTH] += remainder
    else:
        swing_applied[Parties.OTH] = remainder
    return swing_applied
