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
__doc__ = """
The ``pm4py.vis`` module contains the visualizations offered in ``pm4py``
"""

import os
import sys
from typing import Optional
from typing import Union, List, Dict, Any, Tuple, Set

import pandas as pd

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.powl.obj import POWL
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties
from pm4py.objects.transition_system.obj import TransitionSystem
from pm4py.objects.trie.obj import Trie
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.org.sna.obj import SNA
from pm4py.util import constants


def view_petri_net(petri_net: PetriNet, initial_marking: Optional[Marking] = None,
                   final_marking: Optional[Marking] = None, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white",
                   decorations: Dict[Any, Any] = None, debug: bool = False, rankdir: str = constants.DEFAULT_RANKDIR_GVIZ):
    """
    Views a (composite) Petri net

    :param petri_net: Petri net
    :param initial_marking: Initial marking
    :param final_marking: Final marking
    :param format: Format of the output picture (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)
    :param decorations: Decorations (color, label) associated to the elements of the Petri net
    :param debug: Boolean enabling/disabling the debug mode (show place and transition's names)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.view_petri_net(net, im, fm, format='svg')
    """
    format = str(format).lower()
    from pm4py.visualization.petri_net import visualizer as pn_visualizer
    gviz = pn_visualizer.apply(petri_net, initial_marking, final_marking,
                               parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: format, "bgcolor": bgcolor, "decorations": decorations, "debug": debug, "set_rankdir": rankdir})
    pn_visualizer.view(gviz)


def save_vis_petri_net(petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, file_path: str, bgcolor: str = "white",
                   decorations: Dict[Any, Any] = None, debug: bool = False, rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, **kwargs):
    """
    Saves a Petri net visualization to a file

    :param petri_net: Petri net
    :param initial_marking: Initial marking
    :param final_marking: Final marking
    :param file_path: Destination path
    :param bgcolor: Background color of the visualization (default: white)
    :param decorations: Decorations (color, label) associated to the elements of the Petri net
    :param debug: Boolean enabling/disabling the debug mode (show place and transition's names)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.save_vis_petri_net(net, im, fm, 'petri_net.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.petri_net import visualizer as pn_visualizer
    gviz = pn_visualizer.apply(petri_net, initial_marking, final_marking,
                               parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: format, "bgcolor": bgcolor, "decorations": decorations, "debug": debug, "set_rankdir": rankdir})
    return pn_visualizer.save(gviz, file_path)


def view_performance_dfg(dfg: dict, start_activities: dict, end_activities: dict, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW,
                         aggregation_measure="mean", bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, serv_time: Optional[Dict[str, float]] = None):
    """
    Views a performance DFG

    :param dfg: DFG object
    :param start_activities: Start activities
    :param end_activities: End activities
    :param format: Format of the output picture (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param aggregation_measure: Aggregation measure (default: mean): mean, median, min, max, sum, stdev
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)
    :param serv_time: (optional) provides the activities' service times, used to decorate the graph

    .. code-block:: python3

        import pm4py

        performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(dataframe, case_id_key='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')
        pm4py.view_performance_dfg(performance_dfg, start_activities, end_activities, format='svg')
    """
    format = str(format).lower()
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    from pm4py.visualization.dfg.variants import performance as dfg_perf_visualizer
    dfg_parameters = dfg_perf_visualizer.Parameters
    parameters = {}
    parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    parameters[dfg_parameters.AGGREGATION_MEASURE] = aggregation_measure
    parameters["bgcolor"] = bgcolor
    parameters["rankdir"] = rankdir
    gviz = dfg_perf_visualizer.apply(dfg, serv_time=serv_time, parameters=parameters)
    dfg_visualizer.view(gviz)


def save_vis_performance_dfg(dfg: dict, start_activities: dict, end_activities: dict, file_path: str,
                             aggregation_measure="mean", bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, serv_time: Optional[Dict[str, float]] = None, **kwargs):
    """
    Saves the visualization of a performance DFG

    :param dfg: DFG object
    :param start_activities: Start activities
    :param end_activities: End activities
    :param file_path: Destination path
    :param aggregation_measure: Aggregation measure (default: mean): mean, median, min, max, sum, stdev
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)
    :param serv_time: (optional) provides the activities' service times, used to decorate the graph

    .. code-block:: python3

        import pm4py

        performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(dataframe, case_id_key='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')
        pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities, 'perf_dfg.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    from pm4py.visualization.dfg.variants import performance as dfg_perf_visualizer
    dfg_parameters = dfg_perf_visualizer.Parameters
    parameters = {}
    parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    parameters[dfg_parameters.AGGREGATION_MEASURE] = aggregation_measure
    parameters["bgcolor"] = bgcolor
    parameters["rankdir"] = rankdir
    gviz = dfg_perf_visualizer.apply(dfg, serv_time=serv_time, parameters=parameters)
    return dfg_visualizer.save(gviz, file_path)


def view_dfg(dfg: dict, start_activities: dict, end_activities: dict, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white", max_num_edges: int = sys.maxsize, rankdir: str = constants.DEFAULT_RANKDIR_GVIZ):
    """
    Views a (composite) DFG

    :param dfg: DFG object
    :param start_activities: Start activities
    :param end_activities: End activities
    :param format: Format of the output picture (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)
    :param max_num_edges: maximum number of edges to represent in the graph
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        dfg, start_activities, end_activities = pm4py.discover_dfg(dataframe, case_id_key='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')
        pm4py.view_dfg(dfg, start_activities, end_activities, format='svg')
    """
    format = str(format).lower()
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    dfg_parameters = dfg_visualizer.Variants.FREQUENCY.value.Parameters
    parameters = {}
    parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    parameters["bgcolor"] = bgcolor
    parameters["rankdir"] = rankdir
    parameters["maxNoOfEdgesInDiagram"] = max_num_edges
    gviz = dfg_visualizer.apply(dfg, variant=dfg_visualizer.Variants.FREQUENCY,
                                parameters=parameters)
    dfg_visualizer.view(gviz)


def save_vis_dfg(dfg: dict, start_activities: dict, end_activities: dict, file_path: str, bgcolor: str = "white", max_num_edges: int = sys.maxsize, rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, **kwargs):
    """
    Saves a DFG visualization to a file

    :param dfg: DFG object
    :param start_activities: Start activities
    :param end_activities: End activities
    :param file_path: Destination path
    :param bgcolor: Background color of the visualization (default: white)
    :param max_num_edges: maximum number of edges to represent in the graph
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        dfg, start_activities, end_activities = pm4py.discover_dfg(dataframe, case_id_key='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')
        pm4py.save_vis_dfg(dfg, start_activities, end_activities, 'dfg.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.dfg import visualizer as dfg_visualizer
    dfg_parameters = dfg_visualizer.Variants.FREQUENCY.value.Parameters
    parameters = {}
    parameters[dfg_parameters.FORMAT] = format
    parameters[dfg_parameters.START_ACTIVITIES] = start_activities
    parameters[dfg_parameters.END_ACTIVITIES] = end_activities
    parameters["bgcolor"] = bgcolor
    parameters["rankdir"] = rankdir
    parameters["maxNoOfEdgesInDiagram"] = max_num_edges
    gviz = dfg_visualizer.apply(dfg, variant=dfg_visualizer.Variants.FREQUENCY,
                                parameters=parameters)
    return dfg_visualizer.save(gviz, file_path)


def view_process_tree(tree: ProcessTree, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ):
    """
    Views a process tree

    :param tree: Process tree
    :param format: Format of the visualization (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        process_tree = pm4py.discover_process_tree_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.view_process_tree(process_tree, format='svg')
    """
    format = str(format).lower()
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    parameters = pt_visualizer.Variants.WO_DECORATION.value.Parameters
    gviz = pt_visualizer.apply(tree, parameters={parameters.FORMAT: format, "bgcolor": bgcolor, "rankdir": rankdir})
    pt_visualizer.view(gviz)


def save_vis_process_tree(tree: ProcessTree, file_path: str, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, **kwargs):
    """
    Saves the visualization of a process tree

    :param tree: Process tree
    :param file_path: Destination path
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        process_tree = pm4py.discover_process_tree_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.save_vis_process_tree(process_tree, 'process_tree.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.process_tree import visualizer as pt_visualizer
    parameters = pt_visualizer.Variants.WO_DECORATION.value.Parameters
    gviz = pt_visualizer.apply(tree, parameters={parameters.FORMAT: format, "bgcolor": bgcolor, "rankdir": rankdir})
    return pt_visualizer.save(gviz, file_path)


def save_vis_bpmn(bpmn_graph: BPMN, file_path: str, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, variant_str: str = "classic", **kwargs):
    """
    Saves the visualization of a BPMN graph

    :param bpmn_graph: BPMN graph
    :param file_path: Destination path
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)
    :param variant_str: variant of the visualization to be used ("classic" or "dagrejs")

    .. code-block:: python3

        import pm4py

        bpmn_graph = pm4py.discover_bpmn_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.save_vis_bpmn(bpmn_graph, 'trial.bpmn')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()

    from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
    variant = None
    if variant_str == "classic":
        variant = bpmn_visualizer.Variants.CLASSIC
    elif variant_str == "dagrejs":
        variant = bpmn_visualizer.Variants.DAGREJS

    gviz = bpmn_visualizer.apply(bpmn_graph, variant=variant, parameters={"format": format, "bgcolor": bgcolor, "rankdir": rankdir})
    return bpmn_visualizer.save(gviz, file_path, variant=variant)


def view_bpmn(bpmn_graph: BPMN, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, variant_str: str = "classic"):
    """
    Views a BPMN graph

    :param bpmn_graph: BPMN graph
    :param format: Format of the visualization (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)
    :param variant_str: variant of the visualization to be used ("classic" or "dagrejs")

    .. code-block:: python3

        import pm4py

        bpmn_graph = pm4py.discover_bpmn_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.view_bpmn(bpmn_graph)
    """
    format = str(format).lower()

    from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
    variant = None
    if variant_str == "classic":
        variant = bpmn_visualizer.Variants.CLASSIC
    elif variant_str == "dagrejs":
        variant = bpmn_visualizer.Variants.DAGREJS

    gviz = bpmn_visualizer.apply(bpmn_graph, variant=variant, parameters={"format": format, "bgcolor": bgcolor, "rankdir": rankdir})
    bpmn_visualizer.view(gviz, variant=variant)


def view_heuristics_net(heu_net: HeuristicsNet, format: str = "png", bgcolor: str = "white"):
    """
    Views an heuristics net

    :param heu_net: Heuristics net
    :param format: Format of the visualization
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        heu_net = pm4py.discover_heuristics_net(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.view_heuristics_net(heu_net, format='svg')
    """
    format = str(format).lower()
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format, "bgcolor": bgcolor})
    hn_visualizer.view(gviz)


def save_vis_heuristics_net(heu_net: HeuristicsNet, file_path: str, bgcolor: str = "white", **kwargs):
    """
    Saves the visualization of an heuristics net

    :param heu_net: Heuristics net
    :param file_path: Destination path
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        heu_net = pm4py.discover_heuristics_net(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.save_vis_heuristics_net(heu_net, 'heu.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
    parameters = hn_visualizer.Variants.PYDOTPLUS.value.Parameters
    gviz = hn_visualizer.apply(heu_net, parameters={parameters.FORMAT: format, "bgcolor": bgcolor})
    return hn_visualizer.save(gviz, file_path)


def __dotted_attribute_selection(log: Union[EventLog, pd.DataFrame], attributes):
    """
    Default attribute selection for the dotted chart
    """
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)

    if attributes is None:
        from pm4py.util import xes_constants
        from pm4py.objects.log.util import sorting
        from pm4py.objects.conversion.log import converter
        log = converter.apply(log, variant=converter.Variants.TO_EVENT_LOG)
        log = sorting.sort_timestamp(log, xes_constants.DEFAULT_TIMESTAMP_KEY)
        for index, trace in enumerate(log):
            trace.attributes["@@index"] = index
        attributes = ["time:timestamp", "case:@@index", "concept:name"]
    return log, attributes


def view_dotted_chart(log: Union[EventLog, pd.DataFrame], format: str = "png", attributes=None, bgcolor: str = "white", show_legend: bool = True):
    """
    Displays the dotted chart

    The dotted chart is a classic visualization of the events inside an event log across different dimensions. Each event of the event log is corresponding to a point. The dimensions are projected on a graph having:
    - X axis: the values of the first dimension are represented there.
    - Y-axis: the values of the second dimension are represented there.
    - Color: the values of the third dimension are represented as different colors for the points of the dotted chart.

    The values can be either string, numeric or date values, and are managed accordingly by the dotted chart.
    The dotted chart can be built on different attributes. A convenient choice for the dotted chart is to visualize the distribution of cases and events over the time, with the following choices:
    - X-axis: the timestamp of the event.
    - Y-axis: the index of the case inside the event log.
    - Color: the activity of the event.

    The aforementioned choice permits to identify visually patterns such as:
    - Batches.
    - Variations in the case arrival rate.
    - Variations in the case finishing rate.

    :param log: Event log
    :param format: Image format
    :param attributes: Attributes that should be used to construct the dotted chart. If None, the default dotted chart will be shown: x-axis: time y-axis: cases (in order of occurrence in the event log) color: activity. For custom attributes, use a list of attributes of the form [x-axis attribute, y-axis attribute, color attribute], e.g., ["concept:name", "org:resource", "concept:name"])
    :param bgcolor: background color to be used in the dotted chart
    :param show_legend: boolean (enables/disables showing the legend)

    .. code-block:: python3

        import pm4py

        pm4py.view_dotted_chart(dataframe, format='svg')
        pm4py.view_dotted_chart(dataframe, attributes=['time:timestamp', 'concept:name', 'org:resource'])
    """
    format = str(format).lower()

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)

    log, attributes = __dotted_attribute_selection(log, attributes)

    parameters = {}
    parameters["format"] = format
    parameters["bgcolor"] = bgcolor
    parameters["show_legend"] = show_legend

    from pm4py.visualization.dotted_chart import visualizer as dotted_chart_visualizer
    gviz = dotted_chart_visualizer.apply(log, attributes, parameters=parameters)
    dotted_chart_visualizer.view(gviz)


def save_vis_dotted_chart(log: Union[EventLog, pd.DataFrame], file_path: str, attributes=None, bgcolor: str = "white", show_legend: bool = True, **kwargs):
    """
    Saves the visualization of the dotted chart

    The dotted chart is a classic visualization of the events inside an event log across different dimensions. Each event of the event log is corresponding to a point. The dimensions are projected on a graph having:
    - X axis: the values of the first dimension are represented there.
    - Y-axis: the values of the second dimension are represented there.
    - Color: the values of the third dimension are represented as different colors for the points of the dotted chart.

    The values can be either string, numeric or date values, and are managed accordingly by the dotted chart.
    The dotted chart can be built on different attributes. A convenient choice for the dotted chart is to visualize the distribution of cases and events over the time, with the following choices:
    - X-axis: the timestamp of the event.
    - Y-axis: the index of the case inside the event log.
    - Color: the activity of the event.

    The aforementioned choice permits to identify visually patterns such as:
    - Batches.
    - Variations in the case arrival rate.
    - Variations in the case finishing rate.

    :param log: Event log
    :param file_path: Destination path
    :param attributes: Attributes that should be used to construct the dotted chart (for example, ["concept:name", "org:resource"])
    :param bgcolor: background color to be used in the dotted chart
    :param show_legend: boolean (enables/disables showing the legend)

    .. code-block:: python3

        import pm4py

        pm4py.save_vis_dotted_chart(dataframe, 'dotted.png', attributes=['time:timestamp', 'concept:name', 'org:resource'])
    """
    file_path = str(file_path)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)

    format = os.path.splitext(file_path)[1][1:].lower()
    log, attributes = __dotted_attribute_selection(log, attributes)

    parameters = {}
    parameters["format"] = format
    parameters["bgcolor"] = bgcolor
    parameters["show_legend"] = show_legend

    from pm4py.visualization.dotted_chart import visualizer as dotted_chart_visualizer
    gviz = dotted_chart_visualizer.apply(log, attributes, parameters=parameters)
    return dotted_chart_visualizer.save(gviz, file_path)


def view_sna(sna_metric: SNA, variant_str: Optional[str] = None):
    """
    Represents a SNA metric (.html)

    :param sna_metric: Values of the metric
    :param variant_str: variant to be used (default: pyvis)

    .. code-block:: python3

        import pm4py

        metric = pm4py.discover_subcontracting_network(dataframe, resource_key='org:resource', timestamp_key='time:timestamp', case_id_key='case:concept:name')
        pm4py.view_sna(metric)
    """
    if variant_str is None:
        if constants.DEFAULT_GVIZ_VIEW == "matplotlib_view":
            variant_str = "networkx"
        else:
            variant_str = "pyvis"

    from pm4py.visualization.sna import visualizer as sna_visualizer
    variant = sna_visualizer.Variants.PYVIS
    if variant_str == "networkx":
        variant = sna_visualizer.Variants.NETWORKX
    gviz = sna_visualizer.apply(sna_metric, variant=variant)
    sna_visualizer.view(gviz, variant=variant)


def save_vis_sna(sna_metric: SNA, file_path: str, variant_str: Optional[str] = None, **kwargs):
    """
    Saves the visualization of a SNA metric in a .html file

    :param sna_metric: Values of the metric
    :param file_path: Destination path
    :param variant_str: variant to be used (default: pyvis)

    .. code-block:: python3

        import pm4py

        metric = pm4py.discover_subcontracting_network(dataframe, resource_key='org:resource', timestamp_key='time:timestamp', case_id_key='case:concept:name')
        pm4py.save_vis_sna(metric, 'sna.png')
    """
    file_path = str(file_path)

    if variant_str is None:
        if constants.DEFAULT_GVIZ_VIEW == "matplotlib_view":
            variant_str = "networkx"
        else:
            variant_str = "pyvis"

    from pm4py.visualization.sna import visualizer as sna_visualizer
    variant = sna_visualizer.Variants.PYVIS
    if variant_str == "networkx":
        variant = sna_visualizer.Variants.NETWORKX

    gviz = sna_visualizer.apply(sna_metric, variant=variant)
    return sna_visualizer.save(gviz, file_path, variant=variant)


def view_case_duration_graph(log: Union[EventLog, pd.DataFrame], format: str = "png", activity_key="concept:name", timestamp_key="time:timestamp", case_id_key="case:concept:name"):
    """
    Visualizes the case duration graph

    :param log: Log object
    :param format: Format of the visualization (png, svg, ...)
    :param activity_key: attribute to be used as activity
    :param case_id_key: attribute to be used as case identifier
    :param timestamp_key: attribute to be used as timestamp

    .. code-block:: python3

        import pm4py

        pm4py.view_case_duration_graph(dataframe, format='svg', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    format = str(format).lower()

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
        from pm4py.statistics.traces.generic.pandas import case_statistics
        graph = case_statistics.get_kde_caseduration(log, parameters=get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key))
    else:
        from pm4py.statistics.traces.generic.log import case_statistics
        graph = case_statistics.get_kde_caseduration(log, parameters=get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key))
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.CASES,
                                        parameters={"format": format})
    graphs_visualizer.view(graph_vis)


def save_vis_case_duration_graph(log: Union[EventLog, pd.DataFrame], file_path: str, activity_key="concept:name", timestamp_key="time:timestamp", case_id_key="case:concept:name", **kwargs):
    """
    Saves the case duration graph in the specified path

    :param log: Log object
    :param file_path: Destination path
    :param activity_key: attribute to be used as activity
    :param case_id_key: attribute to be used as case identifier
    :param timestamp_key: attribute to be used as timestamp

    .. code-block:: python3

        import pm4py

        pm4py.save_vis_case_duration_graph(dataframe, 'duration.png', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    file_path = str(file_path)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
        from pm4py.statistics.traces.generic.pandas import case_statistics
        graph = case_statistics.get_kde_caseduration(log, parameters=get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key))
    else:
        from pm4py.statistics.traces.generic.log import case_statistics
        graph = case_statistics.get_kde_caseduration(log, parameters=get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key))
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.CASES,
                                        parameters={"format": format})
    return graphs_visualizer.save(graph_vis, file_path)


def view_events_per_time_graph(log: Union[EventLog, pd.DataFrame], format: str = "png", activity_key="concept:name", timestamp_key="time:timestamp", case_id_key="case:concept:name"):
    """
    Visualizes the events per time graph

    :param log: Log object
    :param format: Format of the visualization (png, svg, ...)
    :param activity_key: attribute to be used as activity
    :param case_id_key: attribute to be used as case identifier
    :param timestamp_key: attribute to be used as timestamp

    .. code-block:: python3

        import pm4py

        pm4py.view_events_per_time_graph(dataframe, format='svg', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    format = str(format).lower()

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
        from pm4py.statistics.attributes.pandas import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log, parameters=get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key))
    else:
        from pm4py.statistics.attributes.log import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log, parameters=get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key))
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.DATES,
                                        parameters={"format": format})
    graphs_visualizer.view(graph_vis)


def save_vis_events_per_time_graph(log: Union[EventLog, pd.DataFrame], file_path: str, activity_key="concept:name", timestamp_key="time:timestamp", case_id_key="case:concept:name", **kwargs):
    """
    Saves the events per time graph in the specified path

    :param log: Log object
    :param file_path: Destination path
    :param activity_key: attribute to be used as activity
    :param case_id_key: attribute to be used as case identifier
    :param timestamp_key: attribute to be used as timestamp

    .. code-block:: python3

        import pm4py

        pm4py.save_vis_events_per_time_graph(dataframe, 'ev_time.png', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    file_path = str(file_path)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
        from pm4py.statistics.attributes.pandas import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log, attribute=timestamp_key, parameters=get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key))
    else:
        from pm4py.statistics.attributes.log import get as attributes_get
        graph = attributes_get.get_kde_date_attribute(log, attribute=timestamp_key, parameters=get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key))
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    graph_vis = graphs_visualizer.apply(graph[0], graph[1], variant=graphs_visualizer.Variants.DATES,
                                        parameters={"format": format})
    return graphs_visualizer.save(graph_vis, file_path)


def view_performance_spectrum(log: Union[EventLog, pd.DataFrame], activities: List[str], format: str = "png", activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", bgcolor: str = "white"):
    """
    Displays the performance spectrum

    The performance spectrum is a novel visualization of the performance of the process of the time elapsed between different activities in the process executions. The performance spectrum has initially been described in:

    Denisov, Vadim, et al. "The Performance Spectrum Miner: Visual Analytics for Fine-Grained Performance Analysis of Processes." BPM (Dissertation/Demos/Industry). 2018.

    :param perf_spectrum: Performance spectrum
    :param format: Format of the visualization (png, svg ...)
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param activity_key: attribute to be used as activity
    :param case_id_key: attribute to be used as case identifier
    :param timestamp_key: attribute to be used as timestamp
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        pm4py.view_performance_spectrum(dataframe, ['Act. A', 'Act. C', 'Act. D'], format='svg', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    format = str(format).lower()

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    properties = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    from pm4py.algo.discovery.performance_spectrum import algorithm as performance_spectrum
    perf_spectrum = performance_spectrum.apply(log, activities, parameters=properties)
    from pm4py.visualization.performance_spectrum import visualizer as perf_spectrum_visualizer
    from pm4py.visualization.performance_spectrum.variants import neato
    gviz = perf_spectrum_visualizer.apply(perf_spectrum, parameters={neato.Parameters.FORMAT.value: format, "bgcolor": bgcolor})
    perf_spectrum_visualizer.view(gviz)


def save_vis_performance_spectrum(log: Union[EventLog, pd.DataFrame], activities: List[str], file_path: str, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", bgcolor: str = "white", **kwargs):
    """
    Saves the visualization of the performance spectrum to a file

    The performance spectrum is a novel visualization of the performance of the process of the time elapsed between different activities in the process executions. The performance spectrum has initially been described in:

    Denisov, Vadim, et al. "The Performance Spectrum Miner: Visual Analytics for Fine-Grained Performance Analysis of Processes." BPM (Dissertation/Demos/Industry). 2018.

    :param log: Event log
    :param activities: List of activities (in order) that is used to build the performance spectrum
    :param file_path: Destination path (including the extension)
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        pm4py.save_vis_performance_spectrum(dataframe, ['Act. A', 'Act. C', 'Act. D'], 'perf_spec.png', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    file_path = str(file_path)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    properties = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    from pm4py.algo.discovery.performance_spectrum import algorithm as performance_spectrum
    perf_spectrum = performance_spectrum.apply(log, activities, parameters=properties)
    from pm4py.visualization.performance_spectrum import visualizer as perf_spectrum_visualizer
    from pm4py.visualization.performance_spectrum.variants import neato
    format = os.path.splitext(file_path)[1][1:].lower()
    gviz = perf_spectrum_visualizer.apply(perf_spectrum, parameters={neato.Parameters.FORMAT.value: format, "bgcolor": bgcolor})
    return perf_spectrum_visualizer.save(gviz, file_path)


def __builds_events_distribution_graph(log: Union[EventLog, pd.DataFrame], parameters, distr_type: str = "days_week"):
    """
    Internal method to build the events distribution graph
    """
    if distr_type == "days_month":
        title = "Distribution of the Events over the Days of a Month";
        x_axis = "Day of month";
        y_axis = "Number of Events"
    elif distr_type == "months":
        title = "Distribution of the Events over the Months";
        x_axis = "Month";
        y_axis = "Number of Events"
    elif distr_type == "years":
        title = "Distribution of the Events over the Years";
        x_axis = "Year";
        y_axis = "Number of Events"
    elif distr_type == "hours":
        title = "Distribution of the Events over the Hours";
        x_axis = "Hour (of day)";
        y_axis = "Number of Events"
    elif distr_type == "days_week":
        title = "Distribution of the Events over the Days of a Week";
        x_axis = "Day of the Week";
        y_axis = "Number of Events"
    elif distr_type == "weeks":
        title = "Distribution of the Events over the Weeks of a Year";
        x_axis = "Week of the Year";
        y_axis = "Number of Events"
    else:
        raise Exception("unsupported distribution specified.")

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.statistics.attributes.pandas import get as attributes_get
        x, y = attributes_get.get_events_distribution(log, distr_type=distr_type, parameters=parameters)
    else:
        from pm4py.statistics.attributes.log import get as attributes_get
        x, y = attributes_get.get_events_distribution(log, distr_type=distr_type, parameters=parameters)

    return title, x_axis, y_axis, x, y


def view_events_distribution_graph(log: Union[EventLog, pd.DataFrame], distr_type: str = "days_week", format="png", activity_key="concept:name", timestamp_key="time:timestamp", case_id_key="case:concept:name"):
    """
    Shows the distribution of the events in the specified dimension

    Observing the distribution of events over time permits to infer useful information about the work shifts, the working days, and the period of the year that are more or less busy.

    :param log: Event log
    :param distr_type: Type of distribution (default: days_week): - days_month => Gets the distribution of the events among the days of a month (from 1 to 31) - months => Gets the distribution of the events among the months (from 1 to 12) - years => Gets the distribution of the events among the years of the event log - hours => Gets the distribution of the events among the hours of a day (from 0 to 23) - days_week => Gets the distribution of the events among the days of a week (from Monday to Sunday) - weeks => Gets the distribution of the events among the weeks of a year (from 0 to 52)
    :param format: Format of the visualization (default: png)
    :param activity_key: attribute to be used as activity
    :param case_id_key: attribute to be used as case identifier
    :param timestamp_key: attribute to be used as timestamp

    .. code-block:: python3

        import pm4py

        pm4py.view_events_distribution_graph(dataframe, format='svg', distr_type='days_week', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    format = str(format).lower()

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    parameters = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
    title, x_axis, y_axis, x, y = __builds_events_distribution_graph(log, parameters, distr_type)
    parameters["title"] = title;
    parameters["x_axis"] = x_axis;
    parameters["y_axis"] = y_axis;
    parameters["format"] = format
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    gviz = graphs_visualizer.apply(x, y, variant=graphs_visualizer.Variants.BARPLOT, parameters=parameters)
    graphs_visualizer.view(gviz)


def save_vis_events_distribution_graph(log: Union[EventLog, pd.DataFrame], file_path: str,
                                       distr_type: str = "days_week", activity_key="concept:name", timestamp_key="time:timestamp", case_id_key="case:concept:name", **kwargs):
    """
    Saves the distribution of the events in a picture file

    Observing the distribution of events over time permits to infer useful information about the work shifts, the working days, and the period of the year that are more or less busy.

    :param log: Event log
    :param file_path: Destination path (including the extension)
    :param distr_type: Type of distribution (default: days_week): - days_month => Gets the distribution of the events among the days of a month (from 1 to 31) - months => Gets the distribution of the events among the months (from 1 to 12) - years => Gets the distribution of the events among the years of the event log - hours => Gets the distribution of the events among the hours of a day (from 0 to 23) - days_week => Gets the distribution of the events among the days of a week (from Monday to Sunday)
    :param activity_key: attribute to be used as activity
    :param case_id_key: attribute to be used as case identifier
    :param timestamp_key: attribute to be used as timestamp

    .. code-block:: python3

        import pm4py

        pm4py.save_vis_events_distribution_graph(dataframe, 'ev_distr_graph.png', distr_type='days_week', activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    file_path = str(file_path)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)

    format = os.path.splitext(file_path)[1][1:].lower()
    parameters = get_properties(log, activity_key=activity_key, case_id_key=case_id_key, timestamp_key=timestamp_key)
    title, x_axis, y_axis, x, y = __builds_events_distribution_graph(log, parameters, distr_type)
    parameters["title"] = title;
    parameters["x_axis"] = x_axis;
    parameters["y_axis"] = y_axis;
    parameters["format"] = format
    from pm4py.visualization.graphs import visualizer as graphs_visualizer
    gviz = graphs_visualizer.apply(x, y, variant=graphs_visualizer.Variants.BARPLOT, parameters=parameters)
    return graphs_visualizer.save(gviz, file_path)


def view_ocdfg(ocdfg: Dict[str, Any], annotation: str = "frequency", act_metric: str = "events", edge_metric="event_couples", act_threshold: int = 0, edge_threshold: int = 0, performance_aggregation: str = "mean", format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ):
    """
    Views an OC-DFG (object-centric directly-follows graph) with the provided configuration.

    Object-centric directly-follows multigraphs are a composition of directly-follows graphs for the single object type, which can be annotated with different metrics considering the entities of an object-centric event log (i.e., events, unique objects, total objects).

    :param ocdfg: Object-centric directly-follows graph
    :param annotation: The annotation to use for the visualization. Values: - "frequency": frequency annotation - "performance": performance annotation
    :param act_metric: The metric to use for the activities. Available values: - "events" => number of events (default) - "unique_objects" => number of unique objects - "total_objects" => number of total objects
    :param edge_metric: The metric to use for the edges. Available values: - "event_couples" => number of event couples (default) - "unique_objects" => number of unique objects - "total_objects" => number of total objects
    :param act_threshold: The threshold to apply on the activities frequency (default: 0). Only activities having a frequency >= than this are kept in the graph.
    :param edge_threshold: The threshold to apply on the edges frequency (default 0). Only edges having a frequency >= than this are kept in the graph.
    :param performance_aggregation: The aggregation measure to use for the performance: mean, median, min, max, sum
    :param format: The format of the output visualization (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.view_ocdfg(ocdfg, annotation='frequency', format='svg')
    """
    format = str(format).lower()

    from pm4py.visualization.ocel.ocdfg import visualizer
    from pm4py.visualization.ocel.ocdfg.variants import classic
    parameters = {}
    parameters[classic.Parameters.FORMAT] = format
    parameters[classic.Parameters.ANNOTATION] = annotation
    parameters[classic.Parameters.ACT_METRIC] = act_metric
    parameters[classic.Parameters.EDGE_METRIC] = edge_metric
    parameters[classic.Parameters.ACT_THRESHOLD] = act_threshold
    parameters[classic.Parameters.EDGE_THRESHOLD] = edge_threshold
    parameters[classic.Parameters.PERFORMANCE_AGGREGATION_MEASURE] = performance_aggregation
    parameters["bgcolor"] = bgcolor
    parameters["rankdir"] = rankdir
    gviz = classic.apply(ocdfg, parameters=parameters)
    visualizer.view(gviz)


def save_vis_ocdfg(ocdfg: Dict[str, Any], file_path: str, annotation: str = "frequency", act_metric: str = "events", edge_metric="event_couples", act_threshold: int = 0, edge_threshold: int = 0, performance_aggregation: str = "mean", bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, **kwargs):
    """
    Saves the visualization of an OC-DFG (object-centric directly-follows graph) with the provided configuration.

    Object-centric directly-follows multigraphs are a composition of directly-follows graphs for the single object type, which can be annotated with different metrics considering the entities of an object-centric event log (i.e., events, unique objects, total objects).

    :param ocdfg: Object-centric directly-follows graph
    :param file_path: Destination path (including the extension)
    :param annotation: The annotation to use for the visualization. Values: - "frequency": frequency annotation - "performance": performance annotation
    :param act_metric: The metric to use for the activities. Available values: - "events" => number of events (default) - "unique_objects" => number of unique objects - "total_objects" => number of total objects
    :param edge_metric: The metric to use for the edges. Available values: - "event_couples" => number of event couples (default) - "unique_objects" => number of unique objects - "total_objects" => number of total objects
    :param act_threshold: The threshold to apply on the activities frequency (default: 0). Only activities having a frequency >= than this are kept in the graph.
    :param edge_threshold: The threshold to apply on the edges frequency (default 0). Only edges having a frequency >= than this are kept in the graph.
    :param performance_aggregation: The aggregation measure to use for the performance: mean, median, min, max, sum
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, 'ocdfg.png', annotation='frequency')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.ocel.ocdfg import visualizer
    from pm4py.visualization.ocel.ocdfg.variants import classic
    parameters = {}
    parameters[classic.Parameters.FORMAT] = format
    parameters[classic.Parameters.ANNOTATION] = annotation
    parameters[classic.Parameters.ACT_METRIC] = act_metric
    parameters[classic.Parameters.EDGE_METRIC] = edge_metric
    parameters[classic.Parameters.ACT_THRESHOLD] = act_threshold
    parameters[classic.Parameters.EDGE_THRESHOLD] = edge_threshold
    parameters[classic.Parameters.PERFORMANCE_AGGREGATION_MEASURE] = performance_aggregation
    parameters["bgcolor"] = bgcolor
    parameters["rankdir"] = rankdir
    gviz = classic.apply(ocdfg, parameters=parameters)
    return visualizer.save(gviz, file_path)


def view_ocpn(ocpn: Dict[str, Any], format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ):
    """
    Visualizes on the screen the object-centric Petri net

    :param ocpn: Object-centric Petri net
    :param format: Format of the visualization (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        ocpn = pm4py.discover_oc_petri_net(ocel)
        pm4py.view_ocpn(ocpn, format='svg')
    """
    format = str(format).lower()

    from pm4py.visualization.ocel.ocpn import visualizer as ocpn_visualizer
    gviz = ocpn_visualizer.apply(ocpn, parameters={"format": format, "bgcolor": bgcolor, "rankdir": rankdir})
    ocpn_visualizer.view(gviz)


def save_vis_ocpn(ocpn: Dict[str, Any], file_path: str, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, **kwargs):
    """
    Saves the visualization of the object-centric Petri net into a file

    :param ocpn: Object-centric Petri net
    :param file_path: Target path of the visualization
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        ocpn = pm4py.discover_oc_petri_net(ocel)
        pm4py.save_vis_ocpn(ocpn, 'ocpn.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.ocel.ocpn import visualizer as ocpn_visualizer
    gviz = ocpn_visualizer.apply(ocpn, parameters={"format": format, "bgcolor": bgcolor, "rankdir": rankdir})
    return ocpn_visualizer.save(gviz, file_path)


def view_network_analysis(network_analysis: Dict[Tuple[str, str], Dict[str, Any]], variant: str = "frequency", format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, activity_threshold: int = 1, edge_threshold: int = 1, bgcolor: str = "white"):
    """
    Visualizes the network analysis

    :param network_analysis: Network analysis
    :param variant: Variant of the visualization: - frequency (if the discovered network analysis contains the frequency of the interactions) - performance (if the discovered network analysis contains the performance of the interactions)
    :param format: Format of the visualization (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param activity_threshold: The minimum number of occurrences for an activity to be included (default: 1)
    :param edge_threshold: The minimum number of occurrences for an edge to be included (default: 1)
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        net_ana = pm4py.discover_network_analysis(dataframe, out_column='case:concept:name', in_column='case:concept:name', node_column_source='org:resource', node_column_target='org:resource', edge_column='concept:name')
        pm4py.view_network_analysis(net_ana, format='svg')
    """
    format = str(format).lower()

    from pm4py.visualization.network_analysis import visualizer as network_analysis_visualizer
    variant = network_analysis_visualizer.Variants.PERFORMANCE if variant == "performance" else network_analysis_visualizer.Variants.FREQUENCY
    gviz = network_analysis_visualizer.apply(network_analysis, variant=variant, parameters={"format": format, "activity_threshold": activity_threshold, "edge_threshold": edge_threshold, "bgcolor": bgcolor})
    network_analysis_visualizer.view(gviz)


def save_vis_network_analysis(network_analysis: Dict[Tuple[str, str], Dict[str, Any]], file_path: str, variant: str = "frequency", activity_threshold: int = 1, edge_threshold: int = 1, bgcolor: str = "white", **kwargs):
    """
    Saves the visualization of the network analysis

    :param network_analysis: Network analysis
    :param file_path: Target path of the visualization
    :param variant: Variant of the visualization: - frequency (if the discovered network analysis contains the frequency of the interactions) - performance (if the discovered network analysis contains the performance of the interactions)
    :param activity_threshold: The minimum number of occurrences for an activity to be included (default: 1)
    :param edge_threshold: The minimum number of occurrences for an edge to be included (default: 1)
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        net_ana = pm4py.discover_network_analysis(dataframe, out_column='case:concept:name', in_column='case:concept:name', node_column_source='org:resource', node_column_target='org:resource', edge_column='concept:name')
        pm4py.save_vis_network_analysis(net_ana, 'net_ana.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.network_analysis import visualizer as network_analysis_visualizer
    variant = network_analysis_visualizer.Variants.PERFORMANCE if variant == "performance" else network_analysis_visualizer.Variants.FREQUENCY
    gviz = network_analysis_visualizer.apply(network_analysis, variant=variant, parameters={"format": format, "activity_threshold": activity_threshold, "edge_threshold": edge_threshold, "bgcolor": bgcolor})
    return network_analysis_visualizer.save(gviz, file_path)


def view_transition_system(transition_system: TransitionSystem, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white"):
    """
    Views a transition system

    :param transition_system: Transition system
    :param format: Format of the visualization (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        transition_system = pm4py.discover_transition_system(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.view_transition_system(transition_system, format='svg')
    """
    format = str(format).lower()

    from pm4py.visualization.transition_system import visualizer as ts_visualizer
    gviz = ts_visualizer.apply(transition_system, parameters={"format": format, "bgcolor": bgcolor})
    ts_visualizer.view(gviz)


def save_vis_transition_system(transition_system: TransitionSystem, file_path: str, bgcolor: str = "white", **kwargs):
    """
    Persists the visualization of a transition system

    :param transition_system: Transition system
    :param file_path: Destination path
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        transition_system = pm4py.discover_transition_system(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.save_vis_transition_system(transition_system, 'trans_system.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.transition_system import visualizer as ts_visualizer
    gviz = ts_visualizer.apply(transition_system, parameters={"format": format, "bgcolor": bgcolor})
    return ts_visualizer.save(gviz, file_path)


def view_prefix_tree(trie: Trie, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white"):
    """
    Views a prefix tree

    :param prefix_tree: Prefix tree
    :param format: Format of the visualization (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        prefix_tree = pm4py.discover_prefix_tree(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.view_prefix_tree(prefix_tree, format='svg')
    """
    format = str(format).lower()

    from pm4py.visualization.trie import visualizer as trie_visualizer
    gviz = trie_visualizer.apply(trie, parameters={"format": format, "bgcolor": bgcolor})
    trie_visualizer.view(gviz)


def save_vis_prefix_tree(trie: Trie, file_path: str, bgcolor: str = "white", **kwargs):
    """
    Persists the visualization of a prefix tree

    :param prefix_tree: Prefix tree
    :param file_path: Destination path
    :param bgcolor: Background color of the visualization (default: white)

    .. code-block:: python3

        import pm4py

        prefix_tree = pm4py.discover_prefix_tree(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        pm4py.save_vis_prefix_tree(prefix_tree, 'trie.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.trie import visualizer as trie_visualizer
    gviz = trie_visualizer.apply(trie, parameters={"format": format, "bgcolor": bgcolor})
    return trie_visualizer.save(gviz, file_path)


def view_alignments(log: Union[EventLog, pd.DataFrame], aligned_traces: List[Dict[str, Any]], format: str = "png"):
    """
    Views the alignment table as a figure

    :param log: event log
    :param aligned_traces: results of an alignment
    :param format: format of the visualization (default: png)


    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        aligned_traces = pm4py.conformance_diagnostics_alignments(log, net, im, fm)
        pm4py.view_alignments(log, aligned_traces, format='svg')
    """
    format = str(format).lower()

    from pm4py.visualization.align_table import visualizer
    gviz = visualizer.apply(log, aligned_traces, parameters={"format": format})
    visualizer.view(gviz)


def save_vis_alignments(log: Union[EventLog, pd.DataFrame], aligned_traces: List[Dict[str, Any]], file_path: str, **kwargs):
    """
    Saves an alignment table's figure in the disk

    :param log: event log
    :param aligned_traces: results of an alignment
    :param file_path: target path in the disk

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        aligned_traces = pm4py.conformance_diagnostics_alignments(log, net, im, fm)
        pm4py.save_vis_alignments(log, aligned_traces, 'output.svg')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.align_table import visualizer
    gviz = visualizer.apply(log, aligned_traces, parameters={"format": format})
    return visualizer.save(gviz, file_path)


def view_footprints(footprints: Union[Tuple[Dict[str, Any], Dict[str, Any]], Dict[str, Any]], format: str = "png"):
    """
    Views the footprints as a figure

    :param footprints: footprints
    :param format: format of the visualization (default: png)

     .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        fp_log = pm4py.discover_footprints(log)
        pm4py.view_footprints(fp_log, format='svg')
    """
    format = str(format).lower()

    from pm4py.visualization.footprints import visualizer as fps_visualizer

    if isinstance(footprints, dict):
        gviz = fps_visualizer.apply(footprints, parameters={"format": format})
    else:
        gviz = fps_visualizer.apply(footprints[0], footprints[1], variant=fps_visualizer.Variants.COMPARISON_SYMMETRIC, parameters={"format": format})

    fps_visualizer.view(gviz)


def save_vis_footprints(footprints: Union[Tuple[Dict[str, Any], Dict[str, Any]], Dict[str, Any]], file_path: str, **kwargs):
    """
    Saves the footprints' visualization on disk

    :param footprints: footprints
    :param file_path: target path of the visualization

     .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        fp_log = pm4py.discover_footprints(log)
        pm4py.save_vis_footprints(fp_log, 'output.svg')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()

    from pm4py.visualization.footprints import visualizer as fps_visualizer

    if isinstance(footprints, dict):
        gviz = fps_visualizer.apply(footprints, parameters={"format": format})
    else:
        gviz = fps_visualizer.apply(footprints[0], footprints[1], variant=fps_visualizer.Variants.COMPARISON_SYMMETRIC, parameters={"format": format})

    return fps_visualizer.save(gviz, file_path)


def view_powl(powl: POWL, format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white", variant_str: str = "basic"):
    """
    Perform a visualization of a POWL model.

    Reference paper:
    Kourani, Humam, and Sebastiaan J. van Zelst. "POWL: partially ordered workflow language." International Conference on Business Process Management. Cham: Springer Nature Switzerland, 2023.

    :param powl: POWL model
    :param format: format of the visualization (default: png)
    :param bgcolor: background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)
    :param variant_str: variant of the visualization to be used (values: "basic", "net")

     .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        powl_model = pm4py.discover_powl(log)
        pm4py.view_powl(powl_model, format='svg', variant_str='basic')
        pm4py.view_powl(powl_model, format='svg', variant_str='net')
    """
    from pm4py.visualization.powl.visualizer import POWLVisualizationVariants
    variant = POWLVisualizationVariants.BASIC

    if variant_str == "basic":
        variant = POWLVisualizationVariants.BASIC
    elif variant_str == "net":
        variant = POWLVisualizationVariants.NET

    format = str(format).lower()
    parameters = parameters={"format": format, "bgcolor": bgcolor}

    from pm4py.visualization.powl import visualizer as powl_visualizer
    gviz = powl_visualizer.apply(powl, variant=variant, parameters=parameters)

    powl_visualizer.view(gviz, parameters=parameters)


def save_vis_powl(powl: POWL, file_path: str, bgcolor: str = "white", rankdir: str = "TB", **kwargs):
    """
    Saves the visualization of a POWL model.

    Reference paper:
    Kourani, Humam, and Sebastiaan J. van Zelst. "POWL: partially ordered workflow language." International Conference on Business Process Management. Cham: Springer Nature Switzerland, 2023.

    :param powl: POWL model
    :param file_path: target path of the visualization
    :param bgcolor: background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

     .. code-block:: python3

        import pm4py

        log = pm4py.read_xes('tests/input_data/running-example.xes')
        powl_model = pm4py.discover_powl(log)
        pm4py.save_vis_powl(powl_model, 'powl.png')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    parameters = {"format": format, "bgcolor": bgcolor, "rankdir": rankdir}

    from pm4py.visualization.powl import visualizer as powl_visualizer
    gviz = powl_visualizer.apply(powl, parameters=parameters)

    return powl_visualizer.save(gviz, file_path, parameters=parameters)


def view_object_graph(ocel: OCEL, graph: Set[Tuple[str, str]], format: str = constants.DEFAULT_FORMAT_GVIZ_VIEW, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ):
    """
    Visualizes an object graph on the screen

    :param ocel: object-centric event log
    :param graph: object graph
    :param format: format of the visualization (if html is provided, GraphvizJS is used to render the visualization in an HTML page)
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        obj_graph = pm4py.ocel_discover_objects_graph(ocel, graph_type='object_interaction')
        pm4py.view_object_graph(ocel, obj_graph, format='svg')
    """
    format = str(format).lower()

    from pm4py.visualization.ocel.object_graph import visualizer as obj_graph_vis
    gviz = obj_graph_vis.apply(ocel, graph, parameters={"format": format, "bgcolor": bgcolor, "rankdir": rankdir})
    obj_graph_vis.view(gviz)


def save_vis_object_graph(ocel: OCEL, graph: Set[Tuple[str, str]], file_path: str, bgcolor: str = "white", rankdir: str = constants.DEFAULT_RANKDIR_GVIZ, **kwargs):
    """
    Saves the visualization of an object graph

    :param ocel: object-centric event log
    :param graph: object graph
    :param file_path: Destination path
    :param bgcolor: Background color of the visualization (default: white)
    :param rankdir: sets the direction of the graph ("LR" for left-to-right; "TB" for top-to-bottom)

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel('trial.ocel')
        obj_graph = pm4py.ocel_discover_objects_graph(ocel, graph_type='object_interaction')
        pm4py.save_vis_object_graph(ocel, obj_graph, 'trial.pdf')
    """
    file_path = str(file_path)
    format = os.path.splitext(file_path)[1][1:].lower()
    from pm4py.visualization.ocel.object_graph import visualizer as obj_graph_vis
    gviz = obj_graph_vis.apply(ocel, graph, parameters={"format": format, "bgcolor": bgcolor, "rankdir": rankdir})
    return obj_graph_vis.save(gviz, file_path)
