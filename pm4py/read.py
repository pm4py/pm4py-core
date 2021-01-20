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
import logging

import deprecation

from pm4py import VERSION
from pm4py.util import constants

INDEX_COLUMN = "@@index"


def read_xes(file_path):
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
    from pm4py.objects.log.importer.xes import importer as xes_importer
    log = xes_importer.apply(file_path)
    return log


@deprecation.deprecated(deprecated_in="2.0.1.3", removed_in="3.0",
                        current_version=VERSION,
                        details="Use pandas to import CSV files")
def read_csv(file_path, sep=",", quotechar=None, encoding=constants.DEFAULT_ENCODING, nrows=10000000, timest_format=None):
    """
    Reads an event log in the CSV format (Pandas adapter)

    Parameters
    ----------------
    file_path
        File path
    sep
        Separator; default: ,
    quotechar
        Quote char; default: None
    encoding
        Encoding; default: default of Pandas
    nrows
        maximum number of rows to read (default 10000000)
    timest_format
        Format of the timestamp columns

    Returns
    ----------------
    dataframe
        Dataframe
    """
    from pm4py.objects.log.util import dataframe_utils
    import pandas as pd
    if quotechar is not None:
        df = pd.read_csv(file_path, sep=sep, quotechar=quotechar, encoding=encoding, nrows=nrows)
    else:
        df = pd.read_csv(file_path, sep=sep, encoding=encoding, nrows=nrows)
    df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=timest_format)
    if len(df.columns) < 2:
        logging.error(
            "Less than three columns were imported from the CSV file. Please check the specification of the separation and the quote character!")
    else:
        # logging.warning(
        #    "Please specify the format of the dataframe: df = pm4py.format_dataframe(df, case_id='<name of the case ID column>', activity_key='<name of the activity column>', timestamp_key='<name of the timestamp column>')")
        pass

    return df


def read_petri_net(file_path):
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
    from pm4py.objects.petri.importer import importer as pnml_importer
    net, im, fm = pnml_importer.apply(file_path)
    return net, im, fm


def read_process_tree(file_path):
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
    from pm4py.objects.process_tree.importer import importer as tree_importer
    tree = tree_importer.apply(file_path)
    return tree


def read_dfg(file_path):
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
    from pm4py.objects.dfg.importer import importer as dfg_importer
    dfg, start_activities, end_activities = dfg_importer.apply(file_path)
    return dfg, start_activities, end_activities


def read_bpmn(file_path):
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
    from pm4py.objects.bpmn.importer import importer as bpmn_importer
    bpmn_graph = bpmn_importer.apply(file_path)
    return bpmn_graph


@deprecation.deprecated(deprecated_in="2.1.0", removed_in="3.0",
                        current_version=VERSION,
                        details="Use pm4py.convert.convert_to_event_log method")
def convert_to_event_log(obj):
    """
    Converts a log object to an event log

    Parameters
    -------------
    obj
        Log object

    Returns
    -------------
    log
        Event log object
    """
    from pm4py.convert import convert_to_event_log
    return convert_to_event_log(obj)


@deprecation.deprecated(deprecated_in="2.1.0", removed_in="3.0",
                        current_version=VERSION,
                        details="Use pm4py.convert.convert_to_event_stream method")
def convert_to_event_stream(obj):
    """
    Converts a log object to an event stream

    Parameters
    --------------
    obj
        Log object

    Returns
    --------------
    stream
        Event stream object
    """
    from pm4py.convert import convert_to_event_stream
    return convert_to_event_stream(obj)


@deprecation.deprecated(deprecated_in="2.1.0", removed_in="3.0",
                        current_version=VERSION,
                        details="Use pm4py.convert.convert_to_event_stream method")
def convert_to_dataframe(obj):
    """
    Converts a log object to a dataframe

    Parameters
    --------------
    obj
        Log object

    Returns
    --------------
    df
        Dataframe
    """
    from pm4py.convert import convert_to_dataframe
    return convert_to_dataframe(obj)
