from enum import Enum, auto


class POWLDiscoveryVariant(Enum):
    TREE = auto()  # base IM with no partial orders
    BRUTE_FORCE = auto()
    MAXIMAL = auto()
    DYNAMIC_CLUSTERING = auto()
