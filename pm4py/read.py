import logging
from pm4py.util import constants, xes_constants

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


def read_csv(file_path, sep=",", quotechar=None, encoding=None, nrows=None, timest_format=None):
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
        (If specified) number of rows
    timest_format
        Format of the timestamp columns

    Returns
    ----------------
    dataframe
        Dataframe
    """
    from pm4py.objects.log.adapters.pandas import csv_import_adapter
    df = csv_import_adapter.import_dataframe_from_path(file_path, sep=sep, quotechar=quotechar, encoding=encoding,
                                                       nrows=nrows, timest_format=timest_format)
    if len(df.columns) < 2:
        logging.error(
            "Less than three columns were imported from the CSV file. Please check the specification of the separation and the quote character!")
    else:
        logging.warning(
            "Please specify the format of the dataframe: df = pm4py.format_dataframe(df, case_id='<name of the case ID column>', activity_key='<name of the activity column>', timestamp_key='<name of the timestamp column>')")

    return df


def format_dataframe(df, case_id=constants.CASE_CONCEPT_NAME, activity_key=xes_constants.DEFAULT_NAME_KEY,
                     timestamp_key=xes_constants.DEFAULT_TIMESTAMP_KEY):
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

    Returns
    --------------
    df
        Dataframe
    """
    if case_id not in df.columns:
        raise Exception(case_id + " column (case ID) is not in the dataframe!")
    if activity_key not in df.columns:
        raise Exception(activity_key + " column (activity) is not in the dataframe!")
    if timestamp_key not in df.columns:
        raise Exception(timestamp_key + " column (timestamp) is not in the dataframe!")
    df = df.rename(columns={case_id: constants.CASE_CONCEPT_NAME, activity_key: xes_constants.DEFAULT_NAME_KEY,
                            timestamp_key: xes_constants.DEFAULT_TIMESTAMP_KEY})
    df[constants.CASE_CONCEPT_NAME] = df[constants.CASE_CONCEPT_NAME].astype(str)
    # set an index column
    df[INDEX_COLUMN] = df.index
    # sorts the dataframe
    df = df.sort_values([constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_TIMESTAMP_KEY, INDEX_COLUMN])
    logging.warning(
        "please convert the dataframe for advanced process mining applications. log = pm4py.convert_to_event_log(df)")
    return df


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
    from pm4py.objects.conversion.log import converter
    log = converter.apply(obj, variant=converter.Variants.TO_EVENT_LOG)
    return log


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
    from pm4py.objects.conversion.log import converter
    stream = converter.apply(obj, variant=converter.Variants.TO_EVENT_STREAM)
    return stream


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
    from pm4py.objects.conversion.log import converter
    df = converter.apply(obj, variant=converter.Variants.TO_DATA_FRAME)
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
