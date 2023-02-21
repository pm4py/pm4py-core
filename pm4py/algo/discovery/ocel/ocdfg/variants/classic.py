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
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.statistics.ocel import act_ot_dependent, act_utils, edge_metrics
from copy import copy


class Parameters(Enum):
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> Dict[str, Any]:
    """
    Discovers an OC-DFG model from an object-centric event log.
    Reference paper:
    Berti, Alessandro, and Wil van der Aalst. "Extracting multiple viewpoint models from relational databases." Data-Driven Process Discovery and Analysis. Springer, Cham, 2018. 24-51.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ACTIVITY => the attribute to be used as activity
        - Parameters.OBJECT_TYPE => the attribute to be used as object type

    Returns
    -----------------
    ocdfg
        Object-centric directly-follows graph
    """
    if parameters is None:
        parameters = {}

    ot_independent = act_utils.find_associations_from_ocel(ocel, parameters=parameters)
    ot_dependent = act_ot_dependent.find_associations_from_ocel(ocel, parameters=parameters)
    start_parameters = copy(parameters)
    start_parameters["prefiltering"] = "start"
    ot_dependent_start = act_ot_dependent.find_associations_from_ocel(ocel, parameters=start_parameters)
    end_parameters = copy(parameters)
    end_parameters["prefiltering"] = "end"
    ot_dependent_end = act_ot_dependent.find_associations_from_ocel(ocel, parameters=end_parameters)
    edges = edge_metrics.find_associations_per_edge(ocel, parameters=end_parameters)

    object_type = exec_utils.get_param_value(Parameters.OBJECT_TYPE, parameters, ocel.object_type_column)
    event_activity = exec_utils.get_param_value(Parameters.EVENT_ACTIVITY, parameters, ocel.event_activity)

    ret = {}
    ret["activities"] = set(ocel.events[event_activity].unique())
    ret["object_types"] = set(ocel.objects[object_type].unique())

    ret["edges"] = {}
    ret["edges"]["event_couples"] = edge_metrics.aggregate_ev_couples(edges)
    ret["edges"]["unique_objects"] = edge_metrics.aggregate_unique_objects(edges)
    ret["edges"]["total_objects"] = edge_metrics.aggregate_total_objects(edges)

    ret["edges_performance"] = {}
    ret["edges_performance"]["event_couples"] = edge_metrics.performance_calculation_ocel_aggregation(ocel,
                                                                                                      ret["edges"][
                                                                                                          "event_couples"],
                                                                                                      parameters=parameters)
    ret["edges_performance"]["total_objects"] = edge_metrics.performance_calculation_ocel_aggregation(ocel,
                                                                                                      ret["edges"][
                                                                                                          "total_objects"],
                                                                                                      parameters=parameters)

    ret["activities_indep"] = {}
    ret["activities_indep"]["events"] = act_utils.aggregate_events(ot_independent)
    ret["activities_indep"]["unique_objects"] = act_utils.aggregate_unique_objects(ot_independent)
    ret["activities_indep"]["total_objects"] = act_utils.aggregate_total_objects(ot_independent)

    ret["activities_ot"] = {}
    ret["activities_ot"]["events"] = act_ot_dependent.aggregate_events(ot_dependent)
    ret["activities_ot"]["unique_objects"] = act_ot_dependent.aggregate_unique_objects(ot_dependent)
    ret["activities_ot"]["total_objects"] = act_ot_dependent.aggregate_total_objects(ot_dependent)

    ret["start_activities"] = {}
    ret["start_activities"]["events"] = act_ot_dependent.aggregate_events(ot_dependent_start)
    ret["start_activities"]["unique_objects"] = act_ot_dependent.aggregate_unique_objects(ot_dependent_start)
    ret["start_activities"]["total_objects"] = act_ot_dependent.aggregate_total_objects(ot_dependent_start)

    ret["end_activities"] = {}
    ret["end_activities"]["events"] = act_ot_dependent.aggregate_events(ot_dependent_end)
    ret["end_activities"]["unique_objects"] = act_ot_dependent.aggregate_unique_objects(ot_dependent_end)
    ret["end_activities"]["total_objects"] = act_ot_dependent.aggregate_total_objects(ot_dependent_end)

    return ret
