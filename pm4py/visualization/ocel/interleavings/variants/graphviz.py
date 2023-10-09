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
from graphviz import Digraph
from enum import Enum

import pm4py
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any
import pandas as pd
from uuid import uuid4
from pm4py.util import vis_utils
import tempfile
from pm4py.algo.filtering.dfg import dfg_filtering


def __get_freq_perf_df(dataframe: pd.DataFrame, activity_key: str, aggregation_measure: str, activity_percentage: float,
                       paths_percentage: float, dependency_threshold: float):
    """
    Gets the frequency and performance DFG abstractions from the provided dataframe
    (internal usage)
    """
    freq_dfg, sa, ea = pm4py.discover_dfg(dataframe)
    perf_dfg, sa, ea = pm4py.discover_performance_dfg(dataframe)
    act_count = pm4py.get_event_attribute_values(dataframe, activity_key)

    freq_dfg, sa, ea, act_count = dfg_filtering.filter_dfg_on_activities_percentage(freq_dfg, sa, ea, act_count,
                                                                                    activity_percentage)
    freq_dfg, sa, ea, act_count = dfg_filtering.filter_dfg_on_paths_percentage(freq_dfg, sa, ea, act_count,
                                                                               paths_percentage)
    freq_dfg, sa, ea, act_count = dfg_filtering.filter_dfg_keep_connected(freq_dfg, sa, ea, act_count,
                                                                          dependency_threshold)

    perf_dfg = {x: y[aggregation_measure] for x, y in perf_dfg.items() if x in freq_dfg}

    return freq_dfg, perf_dfg, sa, ea, act_count


class Parameters(Enum):
    FORMAT = "format"
    BGCOLOR = "bgcolor"
    RANKDIR = "rankdir"
    ANNOTATION = "annotation"
    AGGREGATION_MEASURE = "aggregation_measure"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    ACTIVITY_PERCENTAGE = "activity_percentage"
    PATHS_PERCENTAGE = "paths_percentage"
    DEPENDENCY_THRESHOLD = "dependency_threshold"
    MIN_FACT_EDGES_INTERLEAVINGS = "min_fact_edges_interleavings"


def apply(dataframe1: pd.DataFrame, dataframe2: pd.DataFrame, interleavings: pd.DataFrame,
          parameters: Optional[Dict[Any, Any]] = None) -> Digraph:
    """
    Visualizes the interleavings discovered between two different processes.
    We suppose to provide both event logs, and the discovered interleavings.
    The visualization includes the DFG of both processes, along with the arcs discovered between them.
    Both frequency and performance visualization are available.

    Parameters
    --------------------
    dataframe1
        Dataframe of the first process
    dataframe2
        Dataframe of the second process
    interleavings
        Interleavings between the two considered processes
    parameters
        Parameters of the algorithm, including:
        - Parameters.FORMAT => the format of the visualization
        - Parameters.BGCOLOR => the background color
        - Parameters.RANKDIR => the rank direction (LR or TB; default: TB)
        - Parameters.ANNOTATION => the annotation to represent (possible values: frequency or performance)
        - Parameters.AGGREGATION_MEASURE => which aggregation should be used when considering performance
        - Parameters.ACTIVITY_KEY => the activity key
        - Parameters.ACTIVITY_PERCENTAGE => the percentage of activities to include for the DFG of the single processes
        - Parameters.PATHS_PERCENTAGE => the percentage of paths to include for the DFG of the single processes
        - Parameters.DEPENDENCY_THRESHOLD => the dependency threshold to consider for the DFG of the single processes
        - Parameters.MIN_FACT_EDGES_INTERLEAVINGS => factor that is multiplied to the minimum number of occurrences of
                                        edges in the single processes, to decide if the interleavings edge should
                                        be included. E.g., if 0.3 is provided, only interleavings edges having a frequency
                                        of at least 0.3 * MIN_EDGE_COUNT_IN_PROCESSES are included.
    Returns
    ----------------
    digraph
        Graphviz Digraph
    """
    if parameters is None:
        parameters = {}

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    bgcolor = exec_utils.get_param_value(Parameters.BGCOLOR, parameters, constants.DEFAULT_BGCOLOR)
    rankdir = exec_utils.get_param_value(Parameters.RANKDIR, parameters, constants.DEFAULT_RANKDIR_GVIZ)
    annotation = exec_utils.get_param_value(Parameters.ANNOTATION, parameters, "frequency")
    aggregation_measure = exec_utils.get_param_value(Parameters.AGGREGATION_MEASURE, parameters, "mean")
    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    activity_percentage = exec_utils.get_param_value(Parameters.ACTIVITY_PERCENTAGE, parameters, 0.3)
    paths_percentage = exec_utils.get_param_value(Parameters.PATHS_PERCENTAGE, parameters, 0.3)
    dependency_threshold = exec_utils.get_param_value(Parameters.DEPENDENCY_THRESHOLD, parameters, 0.3)
    min_fact_edges_interleavings = exec_utils.get_param_value(Parameters.MIN_FACT_EDGES_INTERLEAVINGS, parameters, 0.3)

    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    filename.close()

    viz = Digraph("interleavings", filename=filename.name, engine='dot', graph_attr={'bgcolor': bgcolor})
    viz.attr('node', shape='ellipse', fixedsize='false')

    viz.attr(rankdir=rankdir)
    viz.format = image_format.replace("html", "plain-ext")

    freq_dfg1, perf_dfg1, sa1, ea1, act_count1 = __get_freq_perf_df(dataframe1, activity_key, aggregation_measure,
                                                                    activity_percentage, paths_percentage,
                                                                    dependency_threshold)
    freq_dfg2, perf_dfg2, sa2, ea2, act_count2 = __get_freq_perf_df(dataframe2, activity_key, aggregation_measure,
                                                                    activity_percentage, paths_percentage,
                                                                    dependency_threshold)

    min_act_count = min(min(act_count1.values()), min(act_count2.values()))
    max_act_count = max(max(act_count1.values()), max(act_count2.values()))

    min_edge_count = min([min(freq_dfg1.values()), min(freq_dfg2.values())])

    interleavings_lr_frequency = interleavings[interleavings["@@direction"] == "LR"][
        ["@@source_activity", "@@target_activity"]].value_counts().to_dict()
    interleavings_lr_performance = \
    interleavings[interleavings["@@direction"] == "LR"].groupby(["@@source_activity", "@@target_activity"])[
        "@@timestamp_diff"].agg(aggregation_measure).to_dict()
    interleavings_rl_frequency = interleavings[interleavings["@@direction"] == "RL"][
        ["@@source_activity", "@@target_activity"]].value_counts().to_dict()
    interleavings_rl_performance = \
    interleavings[interleavings["@@direction"] == "RL"].groupby(["@@source_activity", "@@target_activity"])[
        "@@timestamp_diff"].agg(aggregation_measure).to_dict()

    interleavings_lr_frequency = {x: y for x, y in interleavings_lr_frequency.items() if x[0] in act_count1 and x[
        1] in act_count2 and y >= min_edge_count * min_fact_edges_interleavings}
    interleavings_rl_frequency = {x: y for x, y in interleavings_rl_frequency.items() if x[0] in act_count2 and x[
        1] in act_count1 and y >= min_edge_count * min_fact_edges_interleavings}
    interleavings_lr_performance = {x: y for x, y in interleavings_lr_performance.items() if
                                    x[0] in act_count1 and x[1] in act_count2 and x in interleavings_lr_frequency}
    interleavings_rl_performance = {x: y for x, y in interleavings_rl_performance.items() if
                                    x[0] in act_count2 and x[1] in act_count1 and x in interleavings_rl_frequency}

    min_edge_count = min([min(freq_dfg1.values()), min(freq_dfg2.values()), min(interleavings_lr_frequency.values()),
                          min(interleavings_rl_frequency.values()), min(sa1.values()), min(sa2.values()),
                          min(ea1.values()), min(ea2.values())])
    max_edge_count = max([max(freq_dfg1.values()), max(freq_dfg2.values()), max(interleavings_lr_frequency.values()),
                          max(interleavings_rl_frequency.values()), max(sa1.values()), max(sa2.values()),
                          max(ea1.values()), max(ea2.values())])

    min_edge_perf = min([min(perf_dfg1.values()), min(perf_dfg2.values()), min(interleavings_lr_performance.values()),
                         min(interleavings_rl_performance.values())])
    max_edge_perf = max([max(perf_dfg1.values()), max(perf_dfg2.values()), max(interleavings_lr_performance.values()),
                         max(interleavings_rl_performance.values())])

    nodes1 = {}
    nodes2 = {}

    with viz.subgraph(name="First Model") as c1:
        c1.attr(style='filled')
        c1.attr(color='lightgray')
        c1.attr(label="First Model")

        for act in act_count1:
            act_uuid = str(uuid4())
            nodes1[act] = act_uuid
            color = vis_utils.get_trans_freq_color(act_count1[act], min_act_count, max_act_count)
            c1.node(act_uuid, label=act + "\n" + str(act_count1[act]), shape="box", style="filled", fillcolor=color)

        for edge in freq_dfg1:
            if annotation == "frequency":
                count = freq_dfg1[edge]
                label = str(count)
                penwidth = str(vis_utils.get_arc_penwidth(count, min_edge_count, max_edge_count))
            elif annotation == "performance":
                perf = perf_dfg1[edge]
                label = vis_utils.human_readable_stat(perf)
                penwidth = str(vis_utils.get_arc_penwidth(perf, min_edge_perf, max_edge_perf))
            viz.edge(nodes1[edge[0]], nodes1[edge[1]], label=label, penwidth=penwidth)

        c1.node("@@startnode1", "<&#9679;>", shape='circle', fontsize="34", color="black", fontcolor="black")
        c1.node("@@endnode1", "<&#9632;>", shape='doublecircle', fontsize="32", color="black", fontcolor="black")

        for sa in sa1:
            penwidth = str(vis_utils.get_arc_penwidth(sa1[sa], min_edge_count, max_edge_count))
            label = str(sa1[sa]) if annotation == "frequency" else " "
            viz.edge("@@startnode1", nodes1[sa], color="black", label=label, penwidth=penwidth)

        for ea in ea1:
            penwidth = str(vis_utils.get_arc_penwidth(ea1[ea], min_edge_count, max_edge_count))
            label = str(ea1[ea]) if annotation == "frequency" else " "
            viz.edge(nodes1[ea], "@@endnode1", color="black", label=label, penwidth=penwidth)

    with viz.subgraph(name="Second Model") as c2:
        c2.attr(style='filled')
        c2.attr(color='lightgray')
        c2.attr(label="Second Model")

        for act in act_count2:
            act_uuid = str(uuid4())
            nodes2[act] = act_uuid
            color = vis_utils.get_trans_freq_color(act_count2[act], min_act_count, max_act_count)
            c2.node(act_uuid, label=act + "\n" + str(act_count2[act]), shape="box", style="filled", fillcolor=color,
                    color="gray", fontcolor="gray")

        for edge in freq_dfg2:
            if annotation == "frequency":
                count = freq_dfg2[edge]
                label = str(count)
                penwidth = str(vis_utils.get_arc_penwidth(count, min_edge_count, max_edge_count))
            elif annotation == "performance":
                perf = perf_dfg2[edge]
                label = vis_utils.human_readable_stat(perf)
                penwidth = str(vis_utils.get_arc_penwidth(perf, min_edge_perf, max_edge_perf))
            viz.edge(nodes2[edge[0]], nodes2[edge[1]], label=label, penwidth=penwidth, color="gray", fontcolor="gray")

        c2.node("@@startnode2", "<&#9679;>", shape='circle', fontsize="34", color="gray", fontcolor="gray")
        c2.node("@@endnode2", "<&#9632;>", shape='doublecircle', fontsize="32", color="gray", fontcolor="gray")

        for sa in sa2:
            penwidth = str(vis_utils.get_arc_penwidth(sa2[sa], min_edge_count, max_edge_count))
            label = str(sa2[sa]) if annotation == "frequency" else " "
            viz.edge("@@startnode2", nodes2[sa], color="gray", label=label, penwidth=penwidth)

        for ea in ea2:
            penwidth = str(vis_utils.get_arc_penwidth(ea2[ea], min_edge_count, max_edge_count))
            label = str(ea2[ea]) if annotation == "frequency" else " "
            viz.edge(nodes2[ea], "@@endnode2", color="gray", label=label, penwidth=penwidth)

    for edge in interleavings_lr_frequency:
        if annotation == "frequency":
            count = interleavings_lr_frequency[edge]
            label = str(count)
            penwidth = str(vis_utils.get_arc_penwidth(count, min_edge_count, max_edge_count))
        elif annotation == "performance":
            perf = interleavings_lr_performance[edge]
            label = vis_utils.human_readable_stat(perf)
            penwidth = str(vis_utils.get_arc_penwidth(perf, min_edge_perf, max_edge_perf))
        viz.edge(nodes1[edge[0]], nodes2[edge[1]], label=label, penwidth=penwidth, color="violet", fontcolor="violet",
                 style="dashed")

    for edge in interleavings_rl_frequency:
        if annotation == "frequency":
            count = interleavings_rl_frequency[edge]
            label = str(count)
            penwidth = str(vis_utils.get_arc_penwidth(count, min_edge_count, max_edge_count))
        elif annotation == "performance":
            perf = interleavings_rl_frequency[edge]
            label = vis_utils.human_readable_stat(perf)
            penwidth = str(vis_utils.get_arc_penwidth(perf, min_edge_perf, max_edge_perf))
        viz.edge(nodes2[edge[0]], nodes1[edge[1]], label=label, penwidth=penwidth, color="violet", fontcolor="violet",
                 style="dashed")

    return viz
