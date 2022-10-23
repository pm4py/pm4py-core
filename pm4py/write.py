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
The ``pm4py.write`` module contains all funcationality related to writing files/objects to disk.
"""

import warnings
import deprecation

from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.utils import __event_log_deprecation_warning
import pandas as pd
from typing import Union, Optional, Collection, Tuple, Dict
from pm4py.util import constants
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.objects.log.obj import XESExtension


def write_xes(log: Union[EventLog, pd.DataFrame], file_path: str, case_id_key: str = "case:concept:name", extensions: Optional[Collection[XESExtension]] = None, **kwargs) -> None:
    """
    Writes an event log to disk in the XES format (see `xes-standard <https://xes-standard.org/>`_)

    :param log: log object (``pandas.DataFrame``) that needs to be written to disk
    :param file_path: target file path of the event log (``.xes`` file) on disk
    :param case_id_key: column key that identifies the case identifier
    :param extensions: extensions defined for the event log
        
    .. code-block:: python3

        import pm4py

        pm4py.write_xes(log, '<path_to_export_to>', case_id_key='case:concept:name')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)

    file_path = str(file_path)
    if not (file_path.lower().endswith("xes") or file_path.lower().endswith("xes.gz")):
        file_path = file_path + ".xes"

    parameters = {}
    for k, v in kwargs.items():
        parameters[k] = v
    parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] = case_id_key
    parameters["extensions"] = extensions

    from pm4py.objects.log.exporter.xes import exporter as xes_exporter
    xes_exporter.apply(log, file_path, parameters=parameters)


def write_pnml(petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, file_path: str) -> None:
    """
    Writes a Petri net object to disk in the ``.pnml`` format (see `pnml-standard <https://www.pnml.org/>`_)

    :param petri_net: Petri net object that needs to be written to disk
    :param initial_marking: initial marking of the Petri net
    :param final_marking: final marking of the Petri net
    :param file_path: target file path on disk of the ``.pnml`` file

    .. code-block:: python3

        import pm4py

        log = pm4py.write_pnml(pn, im, fm, '<path_to_export_to>')
    """
    file_path = str(file_path)
    if not file_path.lower().endswith("pnml"):
        file_path = file_path + ".pnml"

    from pm4py.objects.petri_net.exporter import exporter as petri_exporter
    petri_exporter.apply(petri_net, initial_marking, file_path, final_marking=final_marking)


def write_ptml(tree: ProcessTree, file_path: str) -> None:
    """
    Writes a process tree object to disk in the ``.ptml`` format.

    :param tree: ProcessTree object that needs to be written to disk
    :param file_path: target file path on disk of the ``.ptml`` file

    .. code-block:: python3

        import pm4py

        log = pm4py.write_ptml(tree, '<path_to_export_to>')
    """
    file_path = str(file_path)
    if not file_path.lower().endswith("ptml"):
        file_path = file_path + ".ptml"

    from pm4py.objects.process_tree.exporter import exporter as tree_exporter
    tree_exporter.apply(tree, file_path)


def write_dfg(dfg: Dict[Tuple[str,str],int], start_activities:  Dict[str,int], end_activities:  Dict[str,int], file_path: str):
    """
    Writes a directly follows graph (DFG) object to disk in the ``.dfg`` format.

    :param dfg: directly follows relation (multiset of activity-activity pairs)
    :param start_activities: multiset tracking the number of occurrences of start activities
    :param end_activities: mulltiset tracking the number of occurrences of end activities
    :param file_path: target file path on disk to write the dfg object to

    .. code-block:: python3

        import pm4py

        log = pm4py.write_dfg(dfg, sa, ea, '<path_to_export_to>')
    """
    file_path = str(file_path)
    if not file_path.lower().endswith("dfg"):
        file_path = file_path + ".dfg"

    from pm4py.objects.dfg.exporter import exporter as dfg_exporter
    dfg_exporter.apply(dfg, file_path,
                       parameters={dfg_exporter.Variants.CLASSIC.value.Parameters.START_ACTIVITIES: start_activities,
                                   dfg_exporter.Variants.CLASSIC.value.Parameters.END_ACTIVITIES: end_activities})


def write_bpmn(model: BPMN, file_path: str, auto_layout: bool = True):
    """
    Writes a BPMN model object to disk in the ``.bpmn`` format.

    :param model: BPMN model to export
    :param file_path: target file path on disk to write the BPMN object to
    :param auto_layout: boolean indicating whether the model should get an auto layout (which is written to disk)

    .. code-block:: python3

        import pm4py

        log = pm4py.write_bpmn(model, '<path_to_export_to>')
    """
    file_path = str(file_path)
    if not file_path.lower().endswith("bpmn"):
        file_path = file_path + ".bpmn"

    if auto_layout:
        from pm4py.objects.bpmn.layout import layouter
        model = layouter.apply(model)
    from pm4py.objects.bpmn.exporter import exporter
    exporter.apply(model, file_path)

@deprecation.deprecated("2.3.0", "3.0.0", "the write_ocel function is deprecated and replaced by write_ocel_csv, write_ocel_json and write_ocel_xml, respectively")
def write_ocel(ocel: OCEL, file_path: str, objects_path: str = None):
    """
    Writes an OCEL object to disk in the ``.bpmn`` format.
    Different formats are supported, including CSV (flat table), JSON-OCEL and XML-OCEL
    (described in the site http://www.ocel-standard.org/).

    :param ocel: OCEL object to write to disk
    :param file_path: target file path on disk to write the OCEL object to
    :param objects_path: location of the objects table (only applicable in case of .csv exporting)

    .. code-block:: python3

        import pm4py

        log = pm4py.write_ocel(ocel, '<path_to_export_to>')
    """
    file_path = str(file_path)

    if file_path.lower().endswith("csv"):
        from pm4py.objects.ocel.exporter.csv import exporter as csv_exporter
        return csv_exporter.apply(ocel, file_path, objects_path=objects_path)
    elif file_path.lower().endswith("jsonocel"):
        from pm4py.objects.ocel.exporter.jsonocel import exporter as jsonocel_exporter
        return jsonocel_exporter.apply(ocel, file_path)
    elif file_path.lower().endswith("xmlocel"):
        from pm4py.objects.ocel.exporter.xmlocel import exporter as xmlocel_exporter
        return xmlocel_exporter.apply(ocel, file_path)


def write_ocel_csv(ocel: OCEL, file_path: str, objects_path: str):
    """
    Writes an OCEL object to disk in the ``.csv`` file format.
    The OCEL object is exported into two separate files, i.e., one event table and one objects table.
    Both file paths should be specified

    :param ocel: OCEL object
    :param file_path: target file path on disk to write the event table to
    :param objects_path: target file path on disk to write the objects table to

    .. code-block:: python3

        import pm4py

        log = pm4py.write_ocel_csv(ocel, '<path_to_export_events_to>', '<path_to_export_objects_to>')
    """
    file_path = str(file_path)
    if not file_path.lower().endswith("csv"):
        file_path = file_path + ".csv"

    from pm4py.objects.ocel.exporter.csv import exporter as csv_exporter
    return csv_exporter.apply(ocel, file_path, objects_path=objects_path)


def write_ocel_json(ocel: OCEL, file_path: str):
    """
    Writes an OCEL object to disk in the ``.json`` file format (exported as ``.oceljson`` file).

    :param ocel: OCEL object
    :param file_path: target file path on disk to write the OCEL object to

    .. code-block:: python3

        import pm4py

        log = pm4py.write_ocel_json(ocel, '<path_to_export_to>')
    """
    file_path = str(file_path)
    if not file_path.lower().endswith("jsonocel"):
        file_path = file_path + ".jsonocel"

    from pm4py.objects.ocel.exporter.jsonocel import exporter as jsonocel_exporter
    return jsonocel_exporter.apply(ocel, file_path)


def write_ocel_xml(ocel: OCEL, file_path: str):
    """
    Writes an OCEL object to disk in the ``.xml`` file format (exported as ``.ocelxml`` file).

    :param ocel: OCEL object
    :param file_path: target file path on disk to write the OCEL object to

    .. code-block:: python3

        import pm4py

        log = pm4py.write_ocel_xml(ocel, '<path_to_export_to>')
    """
    file_path = str(file_path)
    if not file_path.lower().endswith("xmlocel"):
        file_path = file_path + ".xmlocel"

    from pm4py.objects.ocel.exporter.xmlocel import exporter as xmlocel_exporter
    return xmlocel_exporter.apply(ocel, file_path)
