from typing import Optional, Dict, Any

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
import pandas as pd
from typing import Union


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
        Attributes that should be used to construct the dotted chart (for example, ["concept:name", "org:resource"])
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


def view_performance_spectrum(perf_spectrum: Dict[str, Any], format: str = "png"):
    """
    Displays the performance spectrum

    Parameters
    ----------------
    perf_spectrum
        Performance spectrum
    format
        Format of the visualization (png, svg ...)
    """
    from pm4py.visualization.performance_spectrum import visualizer as perf_spectrum_visualizer
    from pm4py.visualization.performance_spectrum.variants import neato
    gviz = perf_spectrum_visualizer.apply(perf_spectrum, parameters={neato.Parameters.FORMAT.value: format})
    perf_spectrum_visualizer.view(gviz)


def save_vis_performance_spectrum(perf_spectrum: Dict[str, Any], file_path: str):
    """
    Saves the visualization of the performance spectrum to a file

    Parameters
    ---------------
    perf_spectrum
        Performance spectrum
    file_path
        Destination path (including the extension)
    """
    from pm4py.visualization.performance_spectrum import visualizer as perf_spectrum_visualizer
    from pm4py.visualization.performance_spectrum.variants import neato
    format = file_path[file_path.index(".") + 1:].lower()
    gviz = perf_spectrum_visualizer.apply(perf_spectrum, parameters={neato.Parameters.FORMAT.value: format})
    perf_spectrum_visualizer.save(gviz, file_path)
