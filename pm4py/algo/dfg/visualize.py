from graphviz import Digraph
import tempfile, os
import base64
from copy import deepcopy, copy

MAX_EDGE_PENWIDTH_GRAPHVIZ = 2.6
MIN_EDGE_PENWIDTH_GRAPHVIZ = 1.0

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
        v1 = MIN_EDGE_PENWIDTH_GRAPHVIZ + (MAX_EDGE_PENWIDTH_GRAPHVIZ - MIN_EDGE_PENWIDTH_GRAPHVIZ) * (
                    v0 - min_value) / (max_value - min_value + 0.00001)
        penwidth[edge] = str(v1)

    return penwidth

def get_activities_color(activities_count):
    """
    Get frequency color for activities

    Parameters
    -----------
    activities_count
        Count of activities in the log

    Returns
    -----------
    activities_color
        Color assigned to activities in the graph
    """
    activities_color = {}

    min_value, max_value = get_min_max_value(activities_count)

    for ac in activities_count:
        v0 = activities_count[ac]
        transBaseColor = int(
            255 - 100 * (v0 - min_value) / (max_value - min_value + 0.00001))
        transBaseColorHex = str(hex(transBaseColor))[2:].upper()
        v1 = "#" + transBaseColorHex + transBaseColorHex + "FF"

        activities_color[ac] = v1

    return activities_color

def graphviz_visualization(activities_count, dfg, format="pdf", measure="frequency"):
    """
    Do GraphViz visualization of a DFG graph

    Parameters
    -----------
    activities_count
        Count of activities in the log (may include activities that are not in the DFG graph
    dfg
        DFG graph
    format
        GraphViz should be represented in this format
    measure
        Describes hich measure is assigned to edges in direcly follows graph (frequency/performance)

    Returns
    -----------
    viz
        Digraph object
    """
    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("", filename=filename.name, engine='dot')
    penwidth = assign_penwidth_edges(dfg)
    activities_in_dfg = set()
    activities_count_int = copy(activities_count)
    ackeys = copy(list(activities_count_int.keys()))

    for edge in dfg:
        activities_in_dfg.add(edge[0])
        activities_in_dfg.add(edge[1])

    for act in ackeys:
        if not act in activities_in_dfg:
            del activities_count_int[act]

    activities_color = get_activities_color(activities_count_int)

    viz.attr('node', shape='box')
    for act in activities_in_dfg:
        if measure == "frequency":
            viz.node(act, act + " ("+str(activities_count_int[act])+")", style='filled', fillcolor=activities_color[act])
        else:
            viz.node(act, act)

    for edge in dfg:
        if measure == "frequency":
            label = str(dfg[edge])
        else:
            label = str(dfg[edge])
        viz.edge(edge[0], edge[1], label=str(dfg[edge]), penwidth=str(penwidth[edge]))

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = format

    return viz

def return_diagram_as_base64(activities_count, dfg, format="svg", measure="frequency"):
    """
    Return process model in Base64 format

    Parameters
    -----------
    activities_count
        Count of activities in the log (may include activities that are not in the DFG graph
    dfg
        DFG graph
    format
        GraphViz should be represented in this format
    measure
        Describes hich measure is assigned to edges in direcly follows graph (frequency/performance)

    Returns
    -----------
    string
    """

    graphviz = graphviz_visualization(activities_count, dfg, format=format, measure="frequency")
    render = graphviz.render(view=False)
    with open(render, "rb") as f:
        return base64.b64encode(f.read())