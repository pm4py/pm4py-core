__doc__ = """
We offer the possibility to export event logs (in XES or CSV files), object-centric event logs (in OCEL),
and different kinds of process models.

* Exporting traditional event logs
    * `Exporting to XES`_
    * Exporting to CSV
        Use the conversion to dataframe to convert from any log format to dataframe,
        then use Pandas to write the event log in the CSV format. Example:
        
        .. code-block:: python3
        
           import pm4py
           
           event_log = pm4py.read_xes("tests/input_data/running-example.xes")
           dataframe = pm4py.convert_to_dataframe(event_log)
           dataframe.to_csv("example.csv", index=False)

* `Exporting object-centric event logs`_
* Exporting process models
    * `Exporting Petri nets to PNML`_
    * `Exporting BPMN diagrams to BPMN 2.0`_
    * `Exporting process trees to PTML`_
    * `Exporting directly-follows graphs`_

.. _Exporting to XES: pm4py.html#pm4py.write.write_xes
.. _Exporting object-centric event logs: pm4py.html#pm4py.write.write_ocel
.. _Exporting Petri nets to PNML: pm4py.html#pm4py.write.write_pnml
.. _Exporting BPMN diagrams to BPMN 2.0: pm4py.html#pm4py.write.write_bpmn
.. _Exporting process trees to PTML: pm4py.html#pm4py.write.write_ptml
.. _Exporting directly-follows graphs: pm4py.html#pm4py.write.write_dfg
"""

import warnings

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.utils import __event_log_deprecation_warning
import pandas as pd
from typing import Union


def write_xes(log: Union[EventLog, pd.DataFrame], file_path: str) -> None:
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
    # Unit test: YES
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    from pm4py.objects.log.exporter.xes import exporter as xes_exporter
    xes_exporter.apply(log, file_path)


def write_pnml(petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, file_path: str) -> None:
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
    # Unit test: YES
    from pm4py.objects.petri_net.exporter import exporter as petri_exporter
    petri_exporter.apply(petri_net, initial_marking, file_path, final_marking=final_marking)


def write_ptml(tree: ProcessTree, file_path: str) -> None:
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
    # Unit test: YES
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
    # Unit test: YES
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
    # Unit test: YES
    if enable_layout:
        from pm4py.objects.bpmn.layout import layouter
        bpmn_graph = layouter.apply(bpmn_graph)
    from pm4py.objects.bpmn.exporter import exporter
    exporter.apply(bpmn_graph, file_path)


def write_ocel(ocel: OCEL, file_path: str, objects_path: str = None):
    """
    Stores the content of the object-centric event log to a file.
    Different formats are supported, including CSV (flat table), JSON-OCEL and XML-OCEL
    (described in the site http://www.ocel-standard.org/).

    Parameters
    -----------------
    ocel
        Object-centric event log
    file_path
        Path at which the object-centric event log should be stored
    objects_path
        (Optional, only used in CSV exporter) Path where the objects dataframe should be stored
    """
    # Unit test: YES
    if file_path.lower().endswith("csv"):
        from pm4py.objects.ocel.exporter.csv import exporter as csv_exporter
        return csv_exporter.apply(ocel, file_path, objects_path=objects_path)
    elif file_path.lower().endswith("jsonocel"):
        from pm4py.objects.ocel.exporter.jsonocel import exporter as jsonocel_exporter
        return jsonocel_exporter.apply(ocel, file_path)
    elif file_path.lower().endswith("xmlocel"):
        from pm4py.objects.ocel.exporter.xmlocel import exporter as xmlocel_exporter
        return xmlocel_exporter.apply(ocel, file_path)
