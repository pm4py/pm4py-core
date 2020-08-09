from pm4py.algo.discovery.correlation_mining.versions import classic_split, classic, trace_based
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    CLASSIC_SPLIT = classic_split
    CLASSIC = classic
    TRACE_BASED = trace_based


DEFAULT_VARIANT = Variants.CLASSIC


def apply(log, variant=DEFAULT_VARIANT, parameters=None):
    """
    Applies the Correlation Miner to the event stream (a log is converted to a stream)

    The approach is described in:
    Pourmirza, Shaya, Remco Dijkman, and Paul Grefen. "Correlation miner: mining business process models and event
    correlations without case identifiers." International Journal of Cooperative Information Systems 26.02 (2017):
    1742002.

    Parameters
    -------------
    log
        Log object
    variant
        Variant of the algorithm to use
    parameters
        Parameters of the algorithm

    Returns
    --------------
    dfg
        Directly-follows graph
    performance_dfg
        Performance DFG (containing the estimated performance for the arcs)
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log, parameters=parameters)
