from enum import Enum
from typing import Any, Dict, Optional, Set

import pm4py
from pm4py.algo.discovery.minimum_self_distance import algorithm as msd_algo
from pm4py.objects.log.log import EventLog
from pm4py.util import constants, exec_utils, xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


def derive_msd_witnesses(log: EventLog, msd: Optional[Dict[str, int]] = None,
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Set[str]]:
    '''
    This function derives the minimum self distance witnesses.
    The self distance of a in <a> is infinity, of a in <a,a> is 0, in <a,b,a> is 1, etc.
    The minimum self distance is the minimal observed self distance value in the event log.
    A 'witness' is an activity that witnesses the minimum self distance.
    For example, if the minimum self distance of activity a in some log L is 2, then,
    if trace <a,b,c,a> is in log L, b and c are a witness of a.

    Parameters
    ----------
    log
        Event Log to use
    msd
        Optional minimum self distance dictionary
    parameters
        Optional parameters dictionary

    Returns
    -------
    Dictionary mapping each activity to a set of witnesses.

    '''
    log = pm4py.convert_to_event_log(log)
    act_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                         xes_constants.DEFAULT_NAME_KEY)
    alphabet = pm4py.get_attribute_values(log, act_key)
    msd = msd if msd is not None else msd_algo.apply(log, parameters)
    log = list(map(lambda t: list(map(lambda e: e[act_key], t)), log))
    witnesses = dict()
    for a in alphabet:
        if a in msd and msd[a] > 0:
            witnesses[a] = set()
        else:
            continue
        for t in log:
            if len(list(filter(lambda e: e == a, t))) > 1:
                indices = [i for i, x in enumerate(t) if x == a]
                for i in range(len(indices) - 1):
                    if indices[i + 1] - indices[i] - 1 == msd[a]:
                        for b in t[indices[i] + 1:indices[i + 1]]:
                            witnesses[a].add(b)
    return witnesses
