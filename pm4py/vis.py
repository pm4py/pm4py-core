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
from typing import Optional, Dict, Any, List

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
import pandas as pd
from typing import Union, List
from pm4py.util.pandas_utils import check_is_dataframe, check_dataframe_columns


def view_petri_net(petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, format: str = "png"):
    """
    Views a (composite) Petri net

    Parameters
    -------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final marking
        Final marking
    format
        Format of the output picture (default: png)
    """
    from pm4py.visualization.petri_net import visualizer as pn_visualizer
    gviz = pn_visualizer.apply(petri_net, initial_marking, final_marking,
                               parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: format})
    pn_visualizer.view(gviz)


def save_vis_petri_net(petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, file_path: str):
    """
    Saves a Petri net visualization to a file

    Parameters
    --------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final marking
        Final marking
    file_path
        Destination path
    """
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.petri_net import visualizer as pn_visualizer
    gviz = pn_visualizer.apply(petri_net, initial_marking, final_marking,
                               parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: format})
    pn_visualizer.save(gviz, file_path)


def view_dfg(dfg: dict, start_activities: dict, end_activities: dict, format: str = "png",
             log: Optional[EventLog] = None):
    """
    Views a (composite) DFG

    Parameters
    -------------
    dfg
        DFG object
    start_activities
        Start activities
    end_activities
        End activities
    format
        Format of the output picture (default: png)
    """
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    parameters = dfg_visualizer.Variants.FREQUENCY.value.Parameters
    gviz = dfg_visualizer.apply(dfg, log=log, variant=dfg_visualizer.Variants.FREQUENCY,
                                parameters={parameters.FORMAT: format,
                                            parameters.START_ACTIVITIES: start_activities,
                                            parameters.END_ACTIVITIES: end_activities})
    dfg_visualizer.view(gviz)


def save_vis_dfg(dfg: dict, start_activities: dict, end_activities: dict, file_path: str,
                 log: Optional[EventLog] = None):
    """
    Saves a DFG visualization to a file

    Parameters
    --------------
    dfg
        DFG object
    start_activities
        Start activities
    end_activities
        End activities
    file_path
        Destination path
    """
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    parameters = dfg_visualizer.Variants.FREQUENCY.value.Parameters
    gviz = dfg_visualizer.apply(dfg, log=log, variant=dfg_visualizer.Variants.FREQUENCY,
                                parameters={parameters.FORMAT: format,
                                            parameters.START_ACTIVITIES: start_activities,
                                            parameters.END_ACTIVITIES: end_activities})
    dfg_visualizer.save(gviz, file_path)


def view_process_tree(tree: ProcessTree, format: str = "png"):
    """
    Views a process tree

    Parameters
    ---------------
    tree
        Process tree
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    parameters = pt_visualizer.Variants.WO_DECORATION.value.Parameters
    gviz = pt_visualizer.apply(tree, parameters={parameters.FORMAT: format})
    pt_visualizer.view(gviz)


def save_vis_process_tree(tree: ProcessTree, file_path: str):
    """
    Saves the visualization of a process tree

    Parameters
    ---------------
    tree
        Process tree
    file_path
        Destination path
    """
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    parameters = pt_visualizer.Variants.WO_DECORATION.value.Parameters
    gviz = pt_visualizer.apply(tree, parameters={parameters.FORMAT: format})
    pt_visualizer.save(gviz, file_path)


def save_vis_bpmn(bpmn_graph: BPMN, file_path: str):
    """
    Saves the visualization of a BPMN graph

    Parameters
    --------------
    bpmn_graph
        BPMN graph
    file_path
        Destination path
    """
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
    parameters = bpmn_visualizer.Variants.CLASSIC.value.Parameters
    gviz = bpmn_visualizer.apply(bpmn_graph, parameters={parameters.FORMAT: format})
    bpmn_visualizer.save(gviz, file_path)


def view_bpmn(bpmn_graph: BPMN, format: str = "png"):
    """
    Views a BPMN graph

    Parameters
    ---------------
    bpmn_graph
        BPMN graph
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
    parameters = bpmn_visualizer.Variants.CLASSIC.value.Parameters
    gviz = bpmn_visualizer.apply(bpmn_graph, parameters={parameters.FORMAT: format})
    bpmn_visualizer.view(gviz)


def view_heuristics_net(heu_net: HeuristicsNet, format: str = "png"):
    """
    Views an heuristics net

    Parameters
    --------------
    heu_net
        Heuristics net
    format
        Format of the visualization (default: png)
    """
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format})
    hn_visualizer.view(gviz)


def save_vis_heuristics_net(heu_net: HeuristicsNet, file_path: str):
    """
    Saves the visualization of an heuristics net

    Parameters
    --------------
    heu_net
        Heuristics nte
    file_path
        Destination path
    """
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format})
    hn_visualizer.save(gviz, file_path)


def __dotted_attribute_selection(log, attributes):
    """
    Default attribute selection for the dotted chart

    Parameters
    -----------------
    log
        Event log

    Returns
    -----------------
    attributes
        List of attributes
    """
    if attributes is None:
        from pm4py.util import xes_constants
        from pm4py.objects.log.util import sorting
        from pm4py.convert import convert_to_event_log
        log = convert_to_event_log(log)
        log = sorting.sort_timestamp(log, xes_constants.DEFAULT_TIMESTAMP_KEY)
        for index, trace in enumerate(log):
            trace.attributes["@@index"] = index
        attributes = ["time:timestamp", "case:@@index", "concept:name"]
    return log, attributes


def view_dotted_chart(log, format: str = "png", attributes=None):
    """
    Displays the dotted chart

    Parameters
    -----------------
    log
        Event log
    format
        Image format
    attributes
        Attributes that should be used to construct the dotted chart.
        If None, the default dotted chart will be shown:
            x-axis: time
            y-axis: cases (in order of occurrence in the event log)
            color: activity
        For custom attributes, use a list of attributes
        of the form [x-axis attribute, y-axis attribute, color attribute], e.g., ["concept:name", "org:resource", "concept:name"])

    """
    log, attributes = __dotted_attribute_selection(log, attributes)
    from pm4py.visualization.dotted_chart import visualizer as dotted_chart_visualizer
    gviz = dotted_chart_visualizer.apply(log, attributes, parameters={"format": format})
    dotted_chart_visualizer.view(gviz)


def save_vis_dotted_chart(log, file_path: str, attributes=None):
    """
    Saves the visualization of the dotted chart

    Parameters
    -----------------
    log
        Event log
    file_path
        Destination path
    attributes
        Attributes that should be used to construct the dotted chart (for example, ["concept:name", "org:resource"])
    """
    format = file_path[file_path.index(".") + 1:].lower()
    log, attributes = __dotted_attribute_selection(log, attributes)
    from pm4py.visualization.dotted_chart import visualizer as dotted_chart_visualizer
    gviz = dotted_chart_visualizer.apply(log, attributes, parameters={"format": format})
    dotted_chart_visualizer.save(gviz, file_path)


def view_sna(sna_metric):
    """
    Represents a SNA metric (.html)

    Parameters
    ---------------
    sna_metric
        Values of the metric
    """
    from pm4py.visualization.sna import visualizer as sna_visualizer
    gviz = sna_visualizer.apply(sna_metric, variant=sna_visualizer.Variants.PYVIS)
    sna_visualizer.view(gviz)


def save_vis_sna(sna_metric, file_path: str):
    """
    Saves the visualization of a SNA metric in a .html file

    Parameters
    ----------------
    sna_metric
        Values of the metric
    file_path
        Destination path
    """
    from pm4py.visualization.sna import visualizer as sna_visualizer
    gviz = sna_visualizer.apply(sna_metric, variant=sna_visualizer.Variants.PYVIS)
    sna_visualizer.save(gviz, file_path)


def view_case_duration_graph(log: Union[EventLog, pd.DataFrame], format: str = "png"):
    """
    Visualizes the case duration graph

    Parameters
    -----------------
    log
        Log object
    format
        Format of the visualization (png, svg, ...)
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.traces.pandas import case_statistics
        graph = case_statistics.get_kde_caseduration(log)
    else:
        from pm4py.statistics.traces.log import case_statistics
        graph = case_statistics.get_kde_caseduration(log)
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.CASES,
                                          parameters={"format": format})
    graphs_visualizer.view(graph_vis)


def save_vis_case_duration_graph(log: Union[EventLog, pd.DataFrame], file_path: str):
    """
    Saves the case duration graph in the specified path

    Parameters
    ----------------
    log
        Log object
    file_path
        Destination path
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.traces.pandas import case_statistics
        graph = case_statistics.get_kde_caseduration(log)
    else:
        from pm4py.statistics.traces.log import case_statistics
        graph = case_statistics.get_kde_caseduration(log)
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.CASES,
                                          parameters={"format": format})
    graphs_visualizer.save(graph_vis, file_path)


def view_events_per_time_graph(log: Union[EventLog, pd.DataFrame], format: str = "png"):
    """
    Visualizes the events per time graph

    Parameters
    -----------------
    log
        Log object
    format
        Format of the visualization (png, svg, ...)
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log)
    else:
        from pm4py.statistics.attributes.log import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log)
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.DATES,
                                          parameters={"format": format})
    graphs_visualizer.view(graph_vis)


def save_vis_events_per_time_graph(log: Union[EventLog, pd.DataFrame], file_path: str):
    """
    Saves the events per time graph in the specified path

    Parameters
    ----------------
    log
        Log object
    file_path
        Destination path
    """
    if check_is_dataframe(log):
        check_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log)
    else:
        from pm4py.statistics.attributes.log import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log)
    format = file_path[file_path.index(".") + 1:].lower()
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.DATES,
                                          parameters={"format": format})
    graphs_visualizer.save(graph_vis, file_path)


def view_performance_spectrum(log: Union[EventLog, pd.DataFrame], activities: List[str], format: str = "png"):
    """
    Displays the performance spectrum

    Parameters
    ----------------
    perf_spectrum
        Performance spectrum
    format
        Format of the visualization (png, svg ...)
    """
    from pm4py.algo.discovery.performance_spectrum import algorithm as performance_spectrum
    perf_spectrum = performance_spectrum.apply(log, activities)
    from pm4py.visualization.performance_spectrum import visualizer as perf_spectrum_visualizer
    from pm4py.visualization.performance_spectrum.variants import neato
    gviz = perf_spectrum_visualizer.apply(perf_spectrum, parameters={neato.Parameters.FORMAT.value: format})
    perf_spectrum_visualizer.view(gviz)


def save_vis_performance_spectrum(log: Union[EventLog, pd.DataFrame], activities: List[str], file_path: str):
    """
    Saves the visualization of the performance spectrum to a file

    Parameters
    ---------------
    log
        Event log
    activities
        List of activities (in order) that is used to build the performance spectrum
    file_path
        Destination path (including the extension)
    """
    from pm4py.algo.discovery.performance_spectrum import algorithm as performance_spectrum
    perf_spectrum = performance_spectrum.apply(log, activities)
    from pm4py.visualization.performance_spectrum import visualizer as perf_spectrum_visualizer
    from pm4py.visualization.performance_spectrum.variants import neato
    format = file_path[file_path.index(".") + 1:].lower()
    gviz = perf_spectrum_visualizer.apply(perf_spectrum, parameters={neato.Parameters.FORMAT.value: format})
    perf_spectrum_visualizer.save(gviz, file_path)
