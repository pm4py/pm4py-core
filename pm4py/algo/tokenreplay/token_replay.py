from pm4py.models.petri import semantics
from copy import deepcopy,copy

MAX_REC_DEPTH = 6
MAX_HID_VISITED = 6

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
    tokensAdded = {}
    for a in t.in_arcs:
        if marking[a.source] < a.weight:
            missing = missing + (a.weight - marking[a.source])
            marking[a.source] = marking[a.source] + a.weight
            tokensAdded[a.source] = a.weight - marking[a.source]
    return [missing, tokensAdded]

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

def merge_dicts(x, y):
    for key in y:
        if not key in x:
            x[key] = y[key]
        else:
            if y[key] < x[key]:
                x[key] = y[key]

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
    reachTrans = {}
    if recDepth > MAX_REC_DEPTH:
        return reachTrans
    for a1 in t.out_arcs:
        place = a1.target
        for a2 in place.out_arcs:
            t2 = a2.target
            if t2.label is not None:
                reachTrans[t2.label] = recDepth
            if t2.label is None:
                merge_dicts(reachTrans, get_hiddenTrans_ReachTrans(t2, net, recDepth + 1))
    return reachTrans

def apply_trace(trace, net, initialMarking, finalMarking, transMap, enable_placeFitness, place_fitness):
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
    enable_placeFitness
        Enable fitness calculation at place level
    """
    is_fit = False
    trace_fitness = 0.0
    activatedTransitions = []
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

            if len(hiddenTransitions) >= 1:
                j = 0
                while j < MAX_HID_VISITED:
                    enabledSomeHiddenTransition = False
                    enabledTransitions = semantics.enabled_transitions(net, marking)
                    hiddenTransitions = [x for x in enabledTransitions if x.label is None]
                    executedHiddenTransitions = 0
                    reachTransFromHiddenTrans = 0
                    hiddenTransDist = 0
                    executedHiddenTransitions = []
                    reachTransFromHiddenTrans = []
                    hiddenTransDist = {}

                    if len(hiddenTransitions) == 1:
                        marking = semantics.execute(hiddenTransitions[0], net, marking)
                        executedHiddenTransitions.append(hiddenTransitions[0])
                        activatedTransitions.append(hiddenTransitions[0])
                        break
                    else:
                        for t2 in hiddenTransitions:
                            reachTransDict = get_hiddenTrans_ReachTrans(t2, net, 0)
                            reachTrans = list(reachTransDict.keys())
                            reachTransFromHiddenTrans.append(reachTrans)
                            if t.label in reachTrans:
                                hiddenTransDist[t2] = reachTransDict[t.label]
                        if len(hiddenTransDist.keys()) > 0:
                            minTransDist = min(hiddenTransDist.items(), key=lambda x: x[1])
                            marking = semantics.execute(minTransDist[0], net, marking)
                            executedHiddenTransitions.append(minTransDist[0])
                            activatedTransitions.append(minTransDist[0])
                    if not executedHiddenTransitions or semantics.is_enabled(t, net, marking):
                        break
                    j = j + 1
            if not semantics.is_enabled(t, net, marking):
                semantics.detail_is_enabled(t, net, marking)
                [m, tokensAdded] = add_missingTokens(t, net, marking)
                missing = missing + m
                if enable_placeFitness:
                    for place in tokensAdded.keys():
                        place_fitness[place]["underfedTraces"].add(trace)
            else:
                m = 0
        c = get_consumedTokens(t, net)
        p = get_producedTokens(t, net)
        consumed = consumed + c
        produced = produced + p
        activatedTransitions.append(t)
        marking = semantics.execute(t, net, marking)
        i = i + 1
    remaining = 0
    for p in marking:
        if p in finalMarking:
            marking[p] = max(0, marking[p] - finalMarking[p])
            if enable_placeFitness:
                if marking[p] > 0:
                    if not trace in place_fitness[place]["underfedTraces"]:
                        place_fitness[place]["overfedTraces"].add(trace)
            remaining = remaining + marking[p]
    is_fit = (missing == 0)
    #print("missing=", missing)
    #print("consumed=", consumed)
    #print("produced=", produced)
    #print("remaining=", remaining)

    trace_fitness = (1.0 - float(missing)/float(consumed)) * (1.0 - float(remaining)/float(produced))

    return [is_fit, trace_fitness, activatedTransitions, place_fitness]

def apply_log(log, net, initialMarking, finalMarking, enable_placeFitness=False):
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
    enable_placeFitness
        Enable fitness calculation at place level
    """
    traceIsFit = []
    traceFitnessValue = []
    activatedTransitions = []
    placeFitnessPerTrace = {}
    if enable_placeFitness:
        for place in net.places:
            placeFitnessPerTrace[place] = {"underfedTraces": set(), "overfedTraces": set()}
    transMap = {}
    for t in net.transitions:
        transMap[t.label] = t
    traceCount = 0
    for trace in log:
        tFit, tValue, actTrans, pFitness = apply_trace(trace, net, initialMarking, finalMarking, transMap, enable_placeFitness, placeFitnessPerTrace)
        traceIsFit.append(tFit)
        traceFitnessValue.append(tValue)
        activatedTransitions.append(actTrans)
        traceCount = traceCount + 1
        #print("traceCount = "+str(traceCount)+" out of "+str(len(log)))

    return [traceIsFit, traceFitnessValue, activatedTransitions, placeFitnessPerTrace]