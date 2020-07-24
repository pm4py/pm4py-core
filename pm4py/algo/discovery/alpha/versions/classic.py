"""
This module implements the \"classic\" alpha miner [1]_.
It converts the input event log, which should be a log, to the (well-known) directly follows abstraction.
For example, when we have a trace of the form (control-flow perspective) <...a,b,...>, we observe the relation a>b, i.e.
activity a precedes activity b.
From the directly follows relations, the alpha relations parallelism (||), conflict (x) and causality (->) are deduced.
These relations form the basics for finding the places in the net.
Finally, a start and end place is added.

References
    ----------
    .. [1] Wil M. P. van der Aalst et al., "Workflow Mining: Discovering Process Models from Event Logs",
      IEEE Trans. Knowl. Data Eng., 16, 1128-1142, 2004. `DOI <https://doi.org/10.1109/TKDE.2004.47>`_.
"""

import time
from itertools import product

from pm4py import util as pm_util
from pm4py.algo.discovery.alpha.data_structures import alpha_classic_abstraction
from pm4py.algo.discovery.alpha.utils import endpoints
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.objects import petri
from pm4py.objects.petri.petrinet import Marking
from pm4py.algo.discovery.parameters import Parameters
from pm4py.util import exec_utils


def apply(log, parameters=None):
    """
    This method calls the \"classic\" alpha miner [1]_.

    Parameters
    ----------
    log: :class:`pm4py.log.log.EventLog`
        Event log to use in the alpha miner
    parameters:
        Parameters of the algorithm, including:
            activity_key : :class:`str`, optional
                Key to use within events to identify the underlying activity.
                By deafult, the value 'concept:name' is used.

    Returns
    -------
    net: :class:`pm4py.entities.petri.petrinet.PetriNet`
        A Petri net describing the event log that is provided as an input
    initial marking: :class:`pm4py.models.net.Marking`
        marking object representing the initial marking
    final marking: :class:`pm4py.models.net.Marking`
        marking object representing the final marking, not guaranteed that it is actually reachable!

    References
    ----------
    .. [1] Wil M. P. van der Aalst et al., "Workflow Mining: Discovering Process Models from Event Logs",
      IEEE Trans. Knowl. Data Eng., 16, 1128-1142, 2004. `DOI <https://doi.org/10.1109/TKDE.2004.47>`_.

    """
    if parameters is None:
        parameters = {}
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                              pm_util.xes_constants.DEFAULT_NAME_KEY)
    dfg = {k: v for k, v in dfg_inst.apply(log, parameters=parameters).items() if v > 0}
    start_activities = endpoints.derive_start_activities_from_log(log, activity_key)
    end_activities = endpoints.derive_end_activities_from_log(log, activity_key)
    return apply_dfg_sa_ea(dfg, start_activities, end_activities, parameters=parameters)


def apply_dfg(dfg, parameters=None):
    """
    Applying Alpha Miner starting from the knowledge of the Directly Follows graph,
    and of the start activities and end activities in the log inferred from the DFG

    Parameters
    ------------
    dfg
        Directly-Follows graph
    parameters
        Parameters of the algorithm including:
            activity key -> name of the attribute that contains the activity

    Returns
    -------
    net : :class:`pm4py.entities.petri.petrinet.PetriNet`
        A Petri net describing the event log that is provided as an input
    initial marking : :class:`pm4py.models.net.Marking`
        marking object representing the initial marking
    final marking : :class:`pm4py.models.net.Marking`
        marking object representing the final marking, not guaranteed that it is actually reachable!
    """

    return apply_dfg_sa_ea(dfg, None, None, parameters=parameters)


def apply_dfg_sa_ea(dfg, start_activities, end_activities, parameters=None):
    """
    Applying Alpha Miner starting from the knowledge of the Directly Follows graph,
    and of the start activities and end activities in the log (possibly inferred from the DFG)

    Parameters
    ------------
    dfg
        Directly-Follows graph
    start_activities
        Start activities
    end_activities
        End activities
    parameters
        Parameters of the algorithm including:
            activity key -> name of the attribute that contains the activity

    Returns
    -------
    net : :class:`pm4py.entities.petri.petrinet.PetriNet`
        A Petri net describing the event log that is provided as an input
    initial marking : :class:`pm4py.models.net.Marking`
        marking object representing the initial marking
    final marking : :class:`pm4py.models.net.Marking`
        marking object representing the final marking, not guaranteed that it is actually reachable!
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                              pm_util.xes_constants.DEFAULT_NAME_KEY)

    if start_activities is None:
        start_activities = dfg_utils.infer_start_activities(dfg)

    if end_activities is None:
        end_activities = dfg_utils.infer_end_activities(dfg)

    labels = set()
    for el in dfg:
        labels.add(el[0])
        labels.add(el[1])
    for a in start_activities:
        labels.add(a)
    for a in end_activities:
        labels.add(a)
    labels = list(labels)

    alpha_abstraction = alpha_classic_abstraction.ClassicAlphaAbstraction(start_activities, end_activities, dfg,
                                                                          activity_key=activity_key)
    pairs = list(map(lambda p: ({p[0]}, {p[1]}),
                     filter(lambda p: __initial_filter(alpha_abstraction.parallel_relation, p),
                            alpha_abstraction.causal_relation)))
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
    net = petri.petrinet.PetriNet('alpha_classic_net_' + str(time.time()))
    label_transition_dict = {}

    for i in range(0, len(labels)):
        label_transition_dict[labels[i]] = petri.petrinet.PetriNet.Transition(labels[i], labels[i])
        net.transitions.add(label_transition_dict[labels[i]])

    src = __add_source(net, alpha_abstraction.start_activities, label_transition_dict)
    sink = __add_sink(net, alpha_abstraction.end_activities, label_transition_dict)

    for pair in internal_places:
        place = petri.petrinet.PetriNet.Place(str(pair))
        net.places.add(place)
        for in_arc in pair[0]:
            petri.utils.add_arc_from_to(label_transition_dict[in_arc], place, net)
        for out_arc in pair[1]:
            petri.utils.add_arc_from_to(place, label_transition_dict[out_arc], net)
    return net, Marking({src: 1}), Marking({sink: 1})


def __add_source(net, start_activities, label_transition_dict):
    source = petri.petrinet.PetriNet.Place('start')
    net.places.add(source)
    for s in start_activities:
        petri.utils.add_arc_from_to(source, label_transition_dict[s], net)
    return source


def __add_sink(net, end_activities, label_transition_dict):
    end = petri.petrinet.PetriNet.Place('end')
    net.places.add(end)
    for e in end_activities:
        petri.utils.add_arc_from_to(label_transition_dict[e], end, net)
    return end


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
    S = set(product(item_set_1, item_set_2)).union(set(product(item_set_2, item_set_1)))
    for pair in S:
        if pair in parallel_relation or pair in causal_relation:
            return True
    return False
