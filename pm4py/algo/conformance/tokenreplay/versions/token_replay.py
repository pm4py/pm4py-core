from pm4py.entities.petri import semantics
from copy import copy
from threading import Thread
from pm4py.algo.filtering.tracelog.variants import variants_filter as variants_module
from pm4py import util as pmutil
from pm4py.entities.log.util import xes as xes_util
from pm4py.util import constants

MAX_REC_DEPTH = 50
MAX_IT_FINAL = 10
MAX_REC_DEPTH_HIDTRANSENABL = 5
MAX_POSTFIX_SUFFIX_LENGTH = 20
MAX_NO_THREADS = 1000

class NoConceptNameException(Exception):
    def __init__(self, message):
        self.message = message

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
                if not p2.target in placesShortestPath[placeToPopulate] or len(actualList)+1 < len(placesShortestPath[placeToPopulate][p2.target]):
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

def giveScoreToHiddenTransitions(hiddenTransitionsToEnable):
    """
    Gives score to hidden transitions

    Parameters
    -----------
    hiddenTransitionsToEnable
        Hidden transitions to enable
    :param hiddenTransitionsToEnable:
    :return:
    """
    scoredTransitions = []
    for group in hiddenTransitionsToEnable:
        score = 0.0
        for trans in group:
            if "tau" in trans.name:
                score = score + 1.001
            elif "skip" in trans.name:
                score = score + 1.002
            else:
                score = score + 1.003
        scoredTransitions.append([group, score])
    scoredTransitions = sorted(scoredTransitions, key=lambda x: x[1])
    return scoredTransitions

def getHiddenTransitionsToEnable(marking, placesWithMissing, placesShortestPathByHidden):
    """
    Calculate an ordered list of transitions to visit in order to enable a given transition

    Parameters
    ----------
    marking
        Current marking
    placesWithMissing
        List of places with missing tokens
    placesShortestPathByHidden
        Minimal connection between places by hidden transitions
    """
    hiddenTransitionsToEnable = []

    markingPlaces = [x for x in marking]
    markingPlaces = sorted(markingPlaces, key=lambda x: x.name)
    placesWithMissingKeys = [x for x in placesWithMissing]
    placesWithMissingKeys = sorted(placesWithMissingKeys, key=lambda x: x.name)
    for p1 in markingPlaces:
        for p2 in placesWithMissingKeys:
            if p1 in placesShortestPathByHidden and p2 in placesShortestPathByHidden[p1]:
                hiddenTransitionsToEnable.append(placesShortestPathByHidden[p1][p2])
    hiddenTransitionsToEnable = sorted(hiddenTransitionsToEnable, key=lambda x: len(x))
    #scoredTransitions = giveScoreToHiddenTransitions(hiddenTransitionsToEnable)
    #hiddenTransitionsToEnable = [x[0] for x in scoredTransitions]

    return hiddenTransitionsToEnable

def getReqTransitionsForFinalMarking(marking, finalMarking, placesShortestPathByHidden):
    """
    Gets required transitions for final marking

    Parameters
    ----------
    marking
        Current marking
    placesWithMissing
        List of places with missing tokens
    placesShortestPathByHidden
        Minimal connection between places by hidden transitions
    """
    hiddenTransitionsToEnable = []

    markingPlaces = [x for x in marking]
    markingPlaces = sorted(markingPlaces, key=lambda x: x.name)
    finalMarkingPlaces = [x for x in finalMarking]
    finalMarkingPlaces = sorted(finalMarkingPlaces, key=lambda x: x.name)
    for p1 in markingPlaces:
        for p2 in finalMarkingPlaces:
            if p1 in placesShortestPathByHidden and p2 in placesShortestPathByHidden[p1]:
                hiddenTransitionsToEnable.append(placesShortestPathByHidden[p1][p2])
    hiddenTransitionsToEnable = sorted(hiddenTransitionsToEnable, key=lambda x: len(x))
    #scoredTransitions = giveScoreToHiddenTransitions(hiddenTransitionsToEnable)
    #hiddenTransitionsToEnable = [x[0] for x in scoredTransitions]

    return hiddenTransitionsToEnable

def enableHiddenTransitions(net, marking, activatedTransitions, visitedTransitions, allVisitedMarkings, hiddenTransitionsToEnable, t):
    """
    Actually enable hidden transitions on the Petri net

    Parameters
    -----------
    net
        Petri net
    marking
        Current marking
    activatedTransitions
        All activated transitions during the replay
    visitedTransitions
        All visited transitions by the recursion
    allVisitedMarkings
        All visited markings
    hiddenTransitionsToEnable
        List of hidden transition to enable
    t
        Transition against we should check the enabledness
    """
    somethingChanged = True
    jIndexes = [0 for x in hiddenTransitionsToEnable]
    z = 0
    while somethingChanged:
        somethingChanged = False
        while jIndexes[z % len(hiddenTransitionsToEnable)] < len(
                hiddenTransitionsToEnable[z % len(hiddenTransitionsToEnable)]):
            t3 = hiddenTransitionsToEnable[z % len(hiddenTransitionsToEnable)][
                jIndexes[z % len(hiddenTransitionsToEnable)]]
            if not t3 == t:
                if semantics.is_enabled(t3, net, marking):
                    if not t3 in visitedTransitions:
                        marking = semantics.execute(t3, net, marking)
                        activatedTransitions.append(t3)
                        visitedTransitions.add(t3)
                        allVisitedMarkings.append(marking)
                        enabledTransitions = semantics.enabled_transitions(net, marking)
                        somethingChanged = True
            jIndexes[z % len(hiddenTransitionsToEnable)] = jIndexes[z % len(hiddenTransitionsToEnable)] + 1
            if semantics.is_enabled(t, net, marking):
                break
        if semantics.is_enabled(t, net, marking):
            break
        z = z + 1
    return [marking, activatedTransitions, visitedTransitions, allVisitedMarkings]

def apply_hiddenTrans(t, net, marking, placesShortestPathByHidden, activatedTransitions, recDepth, visitedTransitions, allVisitedMarkings):
    """
    Apply hidden transitions in order to enable a given transition

    Parameters
    ----------
    t
        Transition to eventually enable
    net
        Petri net
    marking
        Marking
    placesShortestPathByHidden
        Shortest paths between places connected by hidden transitions
    activatedTransitions
        All activated transitions
    recDepth
        Current recursion depth
    visitedTransitions
        All visited transitions by hiddenTrans method
    allVisitedMarkings
        All visited markings
    """
    if recDepth >= MAX_REC_DEPTH_HIDTRANSENABL or t in visitedTransitions:
        return [net, marking, activatedTransitions, allVisitedMarkings]
    visitedTransitions.add(t)
    markingAtStart = copy(marking)
    placesWithMissing = get_placesWithMissingTokens(t, net, marking)
    hiddenTransitionsToEnable = getHiddenTransitionsToEnable(marking, placesWithMissing, placesShortestPathByHidden)

    if hiddenTransitionsToEnable:
        [marking, activatedTransitions, visitedTransitions, allVisitedMarkings] = enableHiddenTransitions(net, marking, activatedTransitions, visitedTransitions, allVisitedMarkings, hiddenTransitionsToEnable, t)
        if not semantics.is_enabled(t, net, marking):
            hiddenTransitionsToEnable = getHiddenTransitionsToEnable(marking, placesWithMissing, placesShortestPathByHidden)
            z = 0
            while z < len(hiddenTransitionsToEnable):
                k = 0
                while k < len(hiddenTransitionsToEnable[z]):
                    t4 = hiddenTransitionsToEnable[z][k]
                    if not t4 == t:
                        if not t4 in visitedTransitions:
                            if not semantics.is_enabled(t4, net, marking):
                                [net, marking, activatedTransitions, allVisitedMarkings] = apply_hiddenTrans(t4, net, marking, placesShortestPathByHidden, activatedTransitions, recDepth+1, visitedTransitions, allVisitedMarkings)
                            if semantics.is_enabled(t4, net, marking):
                                marking = semantics.execute(t4, net, marking)
                                activatedTransitions.append(t4)
                                visitedTransitions.add(t4)
                                allVisitedMarkings.append(marking)
                    k = k + 1
                z = z + 1
        if not semantics.is_enabled(t, net, marking):
            if not(markingAtStart == marking):
                [net, marking, activatedTransitions, allVisitedMarkings] = apply_hiddenTrans(t, net, marking, placesShortestPathByHidden,
                                                                         activatedTransitions, recDepth + 1, visitedTransitions, allVisitedMarkings)

    return [net, marking, activatedTransitions, allVisitedMarkings]

def get_visible_transitions_eventually_enabled_by_marking(net, marking):
    """
    Get visible transitions eventually enabled by marking (passing possibly through hidden transitions)

    Parameters
    ----------
    net
        Petri net
    marking
        Current marking
    """
    allEnabledTransitions = list(semantics.enabled_transitions(net, marking))
    visibleTransitions = set()
    visitedTransitions = set()

    i = 0
    while i < len(allEnabledTransitions):
        t = allEnabledTransitions[i]
        if not t in visitedTransitions:
            if t.label is not None:
                visibleTransitions.add(t)
            else:
                markingCopy = copy(marking)
                if semantics.is_enabled(t, net, markingCopy):
                    newMarking = semantics.execute(t, net, markingCopy)
                    newEnabledTransitions = list(semantics.enabled_transitions(net, newMarking))
                    allEnabledTransitions = allEnabledTransitions + newEnabledTransitions
            visitedTransitions.add(t)
        i = i + 1

    return visibleTransitions

def break_condition_final_marking(marking, finalMarking):
    """
    Verify break condition for final marking

    Parameters
    -----------
    marking
        Current marking
    finalMarking
        Target final marking
    """
    finalMarkingDict = dict(finalMarking)
    markingDict = dict(marking)
    finalMarkingDictKeys = set(finalMarkingDict.keys())
    markingDictKeys = set(markingDict.keys())

    return finalMarkingDictKeys.issubset(markingDictKeys)

def apply_trace(trace, net, initialMarking, finalMarking, transMap, enable_placeFitness, place_fitness, placesShortestPathByHidden, consider_remaining_in_fitness, activity_key="concept:name", tryToReachFinalMarkingThroughHidden=True, stopImmediatelyWhenUnfit=False, useHiddenTransitionsToEnableCorrespondingTransitions=True, postFixCaching=None, markingToActivityCaching=None):
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
    trace_activities = [event[activity_key] for event in trace]
    activatedTransitions = []
    allVisitedMarkings = []
    activatingTransitionIndex = {}
    activatingTransitionInterval = []
    usedPostfixCache = False
    marking = copy(initialMarking)
    allVisitedMarkings.append(marking)
    missing = 0
    consumed = 0
    produced = 0
    i = 0
    while i < len(trace):
        if True and (str(trace_activities) in postFixCaching.cache and hash(marking) in postFixCaching.cache[str(trace_activities)]):
            transToAct = postFixCaching.cache[str(trace_activities)][hash(marking)]["transToAct"]
            z = 0
            while z < len(transToAct):
                t = transToAct[z]
                activatedTransitions.append(t)
                z = z + 1
            usedPostfixCache = True
            marking = postFixCaching.cache[str(trace_activities)][hash(marking)]["finalMarking"]
            break
        else:
            prevLenActivatedTransitions = len(activatedTransitions)
            if True and (hash(marking) in markingToActivityCaching.cache and trace[i][activity_key] in markingToActivityCaching.cache[hash(marking)] and trace[i-1][activity_key] == markingToActivityCaching.cache[hash(marking)][trace[i][activity_key]]["previousActivity"]):
                thisEndMarking = markingToActivityCaching.cache[hash(marking)][trace[i][activity_key]]["endMarking"]
                thisActTrans = markingToActivityCaching.cache[hash(marking)][trace[i][activity_key]]["thisActTrans"]
                thisVisMarkings = markingToActivityCaching.cache[hash(marking)][trace[i][activity_key]]["thisVisMarkings"]
                activatedTransitions = activatedTransitions + thisActTrans
                allVisitedMarkings = allVisitedMarkings + thisVisMarkings
                marking = copy(thisEndMarking)
            else:
                if trace[i][activity_key] in transMap:
                    t = transMap[trace[i][activity_key]]
                    if useHiddenTransitionsToEnableCorrespondingTransitions and not semantics.is_enabled(t, net, marking):
                        visitedTransitions = 0
                        visitedTransitions = set()
                        prevLenActivatedTransitions = len(activatedTransitions)
                        [net, marking, activatedTransitions, allVisitedMarkings] = apply_hiddenTrans(t, net, marking, placesShortestPathByHidden, activatedTransitions, 0, visitedTransitions, allVisitedMarkings)
                    if not semantics.is_enabled(t, net, marking):
                        if stopImmediatelyWhenUnfit:
                            missing = missing + 1
                            break
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
                    if semantics.is_enabled(t, net, marking):
                        marking = semantics.execute(t, net, marking)
                        activatedTransitions.append(t)
                        allVisitedMarkings.append(marking)
            del trace_activities[0]
            if len(trace_activities) < MAX_POSTFIX_SUFFIX_LENGTH:
                activatingTransitionIndex[str(trace_activities)] = {"index":len(activatedTransitions), "marking":hash(marking)}
            if i > 0:
                activatingTransitionInterval.append([trace[i][activity_key], prevLenActivatedTransitions, len(activatedTransitions), trace[i-1][activity_key]])
            else:
                activatingTransitionInterval.append(
                    [trace[i][activity_key], prevLenActivatedTransitions, len(activatedTransitions),
                     ""])
        i = i + 1

    if tryToReachFinalMarkingThroughHidden and not usedPostfixCache:
        i = 0
        while i < MAX_IT_FINAL:
            if not break_condition_final_marking(marking, finalMarking):
                hiddenTransitionsToEnable = getReqTransitionsForFinalMarking(marking, finalMarking, placesShortestPathByHidden)

                for group in hiddenTransitionsToEnable:
                    for t in group:
                        if semantics.is_enabled(t, net, marking):
                            marking = semantics.execute(t, net, marking)
                            activatedTransitions.append(t)
                            allVisitedMarkings.append(marking)
                    if break_condition_final_marking(marking, finalMarking):
                        break
            else:
                break
            i = i + 1

    markingBeforeCleaning = copy(marking)

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

    if consumed > 0 and produced > 0:
        trace_fitness = (1.0 - float(missing)/float(consumed)) * (1.0 - float(remaining)/float(produced))
    else:
        trace_fitness = 1.0

    if is_fit:
        for suffix in activatingTransitionIndex:
            if not suffix in postFixCaching.cache:
                postFixCaching.cache[suffix] = {}
            if not activatingTransitionIndex[suffix]["marking"] in postFixCaching.cache[suffix]:
                postFixCaching.cache[suffix][activatingTransitionIndex[suffix]["marking"]] =\
                    {"transToAct":activatedTransitions[activatingTransitionIndex[suffix]["index"]:],"finalMarking":marking}
        for trans in activatingTransitionInterval:
            activity = trans[0]
            startMarkingIndex = trans[1]
            endMarkingIndex = trans[2]
            previousActivity = trans[3]
            if endMarkingIndex < len(allVisitedMarkings):
                startMarkingObject = allVisitedMarkings[startMarkingIndex]
                startMarkingHash = hash(startMarkingObject)
                endMarkingObject = allVisitedMarkings[endMarkingIndex]
                if activity in transMap:
                    thisActivatedTrans = activatedTransitions[startMarkingIndex:endMarkingIndex]
                    thisVisitedMarkings = allVisitedMarkings[startMarkingIndex+1:endMarkingIndex+1]

                    if not startMarkingHash in markingToActivityCaching.cache:
                        markingToActivityCaching.cache[startMarkingHash] = {}
                    if not activity in markingToActivityCaching.cache[startMarkingHash]:
                        markingToActivityCaching.cache[startMarkingHash][activity] = {"startMarking":startMarkingObject, "endMarking":endMarkingObject,"thisActTrans":thisActivatedTrans,"thisVisMarkings":thisVisitedMarkings, "previousActivity":previousActivity}

    return [is_fit, trace_fitness, activatedTransitions, markingBeforeCleaning, get_visible_transitions_eventually_enabled_by_marking(net, markingBeforeCleaning)]

class ApplyTraceTokenReplay(Thread):
    def __init__(self, trace, net, initialMarking, finalMarking, transMap, enable_placeFitness, place_fitness, placesShortestPathByHidden, consider_remaining_in_fitness, activity_key="concept:name", tryToReachFinalMarkingThroughHidden=True, stopImmediatelyWhenUnfit=False, useHiddenTransitionsToEnableCorrespondingTransitions=True, postFixCaching=None, markingToActivityCaching=None):
        """
        Constructor
        """
        self.trace = trace
        self.net = net
        self.initialMarking = initialMarking
        self.finalMarking = finalMarking
        self.transMap = transMap
        self.enable_placeFitness = enable_placeFitness
        self.place_fitness = place_fitness
        self.placesShortestPathByHidden = placesShortestPathByHidden
        self.consider_remaining_in_fitness = consider_remaining_in_fitness
        self.activity_key = activity_key
        self.tryToReachFinalMarkingThroughHidden = tryToReachFinalMarkingThroughHidden
        self.stopImmediatelyWhenUnfit = stopImmediatelyWhenUnfit
        self.useHiddenTransitionsToEnableCorrespondingTransitions = useHiddenTransitionsToEnableCorrespondingTransitions
        self.postFixCaching = postFixCaching
        self.markingToActivityCaching = markingToActivityCaching
        Thread.__init__(self)

    def run(self):
        """
        Runs the thread and stores the results
        """
        self.tFit, self.tValue, self.actTrans, self.reachedMarking, self.enabledTransitionsInMarking =\
            apply_trace(self.trace, self.net, self.initialMarking, self.finalMarking, self.transMap,
                                                           self.enable_placeFitness, self.place_fitness,
                                                           self.placesShortestPathByHidden, self.consider_remaining_in_fitness, activity_key=self.activity_key,
                                                                                          tryToReachFinalMarkingThroughHidden=self.tryToReachFinalMarkingThroughHidden,
                                                                                          stopImmediatelyWhenUnfit=self.stopImmediatelyWhenUnfit,
                                                                                          useHiddenTransitionsToEnableCorrespondingTransitions=self.useHiddenTransitionsToEnableCorrespondingTransitions, postFixCaching=self.postFixCaching, markingToActivityCaching=self.markingToActivityCaching)

class PostFixCaching:
    """
    Post fix caching object
    """
    def __init__(self):
        self.cache = 0
        self.cache = {}

class MarkingToActivityCaching:
    """
    Marking to activity caching
    """
    def __init__(self):
        self.cache = 0
        self.cache = {}

def apply_log(log, net, initialMarking, finalMarking, enable_placeFitness=False, consider_remaining_in_fitness=False, activity_key="concept:name", tryToReachFinalMarkingThroughHidden=True, stopImmediatelyWhenUnfit=False, useHiddenTransitionsToEnableCorrespondingTransitions=True, placesShortestPathByHidden=None, variants=None):
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
    postFixCaching = PostFixCaching()
    markingToActivityCaching = MarkingToActivityCaching()
    if placesShortestPathByHidden is None:
        placesShortestPathByHidden = get_placesShortestPathByHidden(net)

    placeFitnessPerTrace = {}

    aligned_traces = []

    if enable_placeFitness:
        for place in net.places:
            placeFitnessPerTrace[place] = {"underfedTraces": set(), "overfedTraces": set()}
    transMap = {}
    for t in net.transitions:
        transMap[t.label] = t
    if len(log) > 0:
        if len(log[0]) > 0:
            if activity_key in log[0][0]:
                if variants is None:
                    parameters_variants = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}
                    variants = variants_module.get_variants(log, parameters=parameters_variants)
                vc = variants_module.get_variants_sorted_by_count(variants)
                threads = {}
                threadsResults = {}

                i = 0
                while i < len(vc):
                    variant = vc[i][0]
                    threadsKeys = list(threads.keys())
                    if len(threadsKeys) > MAX_NO_THREADS:
                        while len(threadsKeys) > 0:
                            t = threads[threadsKeys[0]]
                            t.join()
                            threadsResults[threadsKeys[0]] = {"tFit":copy(t.tFit),"tValue":copy(t.tValue),"actTrans":copy(t.actTrans),"reachedMarking":copy(t.reachedMarking),"enabledTransitionsInMarking":copy(t.enabledTransitionsInMarking)}
                            del threads[threadsKeys[0]]
                            del threadsKeys[0]
                    threads[variant] = ApplyTraceTokenReplay(variants[variant][0], net, initialMarking, finalMarking, transMap, enable_placeFitness, placeFitnessPerTrace, placesShortestPathByHidden, consider_remaining_in_fitness, activity_key=activity_key, tryToReachFinalMarkingThroughHidden=tryToReachFinalMarkingThroughHidden, stopImmediatelyWhenUnfit=stopImmediatelyWhenUnfit, useHiddenTransitionsToEnableCorrespondingTransitions=useHiddenTransitionsToEnableCorrespondingTransitions, postFixCaching=postFixCaching, markingToActivityCaching=markingToActivityCaching)
                    threads[variant].start()
                    #threads[variant].join()
                    i = i + 1
                threadsKeys = list(threads.keys())
                while len(threadsKeys) > 0:
                    t = threads[threadsKeys[0]]
                    t.join()
                    threadsResults[threadsKeys[0]] = {"tFit": copy(t.tFit), "tValue": copy(t.tValue), "actTrans": copy(t.actTrans),
                                               "reachedMarking": copy(t.reachedMarking),
                                               "enabledTransitionsInMarking": copy(t.enabledTransitionsInMarking)}
                    del threads[threadsKeys[0]]
                    del threadsKeys[0]
                for trace in log:
                    traceVariant =  ",".join([x[activity_key] for x in trace])
                    t = threadsResults[traceVariant]

                    aligned_traces.append(t)
            else:
                raise NoConceptNameException("at least an event is without " + activity_key)

    if enable_placeFitness:
        return aligned_traces, placeFitnessPerTrace
    else:
        return aligned_traces

def apply(log, net, initialMarking, finalMarking, parameters=None):
    """
    Method to apply token-based replay

    Parameters
    -----------
    log
        Log
    net
        Petri net
    initialMarking
        Initial marking
    finalMarking
        Final marking
    parameters
        Parameters of the algorithm
    activity_key
        Activity key (must be specified by the algorithm)
    variant
        Variant of the algorithm to use
    """
    if parameters is None:
        parameters = {}

    enable_placeFitness=False
    consider_remaining_in_fitness=False
    tryToReachFinalMarkingThroughHidden=True
    stopImmediatelyWhenUnfit=False
    useHiddenTransitionsToEnableCorrespondingTransitions=True
    placesShortestPathByHidden=None
    activity_key = xes_util.DEFAULT_NAME_KEY
    variants = None

    if "enable_placeFitness" in parameters:
        enable_placeFitness = parameters["enable_placeFitness"]
    if "consider_remaining_in_fitness" in parameters:
        consider_remaining_in_fitness = parameters["consider_remaining_in_fitness"]
    if "tryToReachFinalMarkingThroughHidden" in parameters:
        tryToReachFinalMarkingThroughHidden = parameters["tryToReachFinalMarkingThroughHidden"]
    if "stopImmediatelyWhenUnfit" in parameters:
        stopImmediatelyWhenUnfit = parameters["stopImmediatelyWhenUnfit"]
    if "useHiddenTransitionsToEnableCorrespondingTransitions" in parameters:
        useHiddenTransitionsToEnableCorrespondingTransitions = parameters["useHiddenTransitionsToEnableCorrespondingTransitions"]
    if "placesShortestPathByHidden" in parameters:
        placesShortestPathByHidden = parameters["placesShortestPathByHidden"]
    if "variants" in parameters:
        variants = parameters["variants"]
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

    return apply_log(log, net, initialMarking, finalMarking, enable_placeFitness=enable_placeFitness, consider_remaining_in_fitness=consider_remaining_in_fitness,
                     tryToReachFinalMarkingThroughHidden=tryToReachFinalMarkingThroughHidden, stopImmediatelyWhenUnfit=stopImmediatelyWhenUnfit,
                     useHiddenTransitionsToEnableCorrespondingTransitions=useHiddenTransitionsToEnableCorrespondingTransitions, placesShortestPathByHidden=placesShortestPathByHidden, activity_key=activity_key, variants=variants)
