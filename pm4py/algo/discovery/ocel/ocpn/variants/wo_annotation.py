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
from pm4py.algo.discovery.ocel.ocdfg.variants import classic as ocdfg_discovery
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
from collections import Counter
from typing import Optional, Dict, Any


class Parameters(Enum):
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
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
    ocdfg = ocdfg_discovery.apply(ocel, parameters=parameters)

    petri_nets = {}
    double_arcs_on_activity = {}

    for ot in ocdfg["object_types"]:
        activities_eo = ocdfg["activities_ot"]["total_objects"][ot]

        activities = {x: len(y) for x, y in ocdfg["activities_ot"]["events"][ot].items()}
        start_activities = {x: len(y) for x, y in ocdfg["start_activities"]["events"][ot].items()}
        end_activities = {x: len(y) for x, y in ocdfg["end_activities"]["events"][ot].items()}
        dfg = {x: len(y) for x, y in ocdfg["edges"]["event_couples"][ot].items()}

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
        petri_nets[ot] = inductive_miner.apply_dfg(dfg, start_activities, end_activities, activities)

    ocdfg["petri_nets"] = petri_nets
    ocdfg["double_arcs_on_activity"] = double_arcs_on_activity

    return ocdfg
