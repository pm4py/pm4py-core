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
from typing import Optional, Tuple, Any

import pandas as pd

from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import constants, xes_constants, pandas_utils


INDEX_COLUMN = "@@index"


def format_dataframe(df: pd.DataFrame, case_id: str = constants.CASE_CONCEPT_NAME,
                     activity_key: str = xes_constants.DEFAULT_NAME_KEY,
                     timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
                     timest_format: Optional[str] = None) -> pd.DataFrame:
    """
    Give the appropriate format on the dataframe, for process mining purposes

    Parameters
    --------------
    df
        Dataframe
    case_id
        Case identifier column
    activity_key
        Activity column
    timestamp_key
        Timestamp column
    timest_format
        Timestamp format that is provided to Pandas

    Returns
    --------------
    df
        Dataframe
    """
    from pm4py.objects.log.util import dataframe_utils
    if case_id not in df.columns:
        raise Exception(case_id + " column (case ID) is not in the dataframe!")
    if activity_key not in df.columns:
        raise Exception(activity_key + " column (activity) is not in the dataframe!")
    if timestamp_key not in df.columns:
        raise Exception(timestamp_key + " column (timestamp) is not in the dataframe!")
    df = df.rename(columns={case_id: constants.CASE_CONCEPT_NAME, activity_key: xes_constants.DEFAULT_NAME_KEY,
                            timestamp_key: xes_constants.DEFAULT_TIMESTAMP_KEY})
    df[constants.CASE_CONCEPT_NAME] = df[constants.CASE_CONCEPT_NAME].astype(str)
    # makes sure that the timestamp column is of timestamp type
    df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=timest_format,
                                                         timest_columns=[xes_constants.DEFAULT_TIMESTAMP_KEY])
    # set an index column
    df = pandas_utils.insert_index(df, INDEX_COLUMN)
    # sorts the dataframe
    df = df.sort_values([constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_TIMESTAMP_KEY, INDEX_COLUMN])
    # logging.warning(
    #    "please convert the dataframe for advanced process mining applications. log = pm4py.convert_to_event_log(df)")
    return df


def parse_process_tree(tree_string: str) -> ProcessTree:
    """
    Parse a process tree from a string

    Parameters
    ----------------
    tree_string
        String representing a process tree (e.g. '-> ( 'A', O ( 'B', 'C' ), 'D' )')
        Operators are '->': sequence, '+': parallel, 'X': xor choice, '*': binary loop, 'O' or choice

    Returns
    ----------------
    tree
        Process tree
    """
    from pm4py.objects.process_tree.utils.generic import parse
    return parse(tree_string)


def serialize(*args) -> Tuple[str, bytes]:
    """
    Serialize a PM4Py object into a bytes string

    Parameters
    -----------------
    args
        A PM4Py object, among:
        - an EventLog object
        - a Pandas dataframe object
        - a (Petrinet, Marking, Marking) tuple
        - a ProcessTree object
        - a BPMN object
        - a DFG, including the dictionary of the directly-follows relations, the start activities and the end activities

    Returns
    -----------------
    ser
        Serialized object (a tuple consisting of a string denoting the type of the object, and a bytes string
        representing the serialization)
    """
    from pm4py.objects.log.obj import EventLog
    from pm4py.objects.petri_net.obj import PetriNet
    from pm4py.objects.process_tree.obj import ProcessTree
    from pm4py.objects.bpmn.obj import BPMN
    from collections import Counter

    if type(args[0]) is EventLog:
        from pm4py.objects.log.exporter.xes import exporter as xes_exporter
        return (constants.AvailableSerializations.EVENT_LOG.value, xes_exporter.serialize(*args))
    elif type(args[0]) is pd.DataFrame:
        from io import BytesIO
        buffer = BytesIO()
        args[0].to_parquet(buffer)
        return (constants.AvailableSerializations.DATAFRAME.value, buffer.getvalue())
    elif len(args) == 3 and type(args[0]) is PetriNet:
        from pm4py.objects.petri_net.exporter import exporter as petri_exporter
        return (constants.AvailableSerializations.PETRI_NET.value, petri_exporter.serialize(*args))
    elif type(args[0]) is ProcessTree:
        from pm4py.objects.process_tree.exporter import exporter as tree_exporter
        return (constants.AvailableSerializations.PROCESS_TREE.value, tree_exporter.serialize(*args))
    elif type(args[0]) is BPMN:
        from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
        return (constants.AvailableSerializations.BPMN.value, bpmn_exporter.serialize(*args))
    elif len(args) == 3 and (isinstance(args[0], dict) or isinstance(args[0], Counter)):
        from pm4py.objects.dfg.exporter import exporter as dfg_exporter
        return (constants.AvailableSerializations.DFG.value, dfg_exporter.serialize(args[0], parameters={"start_activities": args[1], "end_activities": args[2]}))


def deserialize(ser_obj: Tuple[str, bytes]) -> Any:
    """
    Deserialize a bytes string to a PM4Py object

    Parameters
    ----------------
    ser
        Serialized object (a tuple consisting of a string denoting the type of the object, and a bytes string
        representing the serialization)

    Returns
    ----------------
    obj
         A PM4Py object, among:
        - an EventLog object
        - a Pandas dataframe object
        - a (Petrinet, Marking, Marking) tuple
        - a ProcessTree object
        - a BPMN object
        - a DFG, including the dictionary of the directly-follows relations, the start activities and the end activities
    """
    if ser_obj[0] == constants.AvailableSerializations.EVENT_LOG.value:
        from pm4py.objects.log.importer.xes import importer as xes_importer
        return xes_importer.deserialize(ser_obj[1])
    elif ser_obj[0] == constants.AvailableSerializations.DATAFRAME.value:
        from io import BytesIO
        buffer = BytesIO()
        buffer.write(ser_obj[1])
        buffer.flush()
        return pd.read_parquet(buffer)
    elif ser_obj[0] == constants.AvailableSerializations.PETRI_NET.value:
        from pm4py.objects.petri_net.importer import importer as petri_importer
        return petri_importer.deserialize(ser_obj[1])
    elif ser_obj[0] == constants.AvailableSerializations.PROCESS_TREE.value:
        from pm4py.objects.process_tree.importer import importer as tree_importer
        return tree_importer.deserialize(ser_obj[1])
    elif ser_obj[0] == constants.AvailableSerializations.BPMN.value:
        from pm4py.objects.bpmn.importer import importer as bpmn_importer
        return bpmn_importer.deserialize(ser_obj[1])
    elif ser_obj[0] == constants.AvailableSerializations.DFG.value:
        from pm4py.objects.dfg.importer import importer as dfg_importer
        return dfg_importer.deserialize(ser_obj[1])
