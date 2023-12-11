'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.objects.ocel import constants as ocel_constants
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from enum import Enum
from pm4py.util import exec_utils, pandas_utils
from pm4py.objects.ocel.util import flattening
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.petri_net.saw_net.obj import StochasticArcWeightNet
from pm4py.objects.petri_net.utils import petri_utils
from collections import Counter
from pm4py.util import vis_utils
from copy import copy


class Parameters(Enum):
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE


def __ot_to_color(ot: str) -> str:
    """
    Auxiliary method converting an object type to a color
    """
    ot = int(hash(ot))
    num = []
    while len(num) < 6:
        num.insert(0, ot % 16)
        ot = ot // 16
    ret = "#" + "".join([vis_utils.get_corr_hex(x) for x in num])
    return ret


def __discover_petri_and_consumption_stats_tbr(ocel: OCEL, obj_types, parameters: Optional[Dict[Any, Any]] = None):
    """
    Flattens the OCEL, discovers Petri nets for the flattened log,
    and by the token-based replay measures the usage of the elements
    """
    saw_weights = {}
    ocpn_nets = {}

    for ot in obj_types:
        flat_log = log_converter.apply(flattening.flatten(ocel, ot), variant=log_converter.Variants.TO_EVENT_LOG)
        process_tree = inductive_miner.apply(flat_log, parameters=parameters)
        net, im, fm = pt_converter.apply(process_tree)
        ocpn_nets[ot] = (net, im, fm)
        replayed_traces = token_replay.apply(flat_log, net, im, fm, parameters=parameters)
        transes_ev_ids = {x: [] for x in net.transitions}
        for i in range(len(flat_log)):
            flat_trace = flat_log[i]
            rep_res = replayed_traces[i]["activated_transitions"]
            j = 0
            z = 0
            while z < len(rep_res):
                evid = flat_trace[j][ocel.event_id_column]
                transes_ev_ids[rep_res[z]].append(evid)
                if rep_res[z].label is not None and j < len(flat_trace) - 1:
                    j = j + 1
                z = z + 1
        for x in transes_ev_ids:
            transes_ev_ids[x] = dict(Counter(list(Counter(transes_ev_ids[x]).values())))
        saw_weights[ot] = transes_ev_ids

    return ocpn_nets, saw_weights


def __get_ot_saw_nets(obj_types, ocpn_nets, saw_weights):
    """
    Computes a SAW net for every object type
    """
    ot_saw_nets = {}
    for ot in obj_types:
        net, im, fm = ocpn_nets[ot]
        saw_net = StochasticArcWeightNet(net.name)
        for place in net.places:
            saw_net.places.add(place)
        for trans in net.transitions:
            saw_net.transitions.add(trans)
        for arc in net.arcs:
            new_arc = petri_utils.add_arc_from_to(arc.source, arc.target, saw_net, type="stochastic_arc")
            if isinstance(new_arc.source, PetriNet.Transition) and new_arc.source in saw_weights[ot]:
                new_arc.weight = saw_weights[ot][new_arc.source]
            elif isinstance(new_arc.target, PetriNet.Transition) and new_arc.target in saw_weights[ot]:
                new_arc.weight = saw_weights[ot][new_arc.target]
        ot_saw_nets[ot] = saw_net
    return ot_saw_nets


def __get_multi_saw_net(ot_saw_nets):
    """
    Puts together the SAW nets of the single object types
    """
    multi_saw_net = StochasticArcWeightNet("multi")
    el_corr = dict()
    trans_unq_corr = dict()
    decorations_multi_saw_net = {}

    for ot in ot_saw_nets:
        otc0 = __ot_to_color(ot)
        ot_color = {"color": otc0}
        saw_net = ot_saw_nets[ot]
        for place in saw_net.places:
            multi_saw_net.places.add(place)
            el_corr[place] = place
            decorations_multi_saw_net[place] = ot_color
        for trans in saw_net.transitions:
            if trans.label is None:
                multi_saw_net.transitions.add(trans)
                el_corr[trans] = trans
                decorations_multi_saw_net[trans] = ot_color
            elif trans.label not in trans_unq_corr:
                multi_saw_net.transitions.add(trans)
                trans_unq_corr[trans.label] = trans
                el_corr[trans] = trans
            else:
                el_corr[trans] = el_corr[trans_unq_corr[trans.label]]
        for arc in saw_net.arcs:
            new_arc = petri_utils.add_arc_from_to(el_corr[arc.source], el_corr[arc.target], multi_saw_net, weight=arc.weight)
            decorations_multi_saw_net[new_arc] = ot_color

    return multi_saw_net, decorations_multi_saw_net


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers a SAW net representing the behavior of the provided object-centric event log.

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Possible parameters of the method, including:
        - Parameters.OBJECT_TYPE => the attribute of the log to be used as object type

    Returns
    --------------
    model
        Dictionary with the following keys:
        - ot_saw_net => the SAW nets for the single object types
        - multi_saw_net => the overall SAW net
        - decorations_multi_saw_net => decorations for the visualization of the SAW net
    """
    if parameters is None:
        parameters = {}

    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)
    obj_types = pandas_utils.format_unique(ocel.objects[object_type].unique())

    disc_parameters = copy(parameters)
    # disables the fallthroughs, as computing the model on a myriad of different object types
    # could be really expensive
    disc_parameters["disable_fallthroughs"] = True
    # for performance reasons, also disable the strict sequence cut (use the normal sequence cut)
    disc_parameters["disable_strict_sequence_cut"] = True
    ocpn_nets, saw_weights = __discover_petri_and_consumption_stats_tbr(ocel, obj_types, parameters=disc_parameters)

    ot_saw_nets = __get_ot_saw_nets(obj_types, ocpn_nets, saw_weights)
    multi_saw_net, decorations_multi_saw_net = __get_multi_saw_net(ot_saw_nets)

    return {"ot_saw_nets": ot_saw_nets, "multi_saw_net": multi_saw_net, "decorations_multi_saw_net": decorations_multi_saw_net}
