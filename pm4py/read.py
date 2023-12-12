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
from typing import Tuple, Dict, Optional

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.log.obj import EventLog
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants

import os

from pandas import DataFrame
import importlib.util
from typing import Union

INDEX_COLUMN = "@@index"

__doc__ = """
The ``pm4py.read`` module contains all funcationality related to reading files/objects from disk.
"""


def read_xes(file_path: str, variant: Optional[str] = None, return_legacy_log_object: bool = constants.DEFAULT_READ_XES_LEGACY_OBJECT, encoding: str = constants.DEFAULT_ENCODING, **kwargs) -> Union[DataFrame, EventLog]:
    """
    Reads an event log stored in XES format (see `xes-standard <https://xes-standard.org/>`_)
    Returns a table (``pandas.DataFrame``) view of the event log.

    :param file_path: file path of the event log (``.xes`` file) on disk
    :param variant: the variant of the importer to use. "iterparse" => traditional XML parser; "line_by_line" => text-based line-by-line importer ; "chunk_regex" => chunk-of-bytes importer (default); "iterparse20" => XES 2.0 importer
    :param return_legacy_log_object: boolean value enabling returning a log object (default: False)
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``DataFrame``

    .. code-block:: python3

        import pm4py

        log = pm4py.read_xes("<path_to_xes_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    if variant is None:
        variant = constants.DEFAULT_XES_PARSER

    from pm4py.objects.log.importer.xes import importer as xes_importer

    v = xes_importer.Variants.CHUNK_REGEX
    if variant == "iterparse_20":
        v = xes_importer.Variants.ITERPARSE_20
    elif variant == "iterparse":
        v = xes_importer.Variants.ITERPARSE
    elif variant == "lxml":
        v = xes_importer.Variants.ITERPARSE
    elif variant == "iterparse_mem_compressed":
        v = xes_importer.Variants.ITERPARSE_MEM_COMPRESSED
    elif variant == "line_by_line":
        v = xes_importer.Variants.LINE_BY_LINE
    elif variant == "chunk_regex":
        v = xes_importer.Variants.CHUNK_REGEX
    elif variant == "rustxes":
        v = xes_importer.Variants.RUSTXES

    from copy import copy
    parameters = copy(kwargs)
    parameters["encoding"] = encoding
    parameters["return_legacy_log_object"] = return_legacy_log_object

    log = xes_importer.apply(file_path, variant=v, parameters=parameters)

    if type(log) is EventLog and not return_legacy_log_object:
        log = log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)
        log = dataframe_utils.convert_timestamp_columns_in_df(log, timest_format="ISO8601")

    return log


def read_pnml(file_path: str, auto_guess_final_marking: bool = False, encoding: str = constants.DEFAULT_ENCODING) -> Tuple[PetriNet, Marking, Marking]:
    """
    Reads a Petri net object from a .pnml file.
    The Petri net object returned is a triple containing the following objects:
    
    1. Petrinet Object, encoded as a ``PetriNet`` class
    #. Initial Marking
    #. Final Marking

    :rtype: ``Tuple[PetriNet, Marking, Marking]``
    :param file_path: file path of the Petri net model (``.pnml`` file) on disk
    :param encoding: the encoding to be used (default: utf-8)

    .. code-block:: python3

        import pm4py

        pn = pm4py.read_pnml("<path_to_pnml_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.petri_net.importer import importer as pnml_importer
    net, im, fm = pnml_importer.apply(file_path, parameters={"auto_guess_final_marking": auto_guess_final_marking, "encoding": encoding})
    return net, im, fm


def read_ptml(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> ProcessTree:
    """
    Reads a process tree object from a .ptml file

    :param file_path: file path of the process tree object on disk
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``ProcessTree``

    .. code-block:: python3

        import pm4py

        process_tree = pm4py.read_ptml("<path_to_ptml_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.process_tree.importer import importer as tree_importer
    tree = tree_importer.apply(file_path, parameters={"encoding": encoding})
    return tree


def read_dfg(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> Tuple[Dict[Tuple[str,str],int], Dict[str,int], Dict[str,int]]:
    """
    Reads a DFG object from a .dfg file.
    The DFG object returned is a triple containing the following objects:
    
    1. DFG Object, encoded as a ``Dict[Tuple[str,str],int]``, s.t. ``DFG[('a','b')]=k`` implies that activity ``'a'`` is directly followed by activity ``'b'`` a total of ``k`` times in the log
    #. Start activity dictionary, encoded as a ``Dict[str,int]``, s.t., ``S['a']=k`` implies that activity ``'a'`` is starting ``k`` traces in the event log
    #. End activity dictionary, encoded as a ``Dict[str,int]``, s.t., ``E['z']=k`` implies that activity ``'z'`` is ending ``k`` traces in the event log.

    :rtype: ``Tuple[Dict[Tuple[str,str],int], Dict[str,int], Dict[str,int]]``
    :param file_path: file path of the dfg model on disk
    :param encoding: the encoding to be used (default: utf-8)

    .. code-block:: python3

       import pm4py

       dfg = pm4py.read_dfg("<path_to_dfg_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.dfg.importer import importer as dfg_importer
    dfg, start_activities, end_activities = dfg_importer.apply(file_path, parameters={"encoding": encoding})
    return dfg, start_activities, end_activities


def read_bpmn(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> BPMN:
    """
    Reads a BPMN model from a .bpmn file

    :param file_path: file path of the bpmn model
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``BPMN``

    .. code-block:: python3

        import pm4py

        bpmn = pm4py.read_bpmn('<path_to_bpmn_file>')

    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.bpmn.importer import importer as bpmn_importer
    bpmn_graph = bpmn_importer.apply(file_path, parameters={"encoding": encoding})
    return bpmn_graph


def read_ocel(file_path: str, objects_path: Optional[str] = None, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an object-centric event log from a file (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the object-centric event log
    :param objects_path: [Optional] file path from which the objects dataframe should be read
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel("<path_to_ocel_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    if file_path.lower().endswith("csv"):
        return read_ocel_csv(file_path, objects_path, encoding=encoding)
    elif file_path.lower().endswith("jsonocel"):
        return read_ocel_json(file_path, encoding=encoding)
    elif file_path.lower().endswith("xmlocel"):
        return read_ocel_xml(file_path, encoding=encoding)
    elif file_path.lower().endswith(".sqlite"):
        return read_ocel_sqlite(file_path, encoding=encoding)
    raise Exception("unsupported file format")


def read_ocel_csv(file_path: str, objects_path: Optional[str] = None, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an object-centric event log from a CSV file (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the object-centric event log (.csv)
    :param objects_path: [Optional] file path from which the objects dataframe should be read
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel_csv("<path_to_ocel_file.csv>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.csv import importer as csv_importer
    return csv_importer.apply(file_path, objects_path=objects_path, parameters={"encoding": encoding})


def read_ocel_json(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an object-centric event log from a JSON-OCEL file (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the object-centric event log (.jsonocel)
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel_json("<path_to_ocel_file.jsonocel>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.jsonocel import importer as jsonocel_importer
    return jsonocel_importer.apply(file_path, variant=jsonocel_importer.Variants.CLASSIC, parameters={"encoding": encoding})


def read_ocel_xml(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an object-centric event log from a XML-OCEL file (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the object-centric event log (.xmlocel)
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel_xml("<path_to_ocel_file.xmlocel>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.xmlocel import importer as xmlocel_importer
    return xmlocel_importer.apply(file_path, variant=xmlocel_importer.Variants.CLASSIC, parameters={"encoding": encoding})


def read_ocel_sqlite(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an object-centric event log from a SQLite database (see: http://www.ocel-standard.org/).
    The ``OCEL`` object is returned by this method

    :param file_path: file path of the SQLite database (.sqlite)
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel_sqlite("<path_to_ocel_file.sqlite>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.sqlite import importer as sqlite_importer
    return sqlite_importer.apply(file_path, variant=sqlite_importer.Variants.PANDAS_IMPORTER, parameters={"encoding": encoding})


def read_ocel2(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an OCEL2.0 event log

    :param file_path: path to the OCEL2.0 event log
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel2("<path_to_ocel_file>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    if file_path.lower().endswith("sqlite"):
        return read_ocel2_sqlite(file_path, encoding=encoding)
    elif file_path.lower().endswith("xml") or file_path.lower().endswith("xmlocel"):
        return read_ocel2_xml(file_path, encoding=encoding)
    elif file_path.lower().endswith("jsonocel"):
        return read_ocel2_json(file_path, encoding=encoding)


def read_ocel2_json(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an OCEL2.0 event log from a JSON-OCEL(2) file

    :param file_path: path to the JSON file
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel2_json("<path_to_ocel_file.jsonocel>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.jsonocel import importer as jsonocel_importer
    return jsonocel_importer.apply(file_path, variant=jsonocel_importer.Variants.OCEL20_STANDARD, parameters={"encoding": encoding})


def read_ocel2_sqlite(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an OCEL2.0 event log from a SQLite database

    :param file_path: path to the OCEL2.0 database
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel2_sqlite("<path_to_ocel_file.sqlite>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.sqlite import importer as sqlite_importer
    return sqlite_importer.apply(file_path, variant=sqlite_importer.Variants.OCEL20, parameters={"encoding": encoding})


def read_ocel2_xml(file_path: str, encoding: str = constants.DEFAULT_ENCODING) -> OCEL:
    """
    Reads an OCEL2.0 event log from an XML file

    :param file_path: path to the OCEL2.0 event log
    :param encoding: the encoding to be used (default: utf-8)
    :rtype: ``OCEL``

    .. code-block:: python3

        import pm4py

        ocel = pm4py.read_ocel2_xml("<path_to_ocel_file.xmlocel>")
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")

    from pm4py.objects.ocel.importer.xmlocel import importer as xml_importer
    return xml_importer.apply(file_path, variant=xml_importer.Variants.OCEL20, parameters={"encoding": encoding})


def read_dcr_xml(file_path, **parameters):
    """
    Reads a DCR graph from an XML file
    :param file_path: path to the DCR graph
    :param parameters: parameters of the importer
    :rtype: ``DCR``
    .. code-block:: python3
        import pm4py
        dcr = pm4py.read_dcr_xml("<path_to_dcr_file>", variant)
    """
    if not os.path.exists(file_path):
        raise Exception("File does not exist")
    from pm4py.objects.dcr.importer import importer as dcr_importer
    return dcr_importer.apply(file_path, **parameters)
