import tempfile
from copy import copy

from graphviz import Digraph

from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.log.util import xes
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY
from pm4py.visualization.common.utils import *


def get_min_max_value(dfg):
    """
    Gets min and max value assigned to edges
    in DFG graph

    Parameters
    -----------
    dfg
        Directly follows graph

    Returns
    -----------
    min_value
        Minimum value in directly follows graph
    max_value
        Maximum value in directly follows graph
    """
    min_value = 9999999999
    max_value = -1

    for edge in dfg:
        if dfg[edge] < min_value:
            min_value = dfg[edge]
        if dfg[edge] > max_value:
            max_value = dfg[edge]

    return min_value, max_value


def assign_penwidth_edges(dfg):
    """
    Assign penwidth to edges in directly-follows graph

    Parameters
    -----------
    dfg
        Direcly follows graph

    Returns
    -----------
    penwidth
        Graph penwidth that edges should have in the direcly follows graph
    """
    penwidth = {}
    min_value, max_value = get_min_max_value(dfg)
    for edge in dfg:
        v0 = dfg[edge]
        v1 = get_arc_penwidth(v0, min_value, max_value)
        penwidth[edge] = str(v1)

    return penwidth


def get_activities_color(activities_count):
    """
    Get frequency color for attributes

    Parameters
    -----------
    activities_count
        Count of attributes in the log

    Returns
    -----------
    activities_color
        Color assigned to attributes in the graph
    """
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


def apply_frequency(dfg, log=None, activities_count=None, parameters=None):
    """
    Apply method (to be called from the factory method; calls the graphviz_visualization method)

    Parameters
    -----------
    dfg
        DFG graph
    log
        Event log
    activities_count
        (If provided) Dictionary that associates to each activity its count
    parameters
        Parameters passed to the algorithm (may include the format, the replay measure and the maximum number of edges
        in the diagram)
    """

    return apply(dfg, log=log, parameters=parameters, activities_count=activities_count, measure="frequency")


def apply_performance(dfg, log=None, activities_count=None, parameters=None):
    """
    Apply method (to be called from the factory method; calls the graphviz_visualization method)

    Parameters
    -----------
    dfg
        DFG graph
    log
        Event log
    activities_count
        (If provided) Dictionary that associates to each activity its count
    parameters
        Parameters passed to the algorithm (may include the format, the replay measure and the maximum number of edges
        in the diagram)
    """

    return apply(dfg, log=log, parameters=parameters, activities_count=activities_count, measure="performance")


def graphviz_visualization(activities_count, dfg, image_format="png", measure="frequency",
                           max_no_of_edges_in_diagram=75):
    """
    Do GraphViz visualization of a DFG graph

    Parameters
    -----------
    activities_count
        Count of attributes in the log (may include attributes that are not in the DFG graph)
    dfg
        DFG graph
    image_format
        GraphViz should be represented in this format
    measure
        Describes which measure is assigned to edges in direcly follows graph (frequency/performance)
    max_no_of_edges_in_diagram
        Maximum number of edges in the diagram allowed for visualization

    Returns
    -----------
    viz
        Digraph object
    """
    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("", filename=filename.name, engine='dot')

    # first, remove edges in diagram that exceeds the maximum number of edges in the diagram
    dfg_key_value_list = []
    for edge in dfg:
        dfg_key_value_list.append([edge, dfg[edge]])
    dfg_key_value_list = sorted(dfg_key_value_list, key=lambda x: x[1], reverse=True)
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
    ackeys = copy(list(activities_count_int.keys()))

    for edge in dfg:
        activities_in_dfg.add(edge[0])
        activities_in_dfg.add(edge[1])

    for act in ackeys:
        if act not in activities_in_dfg:
            del activities_count_int[act]

    # assign attributes color
    activities_color = get_activities_color(activities_count_int)

    # represent nodes
    viz.attr('node', shape='box')
    for act in activities_in_dfg:
        if "frequency" in measure:
            viz.node(act, act + " (" + str(activities_count_int[act]) + ")", style='filled',
                     fillcolor=activities_color[act])
        else:
            viz.node(act, act)

    # represent edges
    for edge in dfg:
        if "frequency" in measure:
            label = str(dfg[edge])
        else:
            label = human_readable_stat(dfg[edge])
        viz.edge(edge[0], edge[1], label=label, penwidth=str(penwidth[edge]))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = image_format

    return viz


def apply(dfg, log=None, parameters=None, activities_count=None, measure="frequency"):
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    image_format = "png"
    max_no_of_edges_in_diagram = 75

    if "format" in parameters:
        image_format = parameters["format"]
    if "maxNoOfEdgesInDiagram" in parameters:
        max_no_of_edges_in_diagram = parameters["maxNoOfEdgesInDiagram"]

    if activities_count is None:
        activities_count = attributes_filter.get_attribute_values(log, activity_key, parameters=parameters)

    return graphviz_visualization(activities_count, dfg, image_format=image_format, measure=measure,
                                  max_no_of_edges_in_diagram=max_no_of_edges_in_diagram)
