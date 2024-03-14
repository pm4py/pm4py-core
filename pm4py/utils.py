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
"""

import datetime
from typing import Optional, Tuple, Any, Collection, Union, List

import pandas as pd

from pm4py.objects.log.obj import EventLog, EventStream, Trace, Event
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.powl.obj import POWL
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import constants, xes_constants, pandas_utils
import warnings
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.util.dt_parsing.variants import strpfromiso
import deprecation


INDEX_COLUMN = "@@index"
CASE_INDEX_COLUMN = "@@case_index"


def format_dataframe(df: pd.DataFrame, case_id: str = constants.CASE_CONCEPT_NAME,
                     activity_key: str = xes_constants.DEFAULT_NAME_KEY,
                     timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
                     start_timestamp_key: str = xes_constants.DEFAULT_START_TIMESTAMP_KEY,
                     timest_format: Optional[str] = None) -> pd.DataFrame:
    """
    Give the appropriate format on the dataframe, for process mining purposes

    :param df: Dataframe
    :param case_id: Case identifier column
    :param activity_key: Activity column
    :param timestamp_key: Timestamp column
    :param start_timestamp_key: Start timestamp column
    :param timest_format: Timestamp format that is provided to Pandas
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pandas as pd
        import pm4py

        dataframe = pd.read_csv('event_log.csv')
        dataframe = pm4py.format_dataframe(dataframe, case_id_key='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp', start_timestamp_key='start_timestamp', timest_format='%Y-%m-%d %H:%M:%S')
    """
    if timest_format is None:
        timest_format = constants.DEFAULT_TIMESTAMP_PARSE_FORMAT

    from pm4py.objects.log.util import dataframe_utils
    if case_id not in df.columns:
        raise Exception(case_id + " column (case ID) is not in the dataframe!")
    if activity_key not in df.columns:
        raise Exception(activity_key + " column (activity) is not in the dataframe!")
    if timestamp_key not in df.columns:
        raise Exception(timestamp_key + " column (timestamp) is not in the dataframe!")
    if case_id != constants.CASE_CONCEPT_NAME:
        if constants.CASE_CONCEPT_NAME in df.columns:
            del df[constants.CASE_CONCEPT_NAME]
        df[constants.CASE_CONCEPT_NAME] = df[case_id]
    if activity_key != xes_constants.DEFAULT_NAME_KEY:
        if xes_constants.DEFAULT_NAME_KEY in df.columns:
            del df[xes_constants.DEFAULT_NAME_KEY]
        df[xes_constants.DEFAULT_NAME_KEY] = df[activity_key]
    if timestamp_key != xes_constants.DEFAULT_TIMESTAMP_KEY:
        if xes_constants.DEFAULT_TIMESTAMP_KEY in df.columns:
            del df[xes_constants.DEFAULT_TIMESTAMP_KEY]
        df[xes_constants.DEFAULT_TIMESTAMP_KEY] = df[timestamp_key]
    # makes sure that the timestamps column are of timestamp type
    df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=timest_format)
    # drop NaN(s) in the main columns (case ID, activity, timestamp) to ensure functioning of the
    # algorithms
    prev_length = len(df)
    df = df.dropna(subset={constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_NAME_KEY,
                           xes_constants.DEFAULT_TIMESTAMP_KEY}, how="any")

    if len(df) < prev_length:
        if constants.SHOW_INTERNAL_WARNINGS:
            warnings.warn("Some rows of the Pandas data frame have been removed because of empty case IDs, activity labels, or timestamps to ensure the correct functioning of PM4Py's algorithms.")

    # make sure the case ID column is of string type
    df[constants.CASE_CONCEPT_NAME] = df[constants.CASE_CONCEPT_NAME].astype("string")
    # make sure the activity column is of string type
    df[xes_constants.DEFAULT_NAME_KEY] = df[xes_constants.DEFAULT_NAME_KEY].astype("string")
    # set an index column
    df = pandas_utils.insert_index(df, INDEX_COLUMN, copy_dataframe=False)
    # sorts the dataframe
    df = df.sort_values([constants.CASE_CONCEPT_NAME, xes_constants.DEFAULT_TIMESTAMP_KEY, INDEX_COLUMN])
    # re-set the index column
    df = pandas_utils.insert_index(df, INDEX_COLUMN, copy_dataframe=False)
    # sets the index column in the dataframe
    df = pandas_utils.insert_case_index(df, CASE_INDEX_COLUMN, copy_dataframe=False)
    # sets the properties
    if not hasattr(df, 'attrs'):
        # legacy (Python 3.6) support
        df.attrs = {}
    if start_timestamp_key in df.columns:
        df[xes_constants.DEFAULT_START_TIMESTAMP_KEY] = df[start_timestamp_key]
        df.attrs[constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] = xes_constants.DEFAULT_START_TIMESTAMP_KEY
    df.attrs[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_constants.DEFAULT_NAME_KEY
    df.attrs[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_constants.DEFAULT_TIMESTAMP_KEY
    df.attrs[constants.PARAMETER_CONSTANT_GROUP_KEY] = xes_constants.DEFAULT_GROUP_KEY
    df.attrs[constants.PARAMETER_CONSTANT_TRANSITION_KEY] = xes_constants.DEFAULT_TRANSITION_KEY
    df.attrs[constants.PARAMETER_CONSTANT_RESOURCE_KEY] = xes_constants.DEFAULT_RESOURCE_KEY
    df.attrs[constants.PARAMETER_CONSTANT_CASEID_KEY] = constants.CASE_CONCEPT_NAME
    return df


def rebase(log_obj: Union[EventLog, EventStream, pd.DataFrame], case_id: str = constants.CASE_CONCEPT_NAME,
                     activity_key: str = xes_constants.DEFAULT_NAME_KEY,
                     timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
                     start_timestamp_key: str = xes_constants.DEFAULT_START_TIMESTAMP_KEY, timest_format: Optional[str] = None) -> Union[EventLog, EventStream, pd.DataFrame]:
    """
    Re-base the log object, changing the case ID, activity and timestamp attributes.

    :param log_obj: Log object
    :param case_id: Case identifier
    :param activity_key: Activity
    :param timestamp_key: Timestamp
    :param start_timestamp_key: Start timestamp
    :param timest_format: Timestamp format that is provided to Pandas
    :rtype: ``Union[EventLog, EventStream, pd.DataFrame]``

    .. code-block:: python3

        import pm4py

        rebased_dataframe = pm4py.rebase(dataframe, case_id='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')
    """
    import pm4py

    __event_log_deprecation_warning(log_obj)

    if check_is_pandas_dataframe(log_obj):
        check_pandas_dataframe_columns(log_obj)

    if check_is_pandas_dataframe(log_obj):
        return format_dataframe(log_obj, case_id=case_id, activity_key=activity_key, timestamp_key=timestamp_key,
                                start_timestamp_key=start_timestamp_key, timest_format=timest_format)
    elif isinstance(log_obj, EventLog):
        log_obj = pm4py.convert_to_dataframe(log_obj)
        log_obj = format_dataframe(log_obj, case_id=case_id, activity_key=activity_key, timestamp_key=timestamp_key,
                                   start_timestamp_key=start_timestamp_key, timest_format=timest_format)
        from pm4py.objects.conversion.log import converter
        return converter.apply(log_obj, variant=converter.Variants.TO_EVENT_LOG)
    elif isinstance(log_obj, EventStream):
        log_obj = pm4py.convert_to_dataframe(log_obj)
        log_obj = format_dataframe(log_obj, case_id=case_id, activity_key=activity_key, timestamp_key=timestamp_key,
                                   start_timestamp_key=start_timestamp_key, timest_format=timest_format)
        return pm4py.convert_to_event_stream(log_obj)


def parse_process_tree(tree_string: str) -> ProcessTree:
    """
    Parse a process tree from a string

    :param tree_string: String representing a process tree (e.g. '-> ( 'A', O ( 'B', 'C' ), 'D' )'). Operators are '->': sequence, '+': parallel, 'X': xor choice, '*': binary loop, 'O' or choice
    :rtype: ``ProcessTree``

    .. code-block:: python3

        import pm4py

        process_tree = pm4py.parse_process_tree('-> ( 'A', O ( 'B', 'C' ), 'D' )')
    """
    from pm4py.objects.process_tree.utils.generic import parse
    return parse(tree_string)


def parse_powl_model_string(powl_string: str) -> POWL:
    """
    Parse a POWL model from a string representation of the process model
    (with the same format as the __repr__ and __str__ methods of the POWL model)

    :param powl_string: POWL model expressed as a string (__repr__ of the POWL model)
    :rtype: ``POWL``

    .. code-block:: python3

        import pm4py

        powl_model = pm4py.parse_powl_model_string('PO=(nodes={ NODE1, NODE2, NODE3 }, order={ NODE1-->NODE2 }')
        print(powl_model)

    Parameters
    ----------
    powl_string

    Returns
    -------

    """
    from pm4py.objects.powl import parser
    return parser.parse_powl_model_string(powl_string)


def serialize(*args) -> Tuple[str, bytes]:
    """
    Serialize a PM4Py object into a bytes string

    :param args: A PM4Py object, among: - an EventLog object - a Pandas dataframe object - a (Petrinet, Marking, Marking) tuple - a ProcessTree object - a BPMN object - a DFG, including the dictionary of the directly-follows relations, the start activities and the end activities
    :rtype: ``Tuple[str, bytes]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe)
        serialization = pm4py.serialize(net, im, fm)
    """
    from pm4py.objects.log.obj import EventLog
    from pm4py.objects.petri_net.obj import PetriNet
    from pm4py.objects.process_tree.obj import ProcessTree
    from pm4py.objects.bpmn.obj import BPMN
    from collections import Counter

    if type(args[0]) is EventLog:
        from pm4py.objects.log.exporter.xes import exporter as xes_exporter
        return (constants.AvailableSerializations.EVENT_LOG.value, xes_exporter.serialize(*args))
    elif pandas_utils.check_is_pandas_dataframe(args[0]):
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
        return (constants.AvailableSerializations.DFG.value,
                dfg_exporter.serialize(args[0], parameters={"start_activities": args[1], "end_activities": args[2]}))


def deserialize(ser_obj: Tuple[str, bytes]) -> Any:
    """
    Deserialize a bytes string to a PM4Py object

    :param ser_obj: Serialized object (a tuple consisting of a string denoting the type of the object, and a bytes string representing the serialization)
    :rtype: ``Any``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe)
        serialization = pm4py.serialize(net, im, fm)
        net, im, fm = pm4py.deserialize(serialization)
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


def get_properties(log, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", resource_key: str = "org:resource", group_key: Optional[str] = None, start_timestamp_key: Optional[str] = None, **kwargs):
    """
    Gets the properties from a log object

    :param log: Log object
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param start_timestamp_key: (optional) attribute to be used for the start timestamp
    :param case_id_key: attribute to be used as case identifier
    :param resource_key: (if provided) attribute to be used as resource
    :param group_key: (if provided) attribute to be used as group identifier
    :rtype: ``Dict``
    """
    __event_log_deprecation_warning(log)

    from copy import copy
    parameters = copy(log.properties) if hasattr(log, 'properties') else copy(log.attrs) if hasattr(log,
                                                                                                    'attrs') else {}

    if activity_key is not None:
        parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
        parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key

    if timestamp_key is not None:
        parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = timestamp_key

    if start_timestamp_key is not None:
        parameters[constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] = start_timestamp_key

    if case_id_key is not None:
        parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] = case_id_key

    if resource_key is not None:
        parameters[constants.PARAMETER_CONSTANT_RESOURCE_KEY] = resource_key

    if group_key is not None:
        parameters[constants.PARAMETER_CONSTANT_GROUP_KEY] = group_key

    for k, v in kwargs.items():
        parameters[k] = v

    return parameters


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="this method will be removed in a future release."
                                                  "Please use the method-specific arguments.")
def set_classifier(log, classifier, classifier_attribute=constants.DEFAULT_CLASSIFIER_ATTRIBUTE):
    """
    Methods to set the specified classifier on an existing event log

    :param log: Log object
    :param classifier: Classifier that should be set: - A list of event attributes can be provided - A single event attribute can be provided - A classifier stored between the "classifiers" of the log object can be provided
    :param classifier_attribute: The attribute of the event that should store the concatenation of the attribute values for the given classifier
    :rtype: ``Union[EventLog, pd.DataFrame]``
    """
    __event_log_deprecation_warning(log)

    if type(classifier) is list:
        pass
    elif type(classifier) is str:
        if type(log) is EventLog and classifier in log.classifiers:
            classifier = log.classifiers[classifier]
        else:
            classifier = [classifier]

    if type(log) is EventLog:
        for trace in log:
            for event in trace:
                event[classifier_attribute] = "+".join(list(event[x] for x in classifier))
        log.properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = classifier_attribute
        log.properties[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = classifier_attribute
    elif pandas_utils.check_is_pandas_dataframe(log):
        log[classifier_attribute] = log[classifier[0]]
        for i in range(1, len(classifier)):
            log[classifier_attribute] = log[classifier_attribute] + "+" + log[classifier[i]]
        log.attrs[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = classifier_attribute
        log.attrs[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = classifier_attribute
    else:
        raise Exception("setting classifier is not defined for this class of objects")

    return log


def parse_event_log_string(traces: Collection[str], sep: str = ",",
                           activity_key: str = xes_constants.DEFAULT_NAME_KEY,
                           timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
                           case_id_key: str = constants.CASE_CONCEPT_NAME,
                           return_legacy_log_object: bool = constants.DEFAULT_READ_XES_LEGACY_OBJECT) -> Union[EventLog, pd.DataFrame]:
    """
    Parse a collection of traces expressed as strings
    (e.g., ["A,B,C,D", "A,C,B,D", "A,D"])
    to a log object (Pandas dataframe)

    :param traces: Collection of traces expressed as strings
    :param sep: Separator used to split the activities of a string trace
    :param activity_key: The attribute that should be used as activity
    :param timestamp_key: The attribute that should be used as timestamp
    :param case_id_key: The attribute that should be used as case identifier
    :param return_legacy_log_object: boolean value enabling returning a log object (default: False)
    :rtype: ``pd.DataFrame``

    .. code-block:: python3

        import pm4py

        dataframe = pm4py.parse_event_log_string(["A,B,C,D", "A,C,B,D", "A,D"])
    """
    cases = []
    activitiess = []
    timestamps = []
    this_timest = 10000000

    for index, trace in enumerate(traces):
        activities = trace.split(sep)
        for act in activities:
            cases.append(str(index))
            activitiess.append(act)
            timestamps.append(strpfromiso.fix_naivety(datetime.datetime.fromtimestamp(this_timest)))
            this_timest = this_timest + 1

    dataframe = pandas_utils.instantiate_dataframe({case_id_key: cases, activity_key: activitiess, timestamp_key: timestamps})

    if return_legacy_log_object:
        import pm4py

        return pm4py.convert_to_event_log(dataframe, case_id_key=case_id_key)

    return dataframe


def project_on_event_attribute(log: Union[EventLog, pd.DataFrame], attribute_key=xes_constants.DEFAULT_NAME_KEY, case_id_key=None) -> \
List[List[str]]:
    """
    Project the event log on a specified event attribute. The result is a list, containing a list for each case:
    all the cases are transformed to list of values for the specified attribute.

    Example:

    pm4py.project_on_event_attribute(log, "concept:name")

    [['register request', 'examine casually', 'check ticket', 'decide', 'reinitiate request', 'examine thoroughly', 'check ticket', 'decide', 'pay compensation'],
    ['register request', 'check ticket', 'examine casually', 'decide', 'pay compensation'],
    ['register request', 'examine thoroughly', 'check ticket', 'decide', 'reject request'],
    ['register request', 'examine casually', 'check ticket', 'decide', 'pay compensation'],
    ['register request', 'examine casually', 'check ticket', 'decide', 'reinitiate request', 'check ticket', 'examine casually', 'decide', 'reinitiate request', 'examine casually', 'check ticket', 'decide', 'reject request'],
    ['register request', 'check ticket', 'examine thoroughly', 'decide', 'reject request']]

    :param log: Event log / Pandas dataframe
    :param attribute_key: The attribute to be used
    :param case_id_key: The attribute to be used as case identifier
    :rtype: ``List[List[str]]``

    .. code-block:: python3

        import pm4py

        list_list_activities = pm4py.project_on_event_attribute(dataframe, 'concept:name')
    """
    __event_log_deprecation_warning(log)

    output = []
    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)
        from pm4py.streaming.conversion import from_pandas
        parameters = {from_pandas.Parameters.ACTIVITY_KEY: attribute_key}
        if case_id_key is not None:
            parameters[from_pandas.Parameters.CASE_ID_KEY] = case_id_key
        it = from_pandas.apply(log, parameters=parameters)
        for trace in it:
            output.append([x[xes_constants.DEFAULT_NAME_KEY] if xes_constants.DEFAULT_NAME_KEY is not None else None for x in trace])
    else:
        for trace in log:
            output.append([x[attribute_key] if attribute_key is not None else None for x in trace])
    return output


def sample_cases(log: Union[EventLog, pd.DataFrame], num_cases: int, case_id_key: str = "case:concept:name") -> Union[EventLog, pd.DataFrame]:
    """
    (Random) Sample a given number of cases from the event log.

    :param log: Event log / Pandas dataframe
    :param num_cases: Number of cases to sample
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Union[EventLog, pd.DataFrame]``

    .. code-block:: python3

        import pm4py

        sampled_dataframe = pm4py.sample_cases(dataframe, 10, case_id_key='case:concept:name')
    """
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, case_id_key=case_id_key)

    properties = get_properties(log, case_id_key=case_id_key)

    if isinstance(log, EventLog):
        from pm4py.objects.log.util import sampling
        return sampling.sample(log, num_cases)
    elif check_is_pandas_dataframe(log):
        from pm4py.objects.log.util import dataframe_utils
        properties["max_no_cases"] = num_cases
        return dataframe_utils.sample_dataframe(log, parameters=properties)


def sample_events(log: Union[EventStream, OCEL], num_events: int) -> Union[EventStream, OCEL, pd.DataFrame]:
    """
    (Random) Sample a given number of events from the event log.

    :param log: Event stream / OCEL / Pandas dataframes
    :param num_events: Number of events to sample
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Union[EventStream, OCEL, pd.DataFrame]``

    .. code-block:: python3

        import pm4py

        sampled_dataframe = pm4py.sample_events(dataframe, 100)
    """
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log)

    if isinstance(log, EventLog):
        from pm4py.objects.log.util import sampling
        return sampling.sample_log(log, num_events)
    elif isinstance(log, EventStream):
        from pm4py.objects.log.util import sampling
        return sampling.sample_stream(log, num_events)
    elif isinstance(log, OCEL):
        from pm4py.objects.ocel.util import sampling
        return sampling.sample_ocel_events(log, parameters={"num_entities": num_events})
    elif check_is_pandas_dataframe(log):
        return log.sample(n=num_events)


def __event_log_deprecation_warning(log):
    if constants.SHOW_EVENT_LOG_DEPRECATION and not hasattr(log, "deprecation_warning_shown"):
        if constants.SHOW_INTERNAL_WARNINGS:
            if isinstance(log, EventLog) or isinstance(log, Trace):
                warnings.warn("the EventLog class has been deprecated and will be removed in a future release.")
                log.deprecation_warning_shown = True
            elif isinstance(log, Trace):
                warnings.warn("the Trace class has been deprecated and will be removed in a future release.")
                log.deprecation_warning_shown = True
            elif isinstance(log, EventStream):
                warnings.warn("the EventStream class has been deprecated and will be removed in a future release.")
                log.deprecation_warning_shown = True
