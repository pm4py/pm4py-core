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

import tempfile
import re
import warnings
from copy import copy

from graphviz import Digraph
from graphviz.dot import node

from pm4py.statistics.attributes.log import get as attr_get
from pm4py.objects.dfg.utils import dfg_utils
from pm4py.util import xes_constants as xes
from pm4py.visualization.common.utils import *
from pm4py.util import exec_utils
from pm4py.statistics.sojourn_time.log import get as soj_time_get
from enum import Enum
from pm4py.util import constants
from typing import Optional, Dict, Any, Tuple, no_type_check_decorator
from pm4py.objects.log.obj import EventLog
from collections import Counter


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
    STAT_LOCALE = "stat_locale"


def get_min_max_value(dfg):
    min_value = 9999999999
    max_value = -1

    for edge in dfg:
        if dfg[edge] < min_value:
            min_value = dfg[edge]
        if dfg[edge] > max_value:
            max_value = dfg[edge]

    return min_value, max_value


def assign_penwidth_edges(dfg):

    penwidth = {}
    min_value, max_value = get_min_max_value(dfg)
    for edge in dfg:
        v0 = dfg[edge]
        v1 = get_arc_penwidth(v0, min_value, max_value)
        penwidth[edge] = str(v1)

    return penwidth


def get_activities_color(activities_count):

    activities_color = {}

    min_value, max_value = get_min_max_value(activities_count)

    for ac in activities_count:
        v0 = activities_count[ac]
        """transBaseColor = int(
            255 - 100 * (v0 - min_value) / (max_value - min_value + 0.00001))
        transBaseColorHex = str(hex(transBaseColor))[2:].upper()
        v1 = "#" + transBaseColorHex + transBaseColorHex + "FF"""

        v1 = get_trans_freq_color(v0, min_value, max_value)

        activities_color[ac] = v1

    return activities_color


def graphviz_visualization(activities_count, dfg, dfg_time : Dict, image_format="png", measure="timeline",
                           max_no_of_edges_in_diagram=100000, start_activities=None, end_activities=None, soj_time=None,
                            font_size="12", bgcolor=constants.DEFAULT_BGCOLOR, stat_locale=None):
    if start_activities is None:
        start_activities = {}
    if end_activities is None:
        end_activities = {}
    if stat_locale is None:
        stat_locale = {}

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})

    '''first, remove edges in diagram that exceeds the maximum number of edges in the diagram'''
    dfg_key_value_list = []
    for edge in dfg:
        dfg_key_value_list.append([edge, dfg[edge]])

    '''More fine grained sorting to avoid that edges that are below the threshold are 
    undeterministically removed'''
    dfg_key_value_list = sorted(dfg_key_value_list, key=lambda x: (x[1], x[0][0], x[0][1]), reverse=True)
    dfg_key_value_list = dfg_key_value_list[0:min(len(dfg_key_value_list), max_no_of_edges_in_diagram)]
    dfg_allowed_keys = [x[0] for x in dfg_key_value_list]
    dfg_keys = list(dfg.keys())
    for edge in dfg_keys:
        if edge not in dfg_allowed_keys:
            del dfg[edge]

    # calculate edges penwidth
    penwidth = assign_penwidth_edges(dfg)
    activities_in_dfg = set()
    activities_count_int = copy(activities_count)

    for edge in dfg:
        activities_in_dfg.add(edge[0])
        activities_in_dfg.add(edge[1])

    # assign attributes color
    activities_color = get_activities_color(activities_count_int)

    # represent nodes
    viz.attr('node', shape='rect')

    if len(activities_in_dfg) == 0:
        activities_to_include = sorted(list(set(activities_count_int)))
    else:
        # take unique elements as a list not as a set (in this way, nodes are added in the same order to the graph)
        activities_to_include = sorted(list(set(activities_in_dfg)))


    dfg_timestamps = sorted(dfg_time.items(), key = lambda x:x[1])
    act_time_map = {}
    timestamps_to_include = []
    hash_timestamps_to_include = []

    for dfg_timestamp in dfg_timestamps:
        act = dfg_timestamp[0]
        timestamp = dfg_timestamp[1].total_seconds()
        stat = human_readable_stat(timestamp)
        if stat not in timestamps_to_include:
            viz.node(str(hash(stat)), str(stat), shape='circle', style='filled', fillcolor='pink')
            hash_timestamps_to_include.append(str(hash(stat)))
        timestamps_to_include.append(stat)
        act_time_map[act] = str(hash(stat))

    '''So far, we have created nodes for each timeline. Each node gets a unique value of the readable statistics
    a dictionary (act_time_map) is created having keys as activity and value as the hash of the stat (human readable time).
    There exists another dictionary (timestamp_hash) that has the hash value of the stat as key and an empty list as the value.
    In the next step, we fill this empty list by those activities that are repeated having the same roudned time value.
    The goal is to have a dictionary having the timestamps as keys and a list of activities as values. 
    '''

    time_act_dict = {}
    for key, value in act_time_map.items():
        if value in time_act_dict:
            time_act_dict[value].append(key)
        else:
            time_act_dict[value] = [ key ]


    ''' calculate how long each edge should be to make the edges proportional alomg the timeilne axis..'''
    minlen_list = []

    minlen_aux =[]
    [minlen_aux.append(item) for item in timestamps_to_include if item not in minlen_aux]

    for i, t in enumerate(minlen_aux[:-1]):
        int1 = int(re.search(r'\d+', minlen_aux[i]).group())
        int2 = int(re.search(r'\d+', minlen_aux[i+1]).group())
        minlen = int2 - int1
        if(minlen<1):
            minlen = 1
        minlen_list.append(minlen)


    #create edges for the timeline
    edges_in_timeline = []
    for i, t in enumerate(hash_timestamps_to_include[:-1]):
        minlen = str(minlen_list[i])
        edge = (t, hash_timestamps_to_include[i+1])
        edges_in_timeline.append(edge)
        viz.edge(edge[0],edge[1], minlen=minlen)


    '''Now we have the values that need to go on timeline and we have what activities are supposed to be aligned with what timestamp.
    Next step is calculating how long each edge should be to make the edges proportional along the timeilne axis..'''

    activities_map = {}

    #nodes get defined here 
    for act in activities_to_include:
        if "frequency" in measure and act in activities_count_int:
            viz.node(str(hash(act)), act + " (" + str(activities_count_int[act]) + ")", style='filled',
                     fillcolor=activities_color[act], fontsize=font_size)
            activities_map[act] = str(hash(act))
        else:
            stat_string = human_readable_stat(soj_time[act], stat_locale)
            viz.node(str(hash(act)), act + f" ({stat_string})", fontsize=font_size)
            activities_map[act] = str(hash(act))

    # make edges addition always in the same order
    dfg_edges = sorted(list(dfg.keys()))

    # represent edges
    for edge in dfg_edges:
        if "frequency" in measure:
            label = str(dfg[edge])
        else:
            label = human_readable_stat(dfg[edge], stat_locale)
        viz.edge(str(hash(edge[0])), str(hash(edge[1])), label=label, penwidth=str(penwidth[edge]), fontsize=font_size)

    start_activities_to_include = [act for act in start_activities if act in activities_map]
    end_activities_to_include = [act for act in end_activities if act in activities_map]

    if start_activities_to_include:
        viz.node("@@startnode", "<&#9679;>", shape='circle', fontsize="34")
        for act in start_activities_to_include:
            label = str(start_activities[act]) if isinstance(start_activities, dict) else ""
            viz.edge("@@startnode", activities_map[act], label=label, fontsize=font_size)

    if end_activities_to_include:
        viz.node("@@endnode", "<&#9632;>", shape='doublecircle', fontsize="32")
        for act in end_activities_to_include:
            label = str(end_activities[act]) if isinstance(end_activities, dict) else ""
            viz.edge(activities_map[act], "@@endnode", label=label, fontsize=font_size)


    '''Next, we create subgraphs & include those nodes which are to be aligned on the same rank. 
    Here, we include one node from the timeline axis and 1 or more nodes from the DFG. 
    We use the information of what activities are supposed to go on same level from 
    previous caluclation (i.e. we use time_Act_dict)

    We merge the dictiomaries of act_time_map with activities_map to ensure the alignment is 
    done on the activity node referencing to the same object.'''
 
    from collections import defaultdict
    dd = defaultdict(list)

    for d in (activities_map, act_time_map): # you can list as many input dicts as you want here
        for key, value in d.items():
            dd[key].append(value)


    for hash_time in hash_timestamps_to_include:
        s = Digraph(str(hash_time))
        s.attr(rank='same')
        s.node(hash_time)
        for values in time_act_dict[hash_time]:
            s.node(dd[values][0])
            try:
                s.node(dd[values][1])
            except:
                warnings.warn(dd[values])


        viz.subgraph(s)

    viz.attr(overlap='true')
    viz.format = image_format
    return viz


def apply(dfg: Dict[Tuple[str, str], int], dfg_time : Dict, log: EventLog = None, parameters: Optional[Dict[Any, Any]] = None, activities_count : Dict[str, int] = None, soj_time: Dict[str, float] = None) -> Digraph: 

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
    stat_locale = exec_utils.get_param_value(Parameters.STAT_LOCALE, parameters, {})
    if activities_count is None:
        if log is not None:
            activities_count = attr_get.get_attribute_values(log, activity_key, parameters=parameters)
        else:
            activities_count = Counter({key: 0 for key in activities})
            for el in dfg:
                activities_count[el[1]] += dfg[el]
            if isinstance(start_activities, dict):
                for act in start_activities:
                    activities_count[act] += start_activities[act]


    return graphviz_visualization(activities_count, dfg, dfg_time, image_format=image_format, measure="frequency",
                                  max_no_of_edges_in_diagram=max_no_of_edges_in_diagram,
                                  start_activities=start_activities, end_activities=end_activities, 
                                  font_size=font_size, bgcolor=bgcolor, stat_locale=stat_locale)
