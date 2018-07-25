from pm4py.models.petri import semantics
from copy import deepcopy,copy

MAX_REC_DEPTH = 100

def add_missingTokens(t, net, marking):
    """
    Adds missing tokens needed to activate a transition

    Parameters
    ----------
    t
        Transition that should be enabled
    net
        Petri net
    marking
        Current marking
    """
    missing = 0
    for a in t.in_arcs:
        if marking[a.source] < a.weight:
            missing = missing + (a.weight - marking[a.source])
            marking[a.source] = marking[a.source] + a.weight
    return missing

def get_consumedTokens(t, net):
    """
    Get tokens consumed firing a transition

    Parameters
    ----------
    t
        Transition that should be enabled
    net
        Petri net
    """
    consumed = 0
    for a in t.in_arcs:
        consumed = consumed + a.weight
    return consumed

def get_producedTokens(t, net):
    """
    Get tokens produced firing a transition

    Parameters
    ----------
    t
        Transition that should be enabled
    net
        Petri net
    """
    produced = 0
    for a in t.out_arcs:
        produced = produced + a.weight
    return produced

def get_hiddenTrans_ReachTrans(t, net, recDepth):
    """
    Get visible transitions reachable by enabling a hidden transition

    Parameters
    ----------
    t
        Transition that should be enabled
    net
        Petri net
    recDepth
        Current recursion depth
    """
    reachTrans = []
    if recDepth > MAX_REC_DEPTH:
        return reachTrans
    for a1 in t.out_arcs:
        place = a1.target
        for a2 in place.out_arcs:
            t2 = a2.target
            if t2.label is not None:
                reachTrans.append(t2.label)
    if len(reachTrans) == 0:
        for a1 in t.out_arcs:
            place = a1.target
            for a2 in place.out_arcs:
                t2 = a2.target
                if t2.label is None:
                    reachTrans = reachTrans + get_hiddenTrans_ReachTrans(t2, net, recDepth + 1)
    return reachTrans

def apply_trace(trace, net, initialMarking, finalMarking, transMap):
    """
    Apply the token replaying algorithm to a trace

    Parameters
    ----------
    trace
        Trace in the event log
    net
        Petri net
    initialMarking
        Initial marking
    finalMarking
        Final marking
    transMap
        Map between transitions labels and transitions
    """
    is_fit = False
    trace_fitness = 0.0
    marking = copy(initialMarking)
    missing = 0
    consumed = 0
    produced = 0
    remaining = 0
    i = 0
    while i < len(trace):
        t = transMap[trace[i]["concept:name"]]
        if not semantics.is_enabled(t, net, marking):
            enabledTransitions = semantics.enabled_transitions(net, marking)
            hiddenTransitions = [x for x in enabledTransitions if x.label is None]
            if len(hiddenTransitions) == 1:
                marking = semantics.execute(hiddenTransitions[0], net, marking)
            elif len(hiddenTransitions) > 1:
                for t2 in hiddenTransitions:
                    reachTrans = get_hiddenTrans_ReachTrans(t2, net, 0)
                    #print("reachTrans = ",reachTrans)
                    if t.label in reachTrans:
                        marking = semantics.execute(t2, net, marking)
                        break
            m = add_missingTokens(t, net, marking)
            missing = missing + m
        c = get_consumedTokens(t, net)
        p = get_producedTokens(t, net)
        consumed = consumed + c
        produced = produced + p

        marking = semantics.execute(t, net, marking)
        i = i + 1
    remaining = 0
    for p in marking:
        if p in finalMarking:
            marking[p] = max(0, marking[p] - finalMarking[p])
            remaining = remaining + marking[p]
    is_fit = (missing == 0)
    #print("missing=", missing)
    #print("consumed=", consumed)
    #print("produced=", produced)
    #print("remaining=", remaining)
    trace_fitness = (1.0 - float(missing)/float(consumed)) * (1.0 - float(remaining)/float(produced))

    return [is_fit, trace_fitness]

def apply_log(log, net, initialMarking, finalMarking):
    """
    Apply token-based replay to a log

    Parameters
    ----------
    log
        Trace log
    net
        Petri net
    initialMarking
        Initial marking
    finalMarking
        Final marking
    """
    traceIsFit = []
    traceFitnessValue = []
    transMap = {}
    for t in net.transitions:
        transMap[t.label] = t
    for trace in log:
        #print(trace)
        tFit, tValue = apply_trace(trace, net, initialMarking, finalMarking, transMap)
        traceIsFit.append(tFit)
        traceFitnessValue.append(tValue)

    return [traceIsFit, traceFitnessValue]