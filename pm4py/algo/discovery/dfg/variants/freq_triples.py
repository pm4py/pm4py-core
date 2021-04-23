from collections import Counter
from enum import Enum

from pm4py.util import constants, exec_utils
from pm4py.util import xes_constants as xes_util


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def apply(log, parameters=None):
    return freq_triples(log, parameters=parameters)


def freq_triples(log, parameters=None):
    """
    Counts the number of directly follows occurrences, i.e. of the form <...a,b...>, in an event log.

    Parameters
    ----------
    log
        Trace log
    parameters
        Possible parameters passed to the algorithms:
            activity_key -> Attribute to use as activity

    Returns
    -------
    dfg
        DFG graph
    """
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY)
    dfgs = map(
        (lambda t: [(t[i - 2][activity_key], t[i - 1][activity_key], t[i][activity_key]) for i in range(2, len(t))]),
        log)
    return Counter([dfg for lista in dfgs for dfg in lista])
