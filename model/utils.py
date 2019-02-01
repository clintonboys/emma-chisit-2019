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
    HMP = "HMP"
    IND = "IND"
    IND1 = "IND1"
    IND2 = "IND2"
    IND3 = "IND3"
    IND4 = "IND4"
    IND5 = "IND5"
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
    OUT = "OUT"
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


class RunoffType(Enum):
    ALP_LIB = "ALP_LIB"
    ALP_NAT = "ALP_NAT"
    ALP_GRN = "ALP_GRN"
    ALP_IND = "ALP_IND"
    LIB_IND = "LIB_IND"
    LIB_GRN = "LIB_GRN"
    NAT_IND = "NAT_IND"
    LIB_NXT = "LIB_NXT"
    ALP_NXT = "ALP_NXT"
    LIB_NAT = "LIB_NAT"
    LIB_KAP = "LIB_KAP"
    LIB_ONP = "LIB_ONP"


def load_fundamentals_index():
    raise NotImplementedError()


def get_logger():
    logger = logging.getLogger('emma-chisit-2019')
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    return logger


def get_swing(first_poll, second_poll, logger):
    swing_dict = {}
    for party, votes in second_poll.iteritems():
        if party in first_poll.keys():
            swing_dict[party] = votes - first_poll[party]
        else:
            swing_dict[party] = votes
    logger.info('Computed swing as: {}'.format(swing_dict))
    return swing_dict


def apply_swing(poll, swing):
    swing_applied = {}
    for party, votes in poll.iteritems():
        if party in swing.keys():
            swing_applied[party] = votes + swing[party]
        else:
            swing_applied[party] = votes
    reweight = sum(swing_applied.values())
    for key, value in swing_applied.iteritems():
        swing_applied[key] = value * 100.0/reweight
    # remainder = 100 - sum(swing_applied.values())
    # if Parties.OTH in swing_applied.keys():
    #     swing_applied[Parties.OTH] += remainder
    # else:
    #     swing_applied[Parties.OTH] = remainder
    return swing_applied


def load_pref_flows(pref_flows_filename):
    with open(pref_flows_filename) as f:
        pref_flows_data = json.load(f)
    pref_flows_dict = {}
    for runoff_type in pref_flows_data:
        pref_flows_dict[runoff_type["runoff_type"]] = runoff_type["pref_flow"]
        for party in Parties:
            if party.name not in runoff_type["pref_flow"]:
                pref_flows_dict[runoff_type["runoff_type"]][party.name] = runoff_type["default_pref_flow"]
    return pref_flows_dict
