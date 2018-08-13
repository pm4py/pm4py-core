from itertools import zip_longest
from pm4py.log.util import trace_log as tl_util
from pm4py.models import petri
import time

from pm4py.algo.alpha import data_structures as ds
from pm4py.models.petri.net import Marking


def apply(trace_log, activity_key='concept:name'):
    """
    This method calls the \"classic\" alpha miner [1]_.

    Parameters
    ----------
    trace_log : :class:`pm4py.log.instance.TraceLog`
        Event log to use in the alpha miner, note that it should be a TraceLog!
    activity_key : `str`, optional
        Key to use within events to identify the underlying activity.
        By deafult, the value 'concept:name' is used.

    Returns
    -------
    net : :class:`pm4py.models.petri.net.PetriNet`
        A Petri net describing the event log that is provided as an input

    References
    ----------
    .. [1] Wil M. P. van der Aalst et al., "Workflow Mining: Discovering Process Models from Event Logs",
      IEEE Trans. Knowl. Data Eng., 16, 1128-1142, 2004. `DOI <https://doi.org/10.1109/TKDE.2004.47>`_.

    """
    labels = tl_util.get_event_labels(trace_log, activity_key)
    alpha_abstraction = ds.ClassicAlphaAbstraction(trace_log, activity_key)
    pairs = list(map(lambda p: ({p[0]}, {p[1]}), filter(lambda p: __initial_filter(alpha_abstraction.parallel_relation, p), alpha_abstraction.causal_relation)))

    for i in range(0, len(pairs)):
        t1 = pairs[i]
        for j in range(i, len(pairs)):
            t2 = pairs[j]
            if t1 != t2:
                if t1[0].issubset(t2[0]) or t1[1].issubset(t2[1]):
                    if not (__check_is_unrelated(alpha_abstraction.parallel_relation, alpha_abstraction.causal_relation,
                                                 t1[0], t2[0]) or __check_is_unrelated(
                            alpha_abstraction.parallel_relation, alpha_abstraction.causal_relation, t1[1], t2[1])):
                        new_alpha_pair = (t1[0] | t2[0], t1[1] | t2[1])
                        if new_alpha_pair not in pairs:
                            pairs.append((t1[0] | t2[0], t1[1] | t2[1]))
    internal_places = filter(lambda p: __pair_maximizer(pairs, p), pairs)
    net = petri.net.PetriNet('alpha_classic_net_' + str(time.time()))
    label_transition_dict = {}

    for i in range(0, len(labels)):
        label_transition_dict[labels[i]] = petri.net.PetriNet.Transition('t_' + str(i), labels[i])
        net.transitions.add(label_transition_dict[labels[i]])

    src = __add_source(net, alpha_abstraction.start_activities, label_transition_dict)
    net = __add_sink(net, alpha_abstraction.end_activities, label_transition_dict)

    for pair in internal_places:
        place = petri.net.PetriNet.Place(str(pair))
        net.places.add(place)
        for in_arc in pair[0]:
            petri.utils.add_arc_from_to(label_transition_dict[in_arc], place, net)
        for out_arc in pair[1]:
            petri.utils.add_arc_from_to(place, label_transition_dict[out_arc], net)
    return net, Marking({src: 1})


def __add_source(net, start_activities, label_transition_dict):
    source = petri.net.PetriNet.Place('start')
    net.places.add(source)
    for s in start_activities:
        petri.utils.add_arc_from_to(source, label_transition_dict[s], net)
    return source


def __add_sink(net, end_activities, label_transition_dict):
    end = petri.net.PetriNet.Place('end')
    net.places.add(end)
    for e in end_activities:
        petri.utils.add_arc_from_to(label_transition_dict[e], end, net)
    return net


def __initial_filter(parallel_relation, pair):
    if (pair[0], pair[0]) in parallel_relation or (pair[1], pair[1]) in parallel_relation:
        return False
    return True


def __pair_maximizer(alpha_pairs, pair):
    for alt in alpha_pairs:
        if pair != alt and pair[0].issubset(alt[0]) and pair[1].issubset(alt[1]):
            return False
    return True


def __check_is_unrelated(parallel_relation, causal_relation, item_set_1, item_set_2):
    for pair in zip_longest(item_set_1, item_set_2):
        if pair in parallel_relation or pair in causal_relation:
            return True
    return False
