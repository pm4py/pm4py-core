__doc__ = """
We offer the possibility to import event logs (from XES or CSV files), object-centric event logs (from OCEL),
and different kinds of process models.

* Importing traditional event logs
    * `Importing from XES`_
    * Importing from CSV
* `Importing object-centric event logs`_
* Importing process models
    * `Importing Petri nets from PNML`_
    * `Importing BPMN diagrams from BPMN 2.0`_
    * `Importing process trees from PTML`_
    * `Importing directly-follows graphs`_

.. _Importing from XES: pm4py.html#pm4py.read.read_xes
.. _Importing object-centric event logs: pm4py.html#pm4py.read.read_ocel
.. _Importing Petri nets from PNML: pm4py.html#pm4py.read.read_pnml
.. _Importing BPMN diagrams from BPMN 2.0: pm4py.html#pm4py.read.read_bpmn
.. _Importing process trees from PTML: pm4py.html#pm4py.read.read_ptml
.. _Importing directly-follows graphs: pm4py.html#pm4py.read.read_dfg
"""

import warnings
from typing import Tuple

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.log.obj import EventLog
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree

INDEX_COLUMN = "@@index"


def read_xes(file_path: str, variant: str = "iterparse", **kwargs) -> EventLog:
    """
    Reads an event log in the XES standard

    Parameters
    ---------------
    file_path
        File path

    Returns
    ---------------
    log
        Event log
    """
    # Unit test: YES
    from pm4py.objects.log.importer.xes import importer as xes_importer
    v = xes_importer.Variants.ITERPARSE
    if variant == "iterparse_20":
        v = xes_importer.Variants.ITERPARSE_20
    elif variant == "iterparse_mem_compressed":
        v = xes_importer.Variants.ITERPARSE_MEM_COMPRESSED
    elif variant == "line_by_line":
        v = xes_importer.Variants.LINE_BY_LINE
    log = xes_importer.apply(file_path, variant=v, parameters=kwargs)
    return log


def read_pnml(file_path: str) -> Tuple[PetriNet, Marking, Marking]:
    """
    Reads a Petri net from the .PNML format

    Parameters
    ----------------
    file_path
        File path

    Returns
    ----------------
    petri_net
        Petri net object
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    # Unit test: YES
    from pm4py.objects.petri_net.importer import importer as pnml_importer
    net, im, fm = pnml_importer.apply(file_path)
    return net, im, fm


def read_ptml(file_path: str) -> ProcessTree:
    """
    Reads a process tree from a .ptml file

    Parameters
    ---------------
    file_path
        File path

    Returns
    ----------------
    tree
        Process tree
    """
    # Unit test: YES
    from pm4py.objects.process_tree.importer import importer as tree_importer
    tree = tree_importer.apply(file_path)
    return tree


def read_dfg(file_path: str) -> Tuple[dict, dict, dict]:
    """
    Reads a DFG from a .dfg file

    Parameters
    ------------------
    file_path
        File path

    Returns
    ------------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    # Unit test: YES
    from pm4py.objects.dfg.importer import importer as dfg_importer
    dfg, start_activities, end_activities = dfg_importer.apply(file_path)
    return dfg, start_activities, end_activities


def read_bpmn(file_path: str) -> BPMN:
    """
    Reads a BPMN from a .bpmn file

    Parameters
    ---------------
    file_path
        File path

    Returns
    ---------------
    bpmn_graph
        BPMN graph
    """
    # Unit test: YES
    from pm4py.objects.bpmn.importer import importer as bpmn_importer
    bpmn_graph = bpmn_importer.apply(file_path)
    return bpmn_graph


def read_ocel(file_path: str, objects_path: str = None) -> OCEL:
    """
    Reads an object-centric event log from a file
    (to get an explanation of what an object-centric event log is,
    you can refer to http://www.ocel-standard.org/).

    Parameters
    ----------------
    file_path
        Path from which the object-centric event log should be read.
    objects_path
        (Optional, only used in CSV exporter) Path from which the objects dataframe should be read.

    Returns
    ----------------
    ocel
        Object-centric event log
    """
    # Unit test: YES
    if file_path.lower().endswith("csv"):
        from pm4py.objects.ocel.importer.csv import importer as csv_importer
        return csv_importer.apply(file_path, objects_path=objects_path)
    elif file_path.lower().endswith("jsonocel"):
        from pm4py.objects.ocel.importer.jsonocel import importer as jsonocel_importer
        return jsonocel_importer.apply(file_path)
    elif file_path.lower().endswith("xmlocel"):
        from pm4py.objects.ocel.importer.xmlocel import importer as xmlocel_importer
        return xmlocel_importer.apply(file_path)
