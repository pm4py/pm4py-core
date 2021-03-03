import deprecation
import pandas as pd

from pm4py.meta import VERSION
from pm4py.objects.bpmn.bpmn_graph import BPMN
from pm4py.objects.log.log import EventLog
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.process_tree.process_tree import ProcessTree


def write_xes(log: EventLog, file_path: str):
    """
    Exports a XES log

    Parameters
    --------------
    log
        Event log
    file_path
        Destination path

    Returns
    -------------
    void
    """
    from pm4py.objects.log.exporter.xes import exporter as xes_exporter
    xes_exporter.apply(log, file_path)


@deprecation.deprecated(deprecated_in="2.0.2", removed_in="3.0",
                        current_version=VERSION,
                        details="Use pandas to export CSV files")
def write_csv(log: pd.DataFrame, file_path: str):
    """
    Exports a CSV log

    Parameters
    ---------------
    log
        Event log
    file_path
        Destination path

    Returns
    --------------
    void
    """
    from pm4py.objects.conversion.log import converter
    dataframe = converter.apply(log, variant=converter.Variants.TO_DATA_FRAME)
    dataframe.to_csv(file_path, index=False)


def write_petri_net(petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, file_path: str):
    """
    Exports a (composite) Petri net object

    Parameters
    ------------
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    file_path
        Destination path

    Returns
    ------------
    void
    """
    from pm4py.objects.petri.exporter import exporter as petri_exporter
    petri_exporter.apply(petri_net, initial_marking, file_path, final_marking=final_marking)


def write_process_tree(tree: ProcessTree, file_path: str):
    """
    Exports a process tree

    Parameters
    ------------
    tree
        Process tree
    file_path
        Destination path

    Returns
    ------------
    void
    """
    from pm4py.objects.process_tree.exporter import exporter as tree_exporter
    tree_exporter.apply(tree, file_path)


def write_dfg(dfg: dict, start_activities: dict, end_activities: dict, file_path: str):
    """
    Exports a DFG

    Parameters
    -------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    file_path
        Destination path

    Returns
    ------------
    void
    """
    from pm4py.objects.dfg.exporter import exporter as dfg_exporter
    dfg_exporter.apply(dfg, file_path,
                       parameters={dfg_exporter.Variants.CLASSIC.value.Parameters.START_ACTIVITIES: start_activities,
                                   dfg_exporter.Variants.CLASSIC.value.Parameters.END_ACTIVITIES: end_activities})


def write_bpmn(bpmn_graph: BPMN, file_path: str, enable_layout: bool = True):
    """
    Writes a BPMN to a file

    Parameters
    ---------------
    bpmn_graph
        BPMN
    file_path
        Destination path
    enable_layout
        Enables the automatic layouting of the BPMN diagram (default: True)
    """
    if enable_layout:
        from pm4py.objects.bpmn.layout import layouter
        bpmn_graph = layouter.apply(bpmn_graph)
    from pm4py.objects.bpmn.exporter import exporter
    exporter.apply(bpmn_graph, file_path)
