from pm4py.statistics.attributes.log import get as attr_get
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.util import xes_constants as xes
from pm4py.util import exec_utils
from pm4py.statistics.sojourn_time.log import get as soj_time_get
from enum import Enum
from pm4py.util import constants
from typing import Optional, Dict, Any, Tuple
import graphviz
from pm4py.objects.log.obj import EventLog
from collections import Counter
from pm4py.visualization.dfg.util import dfg_gviz


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    FORMAT = "format"
    MAX_NO_EDGES_IN_DIAGRAM = "maxNoOfEdgesInDiagram"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    FONT_SIZE = "font_size"
    BGCOLOR = "bgcolor"


def apply(dfg: Dict[Tuple[str, str], int], log: EventLog = None, parameters: Optional[Dict[Any, Any]] = None, activities_count : Dict[str, int] = None, soj_time: Dict[str, float] = None) -> graphviz.Digraph:
    """
    Visualize a frequency directly-follows graph

    Parameters
    -----------------
    dfg
        Frequency Directly-follows graph
    log
        (if provided) Event log for the calculation of statistics
    activities_count
        (if provided) Dictionary associating to each activity the number of occurrences in the log.
    soj_time
        (if provided) Dictionary associating to each activity the average sojourn time
    parameters
        Variant-specific parameters

    Returns
    -----------------
    gviz
        Graphviz digraph
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes.DEFAULT_NAME_KEY)
    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    max_no_of_edges_in_diagram = exec_utils.get_param_value(Parameters.MAX_NO_EDGES_IN_DIAGRAM, parameters, 100000)
    start_activities = exec_utils.get_param_value(Parameters.START_ACTIVITIES, parameters, {})
    end_activities = exec_utils.get_param_value(Parameters.END_ACTIVITIES, parameters, {})
    font_size = exec_utils.get_param_value(Parameters.FONT_SIZE, parameters, 12)
    font_size = str(font_size)
    activities = dfg_utils.get_activities_from_dfg(dfg)
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)

    if activities_count is None:
        if log is not None:
            activities_count = attr_get.get_attribute_values(log, activity_key, parameters=parameters)
        else:
            # the frequency of an activity in the log is at least the number of occurrences of
            # incoming arcs in the DFG.
            # if the frequency of the start activities nodes is also provided, use also that.
            activities_count = Counter({key: 0 for key in activities})
            for el in dfg:
                activities_count[el[1]] += dfg[el]
            if isinstance(start_activities, dict):
                for act in start_activities:
                    activities_count[act] += start_activities[act]

    if soj_time is None:
        if log is not None:
            soj_time = soj_time_get.apply(log, parameters=parameters)
        else:
            soj_time = {key: 0 for key in activities}

    return dfg_gviz.graphviz_visualization(activities_count, dfg, image_format=image_format, measure="frequency",
                                  max_no_of_edges_in_diagram=max_no_of_edges_in_diagram,
                                  start_activities=start_activities, end_activities=end_activities, soj_time=soj_time,
                                  font_size=font_size, bgcolor=bgcolor)
