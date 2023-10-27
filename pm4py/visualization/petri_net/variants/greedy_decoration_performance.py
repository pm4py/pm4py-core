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
from pm4py.algo.discovery.dfg.variants import native, performance
from pm4py.statistics.attributes.log import get as attr_get
from pm4py.util import xes_constants as xes
from pm4py.visualization.petri_net.common import visualize
from pm4py.visualization.petri_net.util.vis_trans_shortest_paths import get_decorations_from_dfg_spaths_acticount
from pm4py.visualization.petri_net.util.vis_trans_shortest_paths import get_shortest_paths
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY, PARAMETER_CONSTANT_TIMESTAMP_KEY
from pm4py.objects.petri_net.obj import PetriNet, Marking
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog
import graphviz


class Parameters(Enum):
    FORMAT = "format"
    DEBUG = "debug"
    RANKDIR = "set_rankdir"
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = PARAMETER_CONSTANT_TIMESTAMP_KEY
    AGGREGATION_MEASURE = "aggregationMeasure"
    FONT_SIZE = "font_size"
    STAT_LOCALE = "stat_locale"


def get_decorated_net(net, initial_marking, final_marking, log, parameters=None, variant="frequency"):
    """
    Get a decorated net according to the specified variant (decorate Petri net based on DFG)

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        Log to use to decorate the Petri net
    parameters
        Algorithm parameters
    variant
        Specify if the decoration should take into account the frequency or the performance

    Returns
    ------------
    gviz
        GraphViz object
    """
    if parameters is None:
        parameters = {}

    aggregation_measure = exec_utils.get_param_value(Parameters.AGGREGATION_MEASURE, parameters,
                                                     "sum" if "frequency" in variant else "mean")

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    stat_locale = exec_utils.get_param_value(Parameters.STAT_LOCALE, parameters, {})

    # we find the DFG
    if variant == "performance":
        dfg = performance.performance(log, parameters=parameters)
    else:
        dfg = native.native(log, parameters=parameters)
    # we find shortest paths
    spaths = get_shortest_paths(net)
    # we find the number of activities occurrences in the log
    activities_count = attr_get.get_attribute_values(log, activity_key, parameters=parameters)
    aggregated_statistics = get_decorations_from_dfg_spaths_acticount(net, dfg, spaths,
                                                                      activities_count,
                                                                      variant=variant,
                                                                      aggregation_measure=aggregation_measure,
                                                                      stat_locale=stat_locale)

    return visualize.apply(net, initial_marking, final_marking, parameters=parameters,
                           decorations=aggregated_statistics)


def apply(net: PetriNet, initial_marking: Marking, final_marking: Marking, log: EventLog = None, aggregated_statistics=None, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> graphviz.Digraph:
    """
    Apply performance decoration through greedy algorithm (decorate Petri net based on DFG)

    Parameters
    ------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        Log to use to decorate the Petri net
    aggregated_statistics
        Dictionary containing the frequency statistics
    parameters
        Algorithm parameters

    Returns
    ------------
    gviz
        GraphViz object
    """
    del aggregated_statistics
    return get_decorated_net(net, initial_marking, final_marking, log, parameters=parameters, variant="performance")
