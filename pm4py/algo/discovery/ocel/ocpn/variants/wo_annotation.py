from pm4py.objects.ocel.obj import OCEL
from pm4py.algo.discovery.ocel.ocdfg.variants import classic as ocdfg_discovery
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
from collections import Counter
from typing import Optional, Dict, Any
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.conversion.process_tree import converter as tree_converter
from pm4py.objects.ocel.util import flattening


class Parameters(Enum):
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    INDUCTIVE_MINER_VARIANT = "inductive_miner_variant"
    DOUBLE_ARC_THRESHOLD = "double_arc_threshold"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers an object-centric Petri net (without annotation) from the given object-centric event log,
    using the Inductive Miner as process discovery algorithm.

    Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ACTIVITY => the activity attribute to be used
        - Parameters.OBJECT_TYPE => the object type attribute to be used
        - Parameters.DOUBLE_ARC_THRESHOLD => the threshold for the attribution of the "double arc", as
        described in the paper.

    Returns
    -----------------
    ocpn
        Object-centric Petri net model, as a dictionary of properties.
    """
    if parameters is None:
        parameters = {}

    double_arc_threshold = exec_utils.get_param_value(Parameters.DOUBLE_ARC_THRESHOLD, parameters, 0.0)
    inductive_miner_variant = exec_utils.get_param_value(Parameters.INDUCTIVE_MINER_VARIANT, parameters, "im")

    ocpn = ocdfg_discovery.apply(ocel, parameters=parameters)

    petri_nets = {}
    double_arcs_on_activity = {}
    tbr_results = {}

    for ot in ocpn["object_types"]:
        activities_eo = ocpn["activities_ot"]["total_objects"][ot]

        start_activities = {x: len(y) for x, y in ocpn["start_activities"]["events"][ot].items()}
        end_activities = {x: len(y) for x, y in ocpn["end_activities"]["events"][ot].items()}
        dfg = {}
        if ot in ocpn["edges"]["event_couples"]:
            dfg = {x: len(y) for x, y in ocpn["edges"]["event_couples"][ot].items()}

        is_activity_double = {}
        for act in activities_eo:
            ev_obj_count = Counter()
            for evc in activities_eo[act]:
                ev_obj_count[evc[0]] += 1
            this_single_amount = len(list(x for x in ev_obj_count if ev_obj_count[x] == 1)) / len(ev_obj_count)
            if this_single_amount <= double_arc_threshold:
                is_activity_double[act] = True
            else:
                is_activity_double[act] = False

        double_arcs_on_activity[ot] = is_activity_double

        process_tree = None
        if inductive_miner_variant == "imd":
            obj = DFG()
            obj._graph = Counter(dfg)
            obj._start_activities = Counter(start_activities)
            obj._end_activities = Counter(end_activities)
            process_tree = inductive_miner.apply(obj, variant=inductive_miner.Variants.IMd, parameters=parameters)
            petri_nets[ot] = tree_converter.apply(process_tree, parameters=parameters)
        elif inductive_miner_variant == "im":
            flat_log = flattening.flatten(ocel, ot, parameters=parameters)
            process_tree = inductive_miner.apply(flat_log, parameters=parameters)
            petri_net = tree_converter.apply(process_tree, parameters=parameters)
            petri_nets[ot] = petri_net

    ocpn["petri_nets"] = petri_nets
    ocpn["double_arcs_on_activity"] = double_arcs_on_activity
    ocpn["tbr_results"] = tbr_results

    return ocpn
