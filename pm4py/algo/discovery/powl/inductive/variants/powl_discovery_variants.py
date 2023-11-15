from enum import Enum, auto

class POWLDiscoveryVariant(Enum):
    IM_BASE = auto()  # this is base IM with no partial orders
    BRUTE_FORCE = auto()  # BPM paper
    CLUSTER = auto() # ICPM paper
