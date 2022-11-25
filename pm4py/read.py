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
import warnings
from typing import Tuple, Dict, Optional

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.log.obj import EventLog
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.conversion.log import converter as log_converter

import os

from pandas import DataFrame
import pkgutil
import deprecation

INDEX_COLUMN = "@@index"

__doc__ = """
The ``pm4py.read`` module contains all funcationality related to reading files/objects from disk.
"""


def read_xes(file_path: str, variant: str = "chunk_regex", **kwargs) -> DataFrame:
    """
    Reads an event log stored in XES format (see `xes-standard <https://xes-standard.org/>`_)
    Returns a table (``pandas.DataFrame``) view of the event log.

    :param file_path: file path of the event log (``.xes`` file) on disk
    :param variant: the variant of the importer to use. "iterparse" => traditional XML parser; "line_by_line" => text-based line-by-line importer ; "chunk_regex" => chunk-of-bytes importer (default); "iterparse20" => XES 2.0 importer
    :rtype: ``DataFrame``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("<path_to_xes_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.log.importer.xes import importer as xes_importer
    v = xes_importer.Variants.LINE_BY_LINE
    if pkgutil.find_loader("lxml"):
        v = xes_importer.Variants.ITERPARSE
    if variant == "iterparse_20":
        v = xes_importer.Variants.ITERPARSE_20
    elif variant == "iterparse_mem_compressed":
        v = xes_importer.Variants.ITERPARSE_MEM_COMPRESSED
    elif variant == "line_by_line":
        v = xes_importer.Variants.LINE_BY_LINE
    elif variant == "chunk_regex":
        v = xes_importer.Variants.CHUNK_REGEX
    log = xes_importer.apply(file_path, variant=v, parameters=kwargs)
    log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)
    return log


def read_pnml(file_path: str, auto_guess_final_marking: bool = False) -> Tuple[PetriNet, Marking, Marking]:
    """
    Reads a Petri net object from a .pnml file.
    The Petri net object returned is a triple containing the following objects:
    
    1. Petrinet Object, encoded as a ``PetriNet`` class
    #. Initial Marking
    #. Final Marking

    :rtype: ``Tuple[PetriNet, Marking, Marking]``
    :param file_path: file path of the Petri net model (``.pnml`` file) on disk

    .. code-block:: python3

        import pm4py

        pn = pm4py.read_pnml("<path_to_pnml_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.petri_net.importer import importer as pnml_importer
    net, im, fm = pnml_importer.apply(file_path, parameters={"auto_guess_final_marking": auto_guess_final_marking})
    return net, im, fm


def read_ptml(file_path: str) -> ProcessTree:
    """
    Reads a process tree object from a .ptml file

    :param file_path: file path of the process tree object on disk
    :rtype: ``ProcessTree``

    .. code-block:: python3

        import pm4py

        process_tree = pm4py.read_ptml("<path_to_ptml_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.process_tree.importer import importer as tree_importer
    tree = tree_importer.apply(file_path)
    return tree


def read_dfg(file_path: str) -> Tuple[Dict[Tuple[str,str],int], Dict[str,int], Dict[str,int]]:
    """
    Reads a DFG object from a .dfg file.
    The DFG object returned is a triple containing the following objects:
    
    1. DFG Object, encoded as a ``Dict[Tuple[str,str],int]``, s.t. ``DFG[('a','b')]=k`` implies that activity ``'a'`` is directly followed by activity ``'b'`` a total of ``k`` times in the log
    #. Start activity dictionary, encoded as a ``Dict[str,int]``, s.t., ``S['a']=k`` implies that activity ``'a'`` is starting ``k`` traces in the event log
    #. End activity dictionary, encoded as a ``Dict[str,int]``, s.t., ``E['z']=k`` implies that activity ``'z'`` is ending ``k`` traces in the event log.

    :rtype: ``Tuple[Dict[Tuple[str,str],int], Dict[str,int], Dict[str,int]]``
    :param file_path: file path of the dfg model on disk
    

    .. code-block:: python3

       import pm4py

       dfg = pm4py.read_dfg("<path_to_dfg_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.dfg.importer import importer as dfg_importer
    dfg, start_activities, end_activities = dfg_importer.apply(file_path)
    return dfg, start_activities, end_activities


def read_bpmn(file_path: str) -> BPMN:
    """
    Reads a BPMN model from a .bpmn file

    :param file_path: file path of the bpmn model
    :rtype: ``BPMN``

    .. code-block:: python3

        import pm4py

        bpmn = pm4py.read_bpmn('<path_to_bpmn_file>')

    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.bpmn.importer import importer as bpmn_importer
    bpmn_graph = bpmn_importer.apply(file_path)
    return bpmn_graph

@deprecation.deprecated("2.3.0", "3.0.0", "the read_ocel function is deprecated and replaced by read_ocel_csv, read_ocel_json and read_ocel_xml, respectively")
def read_ocel(file_path: str, objects_path: Optional[str] = None) -> OCEL:
    """
    Reads an object-centric event log from a file (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the object-centric event log
    :param objects_path: [Optional] file path from which the objects dataframe should be read
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel("<path_to_ocel_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    if file_path.lower().endswith("csv"):
        from pm4py.objects.ocel.importer.csv import importer as csv_importer
        return csv_importer.apply(file_path, objects_path=objects_path)
    elif file_path.lower().endswith("jsonocel"):
        from pm4py.objects.ocel.importer.jsonocel import importer as jsonocel_importer
        return jsonocel_importer.apply(file_path)
    elif file_path.lower().endswith("xmlocel"):
        from pm4py.objects.ocel.importer.xmlocel import importer as xmlocel_importer
        return xmlocel_importer.apply(file_path)


def read_ocel_csv(file_path: str, objects_path: Optional[str] = None) -> OCEL:
    """
    Reads an object-centric event log from a CSV file (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the object-centric event log (.csv)
    :param objects_path: [Optional] file path from which the objects dataframe should be read
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel_csv("<path_to_ocel_file.csv>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.csv import importer as csv_importer
    return csv_importer.apply(file_path, objects_path=objects_path)


def read_ocel_json(file_path: str) -> OCEL:
    """
    Reads an object-centric event log from a JSON-OCEL file (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the object-centric event log (.jsonocel)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel_json("<path_to_ocel_file.jsonocel>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.jsonocel import importer as jsonocel_importer
    return jsonocel_importer.apply(file_path)


def read_ocel_xml(file_path: str) -> OCEL:
    """
    Reads an object-centric event log from a XML-OCEL file (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the object-centric event log (.xmlocel)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel_xml("<path_to_ocel_file.xmlocel>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.xmlocel import importer as xmlocel_importer
    return xmlocel_importer.apply(file_path)
