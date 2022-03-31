__doc__ = """
``pm4py`` supports reading various different file formats:

* ``.bpmn`` files; File format specifying process models in the *BPMN* process modeling formalism

    

* ``.dfg`` files; File format specifying *directly follows graphs* (also referred to as *process maps*)

    .. code-block:: python3

        import pm4py

        dfg = pm4py.read_dfg('<path_to_dfg_file>')

* ``.xes`` files; General interchange format for event data.
    
    .. code-block:: python3
        
        import pm4py

        df = pm4py.read_xes('<path_to_xes_file>')
        
* ``.ocel`` files; Novel data format (under development) for multi-dimensional event data.

Both file formats are internally converted to ``pandas dataframes`` (`docs <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html>`_), which are the default data structure used by all algorithms implemented in ``pm4py``.

Additional file formats that are supported are:



* ``.pnml`` files; File format specifying *Petri net* models
* ``.ptml`` files; File format specifying *Process Tree* models


* Importing traditional event logs
    * `Importing from XES`_
    * Importing from CSV
        Import the dataframe using Pandas, and then use the `method to assign a proper column mapping`_. Example:
        
        .. code-block:: python3
        
           import pandas as pd
           import pm4py
        
           dataframe = pm4py.read_csv("tests/input_data/running-example.csv")
           dataframe = pm4py.format_dataframe(dataframe, case_id_column='case:concept:name', activity_column='concept:name', timestamp_column='time:timestamp')
        
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
.. _Importing directly-follows graphs: pm4py.html#pm4py.read.read_dfg
.. _method to assign a proper column mapping: pm4py.html#pm4py.utils.format_dataframe
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
    """This is a module documentation

    Use this module like this:

    .. code-block:: python

    res = aFunction(something, goes, in)
    print(res.avalue)

    Reads an event log in the XES standard.

    Example:

    .. code-block:: python3

       import pm4py

       log = pm4py.read_xes("tests/input_data/running-example.xes")
       pm4py.write_xes("example.xes")

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

    Example:

    .. code-block:: python3

       import pm4py

       net, im, fm = pm4py.read_pnml("tests/input_data/running-example.pnml")
       pm4py.write_pnml(net, im, fm, "example.pnml")

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

    Example:

    .. code-block:: python3

       import pm4py

       process_tree = pm4py.read_ptml("tests/input_data/running-example.ptml")
       pm4py.write_ptml(process_tree, "example.ptml")

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

    :rtype: Tuple[dict, dict, dict]
    :param file_path: file path of the dfg model
    

    .. code-block:: python3

       import pm4py

       dfg = pm4py.read_dfg("<path_to_dfg_file>")
    """
    # Unit test: YES
    from pm4py.objects.dfg.importer import importer as dfg_importer
    dfg, start_activities, end_activities = dfg_importer.apply(file_path)
    return dfg, start_activities, end_activities


def read_bpmn(file_path: str) -> BPMN:
    """
    Reads a BPMN model from a .bpmn file

    :param file_path: file path of the bpmn model

    .. code-block:: python3

        import pm4py

        bpmn = pm4py.read_bpmn('<path_to_bpmn_file>')

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

    Example:

    .. code-block:: python3

       import pm4py

       ocel = pm4py.read_ocel("tests/input_data/ocel/example_log.jsonocel")
       pm4py.write_ocel(ocel, "example.ocel")


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
