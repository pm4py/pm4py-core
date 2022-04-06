import warnings
from typing import Tuple, Dict

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
    from pm4py.objects.process_tree.importer import importer as tree_importer
    tree = tree_importer.apply(file_path)
    return tree


def read_dfg(file_path: str) -> Tuple[Dict[Tuple[str,str],int], Dict[str,int], Dict[str,int]]:
    """
    Reads a DFG from a .dfg file.
    The DFG object returned is a triple with the following objects:
    
    1. DFG Object, encoded as a ``Dict[Tuple[str,str],int]``, s.t. ``DFG[('a','b')]=k`` implies that activity ``'a'`` is directly followed by activity ``'b'`` a total of ``k`` times in the log
    #. Start activity dictionary, encoded as a ``Dict[str,int]``, s.t., ``S['a']=k`` implies that activity ``'a'`` is starting ``k`` traces in the event log
    #. End activity dictionary, encoded as a ``Dict[str,int]``, s.t., ``E['z']=k`` implies that activity ``'z'`` is ending ``k`` traces in the event log.

    :rtype: ``Tuple[Dict[Tuple[str,str],int], Dict[str,int], Dict[str,int]]``
    :param file_path: file path of the dfg model
    

    .. code-block:: python3

       import pm4py

       dfg = pm4py.read_dfg("<path_to_dfg_file>")
    """
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
    if file_path.lower().endswith("csv"):
        from pm4py.objects.ocel.importer.csv import importer as csv_importer
        return csv_importer.apply(file_path, objects_path=objects_path)
    elif file_path.lower().endswith("jsonocel"):
        from pm4py.objects.ocel.importer.jsonocel import importer as jsonocel_importer
        return jsonocel_importer.apply(file_path)
    elif file_path.lower().endswith("xmlocel"):
        from pm4py.objects.ocel.importer.xmlocel import importer as xmlocel_importer
        return xmlocel_importer.apply(file_path)
