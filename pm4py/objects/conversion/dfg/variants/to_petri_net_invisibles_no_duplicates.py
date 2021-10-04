from copy import copy
from enum import Enum
from typing import Optional, Dict, Any, Tuple

from pm4py.objects.dfg.utils import dfg_utils
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils
from pm4py.util import exec_utils, constants


class Parameters(Enum):
    START_ACTIVITIES = 'start_activities'
    END_ACTIVITIES = 'end_activities'
    PARAM_ARTIFICIAL_START_ACTIVITY = constants.PARAM_ARTIFICIAL_START_ACTIVITY
    PARAM_ARTIFICIAL_END_ACTIVITY = constants.PARAM_ARTIFICIAL_END_ACTIVITY


def apply(dfg: Dict[Tuple[str, str], int], parameters: Optional[Dict[Any, Any]] = None):
    """
    Applies the DFG mining on a given object (if it is a Pandas dataframe or a log, the DFG is calculated)

    Parameters
    -------------
    dfg
        Object (DFG) (if it is a Pandas dataframe or a log, the DFG is calculated)
    parameters
        Parameters:
        - Parameters.START_ACTIVITIES: the start activities of the DFG
        - Parameters.END_ACTIVITIES: the end activities of the DFG

    Returns
    -------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    start_activities = exec_utils.get_param_value(Parameters.START_ACTIVITIES, parameters,
                                                  {x: 1 for x in dfg_utils.infer_start_activities(
                                                      dfg)})
    end_activities = exec_utils.get_param_value(Parameters.END_ACTIVITIES, parameters,
                                                {x: 1 for x in dfg_utils.infer_end_activities(dfg)})
    artificial_start_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_START_ACTIVITY, parameters, constants.DEFAULT_ARTIFICIAL_START_ACTIVITY)
    artificial_end_activity = exec_utils.get_param_value(Parameters.PARAM_ARTIFICIAL_END_ACTIVITY, parameters, constants.DEFAULT_ARTIFICIAL_END_ACTIVITY)

    enriched_dfg = copy(dfg)
    for act in start_activities:
        enriched_dfg[(artificial_start_activity, act)] = start_activities[act]
    for act in end_activities:
        enriched_dfg[(act, artificial_end_activity)] = end_activities[act]
    activities = set(x[1] for x in enriched_dfg).union(set(x[0] for x in enriched_dfg))
    net = PetriNet("")
    im = Marking()
    fm = Marking()
    left_places = {}
    transes = {}
    right_places = {}
    for act in activities:
        pl1 = PetriNet.Place("source_" + act)
        pl2 = PetriNet.Place("sink_" + act)
        trans = PetriNet.Transition("trans_" + act, act)
        if act in [artificial_start_activity, artificial_end_activity]:
            trans.label = None
        net.places.add(pl1)
        net.places.add(pl2)
        net.transitions.add(trans)
        petri_utils.add_arc_from_to(pl1, trans, net)
        petri_utils.add_arc_from_to(trans, pl2, net)
        left_places[act] = pl1
        right_places[act] = pl2
        transes[act] = trans
    for arc in enriched_dfg:
        hidden = PetriNet.Transition(arc[0] + "_" + arc[1], None)
        net.transitions.add(hidden)
        petri_utils.add_arc_from_to(right_places[arc[0]], hidden, net)
        petri_utils.add_arc_from_to(hidden, left_places[arc[1]], net)
    im[left_places[artificial_start_activity]] = 1
    fm[right_places[artificial_end_activity]] = 1

    return net, im, fm
