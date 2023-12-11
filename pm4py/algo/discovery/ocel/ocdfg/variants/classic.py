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
from pm4py.util import exec_utils, pandas_utils
from pm4py.objects.ocel import constants as ocel_constants
from pm4py.objects.ocel.obj import OCEL
from pm4py.statistics.ocel import act_ot_dependent, act_utils, edge_metrics
from copy import copy


class Parameters(Enum):
    EVENT_ACTIVITY = ocel_constants.PARAM_EVENT_ACTIVITY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    COMPUTE_EDGES_PERFORMANCE = "compute_edges_performance"


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
        - Parameters.COMPUTE_EDGES_PERFORMANCE => (boolean) enables/disables the computation of the performance on the edges

    Returns
    -----------------
    ocdfg
        Object-centric directly-follows graph, expressed as a dictionary containing the following properties:
        - activities: complete set of activities derived from the object-centric event log
        - object_types: complete set of object types derived from the object-centric event log
        - edges: dictionary connecting each object type to a set of directly-followed arcs between activities (expressed as tuples,
                  e.g., (act1, act2)). Every pair of activities is linked to some sets:
                - event_pairs: the tuples of event identifiers where the directly-follows arc occurs
                - total_objects: set of tuples containing two event and one object identifier, uniquely identifying an
                                  occurrence of the arc.
        - activities_indep: dictionary linking each activity, regardless of the object type, to some sets:
            - events: the event identifiers where the activity occurs
            - unique_objects: the object identifiers where the activity occurs
            - total_objects: the tuples of event and object identifiers where the activity occurs.
        - activities_ot: dictionary linking each object type to another dictionary, where the activities are linked to some sets:
            - events: the event identifiers where the activity occurs (with at least one object of the given object type)
            - unique_objects: the object identifiers of the given object type where the activity occurs
            - total_objects: the tuples of event and object identifiers where the activity occurs.
        - start_activities: dictionary linking each object type to another dictionary, where the start activities
                            of the given object type are linked to some sets:
            - events: the event identifiers where the start activity occurs (with at least one object of the given object type)
            - unique_objects: the object identifiers of the given object type where the start activity occurs
            - total_objects: the tuples of event and object identifiers where the start activity occurs.
        - end_activities: dictionary linking each object type to another dictionary, where the end activities
                          of the given object type are linked to some sets:
            - events: the event identifiers where the end activity occurs (with at least one object of the given object type)
            - unique_objects: the object identifiers of the given object type where the end activity occurs
            - total_objects: the tuples of event and object identifiers where the end activity occurs.
    """
    if parameters is None:
        parameters = {}

    compute_edges_performance = exec_utils.get_param_value(Parameters.COMPUTE_EDGES_PERFORMANCE, parameters, True)

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
    ret["activities"] = set(pandas_utils.format_unique(ocel.events[event_activity].unique()))
    ret["object_types"] = set(pandas_utils.format_unique(ocel.objects[object_type].unique()))

    ret["edges"] = {}
    ret["edges"]["event_couples"] = edge_metrics.aggregate_ev_couples(edges)
    ret["edges"]["unique_objects"] = edge_metrics.aggregate_unique_objects(edges)
    ret["edges"]["total_objects"] = edge_metrics.aggregate_total_objects(edges)

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

    ret["edges_performance"] = {}
    ret["edges_performance"]["event_couples"] = {}
    ret["edges_performance"]["total_objects"] = {}

    if compute_edges_performance:
        ret["edges_performance"]["event_couples"] = edge_metrics.performance_calculation_ocel_aggregation(ocel,
                                                                                                          ret["edges"][
                                                                                                              "event_couples"],
                                                                                                          parameters=parameters)
        ret["edges_performance"]["total_objects"] = edge_metrics.performance_calculation_ocel_aggregation(ocel,
                                                                                                          ret["edges"][
                                                                                                              "total_objects"],
                                                                                                          parameters=parameters)

    return ret
