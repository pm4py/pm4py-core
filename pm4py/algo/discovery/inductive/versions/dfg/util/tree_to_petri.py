from pm4py.entities import petri
from pm4py.entities.petri.petrinet import PetriNet
from pm4py.algo.discovery.dfg.utils.dfg_utils import max_occ_all_activ, sum_start_activities_count, \
    sum_end_activities_count, sum_activities_count, max_occ_among_specif_activ
from pm4py.algo.discovery.inductive.versions.dfg.util.petri_el_add import get_new_place, get_new_hidden_trans, get_transition

def verify_skip_transition_necessity(mAddSkip, initialDfg, activities, initial_connect_to):
    """
    Utility functions that decides if the skip transition is necessary

    Parameters
    ----------
    mAddSkip
        Boolean value, provided by the parent caller, that tells if the skip is absolutely necessary
    initialDfg
        Initial DFG
    activities
        Provided activities of the DFG
    initial_connect_to
        Source place of the subtree
    """
    if initial_connect_to.name == "p_1":
        return False
    if mAddSkip:
        return True

    maxValue = max_occ_all_activ(initialDfg)
    sumStartActivitiesCount = sum_start_activities_count(initialDfg)
    endActivitiesCount = sum_end_activities_count(initialDfg)
    maxValueWithActivitiesSpecification = sum_activities_count(initialDfg, activities)

    condition1 = sumStartActivitiesCount > 0 and maxValueWithActivitiesSpecification < sumStartActivitiesCount
    condition2 = endActivitiesCount > 0 and maxValueWithActivitiesSpecification < endActivitiesCount
    condition3 = sumStartActivitiesCount <= 0 and endActivitiesCount <= 0 and maxValue > 0 and maxValueWithActivitiesSpecification < maxValue
    condition = condition1 or condition2 or condition3

    if condition:
        return True

    return False


def form_petrinet(tree, recDepth, counts, net, initial_marking, final_marking, must_add_initial_place=False,
                  must_add_final_place=False, initial_connect_to=None, final_connect_to=None, must_add_skip=False,
                  must_add_loop=False):
    """
    Form a Petri net from the current tree structure

    Parameters
    -----------
    tree
        Current recursion subtree
    recDepth
        Current recursion depth
    counts
        Count object
    net
        Petri net object
    initial_marking
        Initial marking object
    final_marking
        Final marking object
    must_add_initial_place
        When recursive calls are done, tells to add a new place (from which the subtree starts)
    must_add_final_place
        When recursive calls are done, tells to add a new place (into which the subtree goes)
    initial_connect_to
        Initial element (place/transition) to which we should connect the subtree
    final_connect_to
        Final element (place/transition) to which we should connect the subtree
    must_add_skip
        Must add skip transition
    must_add_loop
        Must add loop transition

    Returns
    ----------
    net
        Petri net object
    initial_marking
        Initial marking object
    final_marking
        Final marking object
    lastAddedPlace
        lastAddedPlace
    """
    lastAddedPlace = None
    initialPlace = None
    finalPlace = None
    if recDepth == 0:
        source = get_new_place(counts)
        initial_connect_to = source
        initialPlace = source
        net.places.add(source)
        sink = get_new_place(counts)
        final_connect_to = sink
        net.places.add(sink)
        lastAddedPlace = sink
    elif recDepth > 0:
        if must_add_initial_place or type(initial_connect_to) is PetriNet.Transition:
            initialPlace = get_new_place(counts)
            net.places.add(initialPlace)
            petri.utils.add_arc_from_to(initial_connect_to, initialPlace, net)
        else:
            initialPlace = initial_connect_to
        if must_add_final_place or type(final_connect_to) is PetriNet.Transition:
            finalPlace = get_new_place(counts)
            net.places.add(finalPlace)
            petri.utils.add_arc_from_to(finalPlace, final_connect_to, net)
        else:
            finalPlace = final_connect_to
        if counts.noOfPlaces == 2 and len(tree.activities) > 1:
            initialTrans = get_new_hidden_trans(counts, type="tau")
            net.transitions.add(initialTrans)
            newPlace = get_new_place(counts)
            net.places.add(newPlace)
            petri.utils.add_arc_from_to(initial_connect_to, initialTrans, net)
            petri.utils.add_arc_from_to(initialTrans, newPlace, net)
            initialPlace = newPlace

    if tree.detectedCut == "base_concurrent" or tree.detectedCut == "flower":
        if final_connect_to is None or type(final_connect_to) is PetriNet.Transition:
            if finalPlace is not None:
                lastAddedPlace = finalPlace
            else:
                lastAddedPlace = get_new_place(counts)
                net.places.add(lastAddedPlace)
        else:
            lastAddedPlace = final_connect_to

        prevNoOfVisibleTransitions = counts.noOfVisibleTransitions

        for act in tree.activities:
            trans = get_transition(counts, act)
            net.transitions.add(trans)
            petri.utils.add_arc_from_to(initialPlace, trans, net)
            petri.utils.add_arc_from_to(trans, lastAddedPlace, net)

        maxValue = max_occ_all_activ(tree.initialDfg)
        sumStartActivitiesCount = sum_start_activities_count(tree.initialDfg)
        endActivitiesCount = sum_end_activities_count(tree.initialDfg)
        maxValueWithActivitiesSpecification = sum_activities_count(tree.initialDfg, tree.activities)

        condition1 = sumStartActivitiesCount > 0 and maxValueWithActivitiesSpecification < sumStartActivitiesCount
        condition2 = endActivitiesCount > 0 and maxValueWithActivitiesSpecification < endActivitiesCount
        condition3 = sumStartActivitiesCount <= 0 and endActivitiesCount <= 0 and maxValue > 0 and maxValueWithActivitiesSpecification < maxValue
        condition = condition1 or condition2 or condition3

        if condition and not initial_connect_to.name == "p_1" and prevNoOfVisibleTransitions > 0:
            # add skip transition
            skipTrans = get_new_hidden_trans(counts, type="skip")
            net.transitions.add(skipTrans)
            petri.utils.add_arc_from_to(initialPlace, skipTrans, net)
            petri.utils.add_arc_from_to(skipTrans, lastAddedPlace, net)

    # iterate over childs
    if tree.detectedCut == "sequential" or tree.detectedCut == "loopCut":

        mAddSkip = False
        mAddLoop = False
        if tree.detectedCut == "loopCut":
            mAddSkip = True
            mAddLoop = True

        net, initial_marking, final_marking, lastAddedPlace, counts = form_petrinet(tree.children[0], recDepth + 1,
                                                                                    counts, net, initial_marking,
                                                                                    final_marking,
                                                                                    initial_connect_to=initialPlace,
                                                                                    must_add_skip=verify_skip_transition_necessity(
                                                                                        mAddSkip,
                                                                                        tree.initialDfg,
                                                                                        tree.activities,
                                                                                        initialPlace),
                                                                                    must_add_loop=mAddLoop)
        net, initial_marking, final_marking, lastAddedPlace, counts = form_petrinet(tree.children[1], recDepth + 1,
                                                                                    counts, net,
                                                                                    initial_marking,
                                                                                    final_marking,
                                                                                    initial_connect_to=lastAddedPlace,
                                                                                    final_connect_to=finalPlace,
                                                                                    must_add_skip=verify_skip_transition_necessity(
                                                                                        mAddSkip,
                                                                                        tree.initialDfg,
                                                                                        tree.activities,
                                                                                        lastAddedPlace),
                                                                                    must_add_loop=mAddLoop)
    elif tree.detectedCut == "parallel":
        mAddSkip = False
        mAddLoop = False

        if finalPlace is None:
            finalPlace = get_new_place(counts)
            net.places.add(finalPlace)

        children_occurrences = []
        for child in tree.children:
            child_occ = max_occ_among_specif_activ(tree.dfg, child.activities)
            children_occurrences.append(child_occ)
        if children_occurrences:
            if not (children_occurrences[0] == children_occurrences[-1]):
                mAddSkip = True

        parallelSplit = get_new_hidden_trans(counts, "tauSplit")
        net.transitions.add(parallelSplit)
        petri.utils.add_arc_from_to(initialPlace, parallelSplit, net)

        parallelJoin = get_new_hidden_trans(counts, "tauJoin")
        net.transitions.add(parallelJoin)
        petri.utils.add_arc_from_to(parallelJoin, finalPlace, net)

        for child in tree.children:
            mAddSkipFinal = verify_skip_transition_necessity(mAddSkip, tree.dfg, tree.activities, parallelSplit)

            net, initial_marking, final_marking, lastAddedPlace, counts = form_petrinet(child, recDepth + 1, counts,
                                                                                        net, initial_marking,
                                                                                        final_marking,
                                                                                        must_add_initial_place=True,
                                                                                        must_add_final_place=True,
                                                                                        initial_connect_to=parallelSplit,
                                                                                        final_connect_to=parallelJoin,
                                                                                        must_add_skip=mAddSkipFinal,
                                                                                        must_add_loop=mAddLoop)

        lastAddedPlace = finalPlace

    elif tree.detectedCut == "concurrent":
        mAddSkip = False
        mAddLoop = False

        if finalPlace is None:
            finalPlace = get_new_place(counts)
            net.places.add(finalPlace)

        for child in tree.children:
            net, initial_marking, final_marking, lastAddedPlace, counts = form_petrinet(child, recDepth + 1, counts,
                                                                                        net, initial_marking,
                                                                                        final_marking,
                                                                                        initial_connect_to=initialPlace,
                                                                                        final_connect_to=finalPlace,
                                                                                        must_add_skip=verify_skip_transition_necessity(
                                                                                            mAddSkip,
                                                                                            tree.initialDfg,
                                                                                            tree.activities,
                                                                                            initialPlace),
                                                                                        must_add_loop=mAddLoop)

        lastAddedPlace = finalPlace

    if tree.detectedCut == "flower" or tree.detectedCut == "sequential" or tree.detectedCut == "loopCut" or tree.detectedCut == "base_concurrent" or tree.detectedCut == "parallel" or tree.detectedCut == "concurrent":
        if must_add_skip:
            if not (initialPlace.name in counts.dictSkips and lastAddedPlace.name in counts.dictSkips[
                initialPlace.name]):
                skipTrans = get_new_hidden_trans(counts, type="skip")
                net.transitions.add(skipTrans)
                petri.utils.add_arc_from_to(initialPlace, skipTrans, net)
                petri.utils.add_arc_from_to(skipTrans, lastAddedPlace, net)

                if not initialPlace.name in counts.dictSkips:
                    counts.dictSkips[initialPlace.name] = []

                counts.dictSkips[initialPlace.name].append(lastAddedPlace.name)

        if tree.detectedCut == "flower" or must_add_loop:
            if not (initialPlace.name in counts.dictLoops and lastAddedPlace.name in counts.dictLoops[
                initialPlace.name]):
                loopTrans = get_new_hidden_trans(counts, type="loop")
                net.transitions.add(loopTrans)
                petri.utils.add_arc_from_to(lastAddedPlace, loopTrans, net)
                petri.utils.add_arc_from_to(loopTrans, initialPlace, net)

                if not initialPlace.name in counts.dictLoops:
                    counts.dictLoops[initialPlace.name] = []

                counts.dictLoops[initialPlace.name].append(lastAddedPlace.name)

    if recDepth == 0:
        if len(sink.out_arcs) == 0 and len(sink.in_arcs) == 0:
            net.places.remove(sink)
            sink = lastAddedPlace

        if len(sink.out_arcs) > 0:
            newSink = get_new_place(counts)
            net.places.add(newSink)
            newHidden = get_new_hidden_trans(counts, type="tau")
            net.transitions.add(newHidden)
            petri.utils.add_arc_from_to(sink, newHidden, net)
            petri.utils.add_arc_from_to(newHidden, newSink, net)
            sink = newSink

        if len(source.in_arcs) > 0:
            newSource = get_new_place(counts)
            net.places.add(newSource)
            newHidden = get_new_hidden_trans(counts, type="tau")
            net.transitions.add(newHidden)
            petri.utils.add_arc_from_to(newSource, newHidden, net)
            petri.utils.add_arc_from_to(newHidden, source, net)
            source = newSource

        source.name = "source"
        sink.name = "sink"
        initial_marking[source] = 1
        final_marking[sink] = 1

    return net, initial_marking, final_marking, lastAddedPlace, counts
