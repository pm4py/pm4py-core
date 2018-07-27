from pm4py.models.petri import semantics
from copy import deepcopy,copy
import time

MAX_REC_DEPTH = 10
MAX_HID_VISITED = 10

def add_missingTokens(t, net, marking, trace, traceIndex):
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
    trace
        Examined trace
    traceIndex
        Trace index
    """
    missing = 0
    tokensAdded = {}
    for a in t.in_arcs:
        if marking[a.source] < a.weight:
            #print("MARKING", [x.name for x in marking],"MISSING",a.source.name,"TRACE",[x["concept:name"] for x in trace]
            #      ,"INDEX",traceIndex,trace[traceIndex]["concept:name"])
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
    """
    Merge two dictionaries

    Parameters
    ----------
    x
        First map (string, integer)
    y
        Second map (string, integer)
    """
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

def get_placesWithMissingTokens(t, net, marking):
    """
    Get places with missing tokens

    Parameters
    ----------
    t
        Transition to enable
    net
        Petri net
    marking
        Current marking
    """
    placesWithMissing = set()
    for a in t.in_arcs:
        if marking[a.source] < a.weight:
            placesWithMissing.add(a.source)
    return placesWithMissing

def get_placesShortestPath(net, placeToPopulate, currentPlace, placesShortestPath, actualList, recDepth):
    """
    Get shortest path between places lead by hidden transitions

    Parameters
    ----------
    net
        Petri net
    placeToPopulate
        Place that we are populating the shortest map of
    currentPlace
        Current visited place (must explore its transitions)
    placesShortestPath
        Current dictionary
    actualList
        Actual list of transitions to enable
    recDepth
        Recursion depth
    """
    if recDepth > MAX_REC_DEPTH:
        return placesShortestPath
    if not placeToPopulate in placesShortestPath:
        placesShortestPath[placeToPopulate] = {}
    for t in currentPlace.out_arcs:
        if t.target.label is None:
            for p2 in t.target.out_arcs:
                if not p2.target in placesShortestPath[placeToPopulate]:
                    newActualList = copy(actualList)
                    newActualList.append(t.target)
                    placesShortestPath[placeToPopulate][p2.target] = copy(newActualList)
                    placesShortestPath = get_placesShortestPath(net, placeToPopulate, p2.target, placesShortestPath, newActualList, recDepth+1)
    return placesShortestPath

def get_placesShortestPathByHidden(net):
    """
    Get shortest path between places lead by hidden transitions

    Parameters
    ----------
    net
        Petri net
    """
    placesShortestPath = {}
    for p in net.places:
        placesShortestPath = get_placesShortestPath(net,p,p,placesShortestPath,[],0)
    return placesShortestPath

def apply_trace(trace, net, initialMarking, finalMarking, transMap, enable_placeFitness, place_fitness, placesShortestPathByHidden, consider_remaining_in_fitness):
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
    activatedHiddenTransitions = []
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
                        activatedHiddenTransitions.append(hiddenTransitions[0])
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
                            activatedHiddenTransitions.append(minTransDist[0])
                    if not executedHiddenTransitions or semantics.is_enabled(t, net, marking):
                        break
                    j = j + 1

            if not semantics.is_enabled(t, net, marking):
                placesWithMissing = get_placesWithMissingTokens(t, net, marking)
                hiddenTransitionsToEnable = []
                for p1 in marking:
                    for p2 in placesWithMissing:
                        if p2 in placesShortestPathByHidden[p1]:
                            hiddenTransitionsToEnable.append(placesShortestPathByHidden[p1][p2])

                if hiddenTransitionsToEnable:
                    somethingChanged = True
                    jIndexes = [0 for x in hiddenTransitionsToEnable]
                    z = 0
                    while somethingChanged:
                        somethingChanged = False
                        while jIndexes[z%len(hiddenTransitionsToEnable)] < len(hiddenTransitionsToEnable[z%len(hiddenTransitionsToEnable)]):
                            enabledTransitions = semantics.enabled_transitions(net, marking)
                            t3 = hiddenTransitionsToEnable[z%len(hiddenTransitionsToEnable)][jIndexes[z%len(hiddenTransitionsToEnable)]]
                            if t3 in enabledTransitions:
                                marking = semantics.execute(t3, net, marking)
                                activatedTransitions.append(t3)
                                somethingChanged = True
                            else:
                                break
                            jIndexes[z % len(hiddenTransitionsToEnable)] = jIndexes[z%len(hiddenTransitionsToEnable)] + 1
                        z = z + 1

            if not semantics.is_enabled(t, net, marking):
                [m, tokensAdded] = add_missingTokens(t, net, marking, trace, i)
                missing = missing + m
                if enable_placeFitness:
                    for place in tokensAdded.keys():
                        if place in place_fitness:
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
                    if p in place_fitness:
                        if not trace in place_fitness[p]["underfedTraces"]:
                            place_fitness[p]["overfedTraces"].add(trace)
            remaining = remaining + marking[p]
    if consider_remaining_in_fitness:
        is_fit = (missing == 0) and (remaining == 0)
    else:
        is_fit = (missing == 0)
    #print("missing=", missing)
    #print("consumed=", consumed)
    #print("produced=", produced)
    #print("remaining=", remaining)

    trace_fitness = (1.0 - float(missing)/float(consumed)) * (1.0 - float(remaining)/float(produced))

    return [is_fit, trace_fitness, activatedTransitions]

def apply_log(log, net, initialMarking, finalMarking, enable_placeFitness=False, consider_remaining_in_fitness=False):
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
    aa = time.time()
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
    bb = time.time()
    placesShortestPathByHidden = get_placesShortestPathByHidden(net)
    cc = time.time()
    print("time interlapsed: ",(cc-bb))

    firstOccVariantTrace = {}
    firstOccVariantIndex = {}
    tFitVariant = {}
    tValueVariant = {}
    actTransVariant = {}

    traceCount = 0
    for trace in log:
        traceVariant = ",".join([x["concept:name"] for x in trace])
        if not traceVariant in tFitVariant.keys():
            firstOccVariantTrace[traceVariant] = trace
            firstOccVariantIndex[traceVariant] = traceCount
            tFit, tValue, actTrans = apply_trace(trace, net, initialMarking, finalMarking, transMap,
                                                           enable_placeFitness, placeFitnessPerTrace,
                                                           placesShortestPathByHidden, consider_remaining_in_fitness)
            tFitVariant[traceVariant] = tFit
            tValueVariant[traceVariant] = tValue
            actTransVariant[traceVariant] = actTrans
            traceIsFit.append(tFit)
            traceFitnessValue.append(tValue)
            activatedTransitions.append(actTrans)
        else:
            traceIsFit.append(tFitVariant[traceVariant])
            traceFitnessValue.append(tValueVariant[traceVariant])
            activatedTransitions.append(actTransVariant[traceVariant])
            for place in placeFitnessPerTrace.keys():
                #print(placeFitnessPerTrace[place])
                if firstOccVariantTrace[traceVariant] in placeFitnessPerTrace[place]["underfedTraces"]:
                    placeFitnessPerTrace[place]["underfedTraces"].add(trace)
                if firstOccVariantTrace[traceVariant] in placeFitnessPerTrace[place]["overfedTraces"]:
                    placeFitnessPerTrace[place]["overfedTraces"].add(trace)
                #placeFitnessPerTrace[place].append(placeFitnessPerTrace[place][firstOccVariantIndex[traceVariant]])
        traceCount = traceCount + 1
        print("traceCount = "+str(traceCount)+" out of "+str(len(log)))

    dd = time.time()
    print("overall time interlapsed: ", (dd - aa))

    return [traceIsFit, traceFitnessValue, activatedTransitions, placeFitnessPerTrace]