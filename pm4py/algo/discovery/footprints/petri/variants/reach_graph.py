from pm4py.objects.petri import reachability_graph
import itertools
from pm4py.algo.discovery.footprints.outputs import Outputs


def findsubsets(s, n):
    return list(itertools.combinations(s, n))


def apply(net, im, parameters=None):
    """
    Discovers a footprint object from a Petri net

    Parameters
    --------------
    net
        Petri net
    im
        Initial marking
    parameters
        Parameters of the algorithm

    Returns
    --------------
    footprints_obj
        Footprints object
    """
    if parameters is None:
        parameters = {}

    incoming_transitions, outgoing_transitions, eventually_enabled = reachability_graph.marking_flow_petri(net, im,
                                                                                                           return_eventually_enabled=True,
                                                                                                           parameters=parameters)

    sequence = set()

    s1 = set()
    s2 = set()

    for m in outgoing_transitions:
        input_trans = set(x for x in incoming_transitions[m] if x.label is not None)
        output_trans = set(x for x in outgoing_transitions[m].keys() if x.label is not None)
        ev_en = set(x for x in eventually_enabled[m])
        two_sets = findsubsets(output_trans, 2)

        for (x, y) in two_sets:
            s1.add((x, y))
            s1.add((y, x))

        for t1 in input_trans:
            for t2 in ev_en:
                sequence.add((t1, t2))
            for t2 in output_trans:
                s2.add((t1, t2))

    parallel = {(x, y) for (x, y) in s2 if (y, x) in s2 and (x, y) in s1}
    sequence = {(x, y) for (x, y) in sequence if not (x, y) in parallel}

    parallel = {(x.label, y.label) for (x, y) in parallel}
    sequence = {(x.label, y.label) for (x, y) in sequence}

    activities = set(x.label for x in net.transitions if x.label is not None)
    start_activities = set(x.label for x in eventually_enabled[im])

    return {Outputs.SEQUENCE.value: sequence, Outputs.PARALLEL.value: parallel, Outputs.ACTIVITIES.value: activities, Outputs.START_ACTIVITIES.value: start_activities}
