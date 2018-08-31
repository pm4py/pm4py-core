from collections import Counter
from pm4py.log.instance import TraceLog, Event, Trace
from pm4py.algo.tokenreplay.versions import token_replay

"""
Implementation of the approach described in paper

Muñoz-Gama, Jorge, and Josep Carmona. "A fresh look at precision in process conformance." International Conference on Business Process Management. Springer, Berlin, Heidelberg, 2010.

for measuring precision.

For each prefix in the log, the reflected tasks are calculated (outgoing activities from the prefix)
Then, a token replay is done on the prefix in order to get activated transitions
Escaping edges is the set difference between activated transitions and reflected tasks

Then, precision is calculated by the formula used in the paper

At the moment, the precision value is different from the one provided by the ProM plug-in,
although the implementation seems to follow the paper concept
"""
def get_log_prefixes(log, activity_key="concept:name"):
    """
    Get trace log prefixes

    Parameters
    ----------
    log
        Trace log
    activity_key
        Activity key (must be provided if different from concept:name)
    """
    prefixes = {}
    prefixCount = Counter()
    for trace in log:
        i = 1
        while i < len(trace) - 1:
            redTrace = trace[0:i]
            prefix = ",".join([x[activity_key] for x in redTrace])
            nextActivity = trace[i][activity_key]
            if not prefix in prefixes:
                prefixes[prefix] = set()
            prefixes[prefix].add(nextActivity)
            prefixCount[prefix] += 1
            i = i + 1
    return prefixes, prefixCount

def form_fake_log(prefixesKeys, prefixes, activity_key="concept:name"):
    """
    Form fake log for replay (putting each prefix as separate trace to align)

    Parameters
    ----------
    prefixesKeys
        Keys of the prefixes (to form a log with a given order)
    prefixes
        All prefixes found in the log
    activity_key
        Activity key (must be provided if different from concept:name)
    """
    fake_log = TraceLog()
    for prefix in prefixesKeys:
        trace = Trace()
        prefixActivities = prefix.split(",")
        for activity in prefixActivities:
            event = Event()
            event[activity_key] = activity
            trace.append(event)
        fake_log.append(trace)
    return fake_log

def apply(log, net, marking, final_marking, activity_key="concept:name"):
    """
    Get ET Conformance precision

    Parameters
    ----------
    log
        Trace log
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    activity_key
        Activity key
    """
    precision = 0.0
    sumEE = 0
    sumAT = 0
    prefixes, prefixCount = get_log_prefixes(log, activity_key=activity_key)
    prefixesKeys = list(prefixes.keys())
    fake_log = form_fake_log(prefixesKeys, prefixes, activity_key=activity_key)
    [traceIsFit, traceFitnessValue, activatedTransitions, placeFitness, reachedMarkings,enabledTransitionsInMarkings] = token_replay.apply_log(fake_log, net, marking, final_marking, consider_remaining_in_fitness=False, tryToReachFinalMarkingThroughHidden=False, stopImmediatelyWhenUnfit=True, useHiddenTransitionsToEnableCorrespondingTransitions=True, activity_key=activity_key)

    i = 0
    while i < len(traceIsFit):
        if traceIsFit[i]:
            logTransitions = set(prefixes[prefixesKeys[i]])
            activatedTransitionsLabels = set([x.label for x in enabledTransitionsInMarkings[i] if x.label is not None])
            sumAT += len(activatedTransitionsLabels) * prefixCount[prefixesKeys[i]]
            escapingEdges = activatedTransitionsLabels.difference(logTransitions)
            sumEE += len(escapingEdges) * prefixCount[prefixesKeys[i]]
        i = i + 1

    if sumAT > 0:
        precision = 1 - float(sumEE)/float(sumAT)

    return precision