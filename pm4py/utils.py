'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
__doc__ = """
"""

import datetime
from typing import Optional, Tuple, Any, Collection, Union, List

import pandas as pd

from pm4py.objects.log.obj import EventLog, EventStream, Trace
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.powl.obj import POWL
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import constants, xes_constants, pandas_utils
import warnings
from pm4py.util.pandas_utils import (
    check_is_pandas_dataframe,
    check_pandas_dataframe_columns,
)
from pm4py.util.dt_parsing.variants import strpfromiso
from pm4py.util import deprecation
from pm4py.util.rustxes_utils import get_rustxes_backend_name


INDEX_COLUMN = "@@index"
CASE_INDEX_COLUMN = "@@case_index"


class Shared:
    RUSTXES_WARNING_SHOWN = False
    FILTERING_LEVEL_WARNING_SHOWN = False


def is_polars_lazyframe(df: Any) -> bool:
    """Return True if the provided dataframe is a Polars LazyFrame."""
    df_type = str(type(df)).lower()
    return "polars" in df_type and "lazyframe" in df_type


def format_dataframe(
    df,
    case_id: str = constants.CASE_CONCEPT_NAME,
    activity_key: str = xes_constants.DEFAULT_NAME_KEY,
    timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
    start_timestamp_key: str = xes_constants.DEFAULT_START_TIMESTAMP_KEY,
    timest_format: Optional[str] = None,
) -> Any:
    """
    Formats the dataframe appropriately for process mining purposes.

    :param df: Dataframe.
    :param case_id: Case identifier column.
    :param activity_key: Activity column.
    :param timestamp_key: Timestamp column.
    :param start_timestamp_key: Start timestamp column.
    :param timest_format: Timestamp format provided to Pandas.
    :return: A formatted dataframe (Pandas DataFrame or Polars LazyFrame).
    :rtype: Any

    .. code-block:: python3

        import pandas as pd
        import pm4py

        dataframe = pd.read_csv('event_log.csv')
        dataframe = pm4py.format_dataframe(
            dataframe,
            case_id='case:concept:name',
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            start_timestamp_key='start_timestamp',
            timest_format='%Y-%m-%d %H:%M:%S'
        )
    """
    if timest_format is None:
        timest_format = constants.DEFAULT_TIMESTAMP_PARSE_FORMAT

    if is_polars_lazyframe(df):
        import polars as pl  # type: ignore[import-untyped]

        lf = df
        schema = lf.collect_schema()
        column_names = schema.names()
        required_columns = (case_id, activity_key, timestamp_key)
        for col in required_columns:
            if col not in column_names:
                raise Exception(f"{col} column is not in the dataframe!")

        def refresh_schema():
            nonlocal lf, schema, column_names
            schema = lf.collect_schema()
            column_names = schema.names()

        def drop_if_present(col_name):
            nonlocal lf
            if col_name in column_names:
                lf = lf.drop(col_name)
                refresh_schema()

        if (
            case_id != constants.CASE_CONCEPT_NAME
            or constants.CASE_CONCEPT_NAME not in column_names
        ):
            drop_if_present(constants.CASE_CONCEPT_NAME)
            lf = lf.with_columns(
                pl.col(case_id).alias(constants.CASE_CONCEPT_NAME)
            )
            refresh_schema()
        if (
            activity_key != xes_constants.DEFAULT_NAME_KEY
            or xes_constants.DEFAULT_NAME_KEY not in column_names
        ):
            drop_if_present(xes_constants.DEFAULT_NAME_KEY)
            lf = lf.with_columns(
                pl.col(activity_key).alias(xes_constants.DEFAULT_NAME_KEY)
            )
            refresh_schema()
        if (
            timestamp_key != xes_constants.DEFAULT_TIMESTAMP_KEY
            or xes_constants.DEFAULT_TIMESTAMP_KEY not in column_names
        ):
            drop_if_present(xes_constants.DEFAULT_TIMESTAMP_KEY)
            lf = lf.with_columns(
                pl.col(timestamp_key).alias(xes_constants.DEFAULT_TIMESTAMP_KEY)
            )
            refresh_schema()

        if start_timestamp_key in column_names:
            lf = lf.with_columns(
                pl.col(start_timestamp_key).alias(
                    xes_constants.DEFAULT_START_TIMESTAMP_KEY
                )
            )
            refresh_schema()

        timestamp_targets = [
            col
            for col in (
                xes_constants.DEFAULT_TIMESTAMP_KEY,
                xes_constants.DEFAULT_START_TIMESTAMP_KEY,
            )
            if col in column_names
        ]

        schema = lf.collect_schema()
        for col in timestamp_targets:
            dtype = schema.get(col)
            expr = pl.col(col)
            if dtype != pl.Datetime:
                expr = expr.cast(pl.Utf8).str.strptime(
                    pl.Datetime,
                    format=timest_format,
                    strict=False,
                    exact=False,
                )
            expr = expr.dt.replace_time_zone("UTC")
            lf = lf.with_columns(expr.alias(col))
        refresh_schema()

        lf = lf.filter(
            pl.col(constants.CASE_CONCEPT_NAME).is_not_null()
            & pl.col(xes_constants.DEFAULT_NAME_KEY).is_not_null()
            & pl.col(xes_constants.DEFAULT_TIMESTAMP_KEY).is_not_null()
        )

        lf = lf.with_columns(
            pl.col(constants.CASE_CONCEPT_NAME).cast(pl.Utf8),
            pl.col(xes_constants.DEFAULT_NAME_KEY).cast(pl.Utf8),
        )

        lf = pandas_utils.insert_index(
            lf, INDEX_COLUMN, copy_dataframe=False
        )
        lf = lf.sort(
            [
                constants.CASE_CONCEPT_NAME,
                xes_constants.DEFAULT_TIMESTAMP_KEY,
                INDEX_COLUMN,
            ]
        )
        lf = pandas_utils.insert_index(
            lf, INDEX_COLUMN, copy_dataframe=False
        )
        lf = pandas_utils.insert_case_index(
            lf,
            CASE_INDEX_COLUMN,
            copy_dataframe=False,
        )
        lf = lf.collect().lazy()
        return lf

    from pm4py.objects.log.util import dataframe_utils

    if case_id not in df.columns:
        raise Exception(case_id + " column (case ID) is not in the dataframe!")
    if activity_key not in df.columns:
        raise Exception(
            activity_key + " column (activity) is not in the dataframe!"
        )
    if timestamp_key not in df.columns:
        raise Exception(
            timestamp_key + " column (timestamp) is not in the dataframe!"
        )
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
    # Makes sure that the timestamps column are of timestamp type
    df = dataframe_utils.convert_timestamp_columns_in_df(
        df, timest_format=timest_format
    )
    # Drop NaN(s) in the main columns (case ID, activity, timestamp) to ensure
    # functioning of the algorithms
    prev_length = len(df)
    df = df.dropna(
        subset={
            constants.CASE_CONCEPT_NAME,
            xes_constants.DEFAULT_NAME_KEY,
            xes_constants.DEFAULT_TIMESTAMP_KEY,
        },
        how="any",
    )

    if len(df) < prev_length:
        if constants.SHOW_INTERNAL_WARNINGS:
            warnings.warn(
                "Some rows of the Pandas data frame have been removed because of empty case IDs, activity labels, or timestamps to ensure the correct functioning of PM4Py's algorithms."
            )

    # Make sure the case ID column is of string type
    df[constants.CASE_CONCEPT_NAME] = df[constants.CASE_CONCEPT_NAME].astype(
        "string"
    )
    # Make sure the activity column is of string type
    df[xes_constants.DEFAULT_NAME_KEY] = df[
        xes_constants.DEFAULT_NAME_KEY
    ].astype("string")
    # Set an index column
    df = pandas_utils.insert_index(df, INDEX_COLUMN, copy_dataframe=False)
    # Sorts the dataframe
    df = df.sort_values(
        [
            constants.CASE_CONCEPT_NAME,
            xes_constants.DEFAULT_TIMESTAMP_KEY,
            INDEX_COLUMN,
        ]
    )
    # Re-set the index column
    df = pandas_utils.insert_index(df, INDEX_COLUMN, copy_dataframe=False)
    # Sets the index column in the dataframe
    df = pandas_utils.insert_case_index(
        df, CASE_INDEX_COLUMN, copy_dataframe=False
    )
    # Sets the properties
    if not hasattr(df, "attrs"):
        # Legacy (Python 3.6) support
        df.attrs = {}
    if start_timestamp_key in df.columns:
        df[xes_constants.DEFAULT_START_TIMESTAMP_KEY] = df[start_timestamp_key]
        df.attrs[constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] = (
            xes_constants.DEFAULT_START_TIMESTAMP_KEY
        )
    df.attrs[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = (
        xes_constants.DEFAULT_NAME_KEY
    )
    df.attrs[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = (
        xes_constants.DEFAULT_TIMESTAMP_KEY
    )
    df.attrs[constants.PARAMETER_CONSTANT_GROUP_KEY] = (
        xes_constants.DEFAULT_GROUP_KEY
    )
    df.attrs[constants.PARAMETER_CONSTANT_TRANSITION_KEY] = (
        xes_constants.DEFAULT_TRANSITION_KEY
    )
    df.attrs[constants.PARAMETER_CONSTANT_RESOURCE_KEY] = (
        xes_constants.DEFAULT_RESOURCE_KEY
    )
    df.attrs[constants.PARAMETER_CONSTANT_CASEID_KEY] = (
        constants.CASE_CONCEPT_NAME
    )
    return df


def rebase(
    log_obj: Union[EventLog, EventStream, pd.DataFrame],
    case_id: str = constants.CASE_CONCEPT_NAME,
    activity_key: str = xes_constants.DEFAULT_NAME_KEY,
    timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
    start_timestamp_key: str = xes_constants.DEFAULT_START_TIMESTAMP_KEY,
    timest_format: Optional[str] = None,
) -> Union[EventLog, EventStream, pd.DataFrame]:
    """
    Re-bases the log object by changing the case ID, activity, and timestamp attributes.

    :param log_obj: Log object.
    :param case_id: Case identifier.
    :param activity_key: Activity.
    :param timestamp_key: Timestamp.
    :param start_timestamp_key: Start timestamp.
    :param timest_format: Timestamp format provided to Pandas.
    :return: A re-based log object.
    :rtype: Union[EventLog, EventStream, pd.DataFrame].

    .. code-block:: python3

        import pm4py

        rebased_dataframe = pm4py.rebase(
            dataframe,
            case_id='case:concept:name',
            activity_key='concept:name',
            timestamp_key='time:timestamp',
            start_timestamp_key='start_timestamp',
            timest_format='%Y-%m-%d %H:%M:%S'
        )
    """
    import pm4py

    __event_log_deprecation_warning(log_obj)

    if is_polars_lazyframe(log_obj):
        check_pandas_dataframe_columns(log_obj)
    elif check_is_pandas_dataframe(log_obj):
        check_pandas_dataframe_columns(log_obj)

    if is_polars_lazyframe(log_obj):
        return format_dataframe(
            log_obj,
            case_id=case_id,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            start_timestamp_key=start_timestamp_key,
            timest_format=timest_format,
        )
    elif check_is_pandas_dataframe(log_obj):
        return format_dataframe(
            log_obj,
            case_id=case_id,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            start_timestamp_key=start_timestamp_key,
            timest_format=timest_format,
        )
    elif isinstance(log_obj, EventLog):
        log_obj = pm4py.convert_to_dataframe(log_obj)
        log_obj = format_dataframe(
            log_obj,
            case_id=case_id,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            start_timestamp_key=start_timestamp_key,
            timest_format=timest_format,
        )
        from pm4py.objects.conversion.log import converter

        return converter.apply(
            log_obj, variant=converter.Variants.TO_EVENT_LOG
        )
    elif isinstance(log_obj, EventStream):
        log_obj = pm4py.convert_to_dataframe(log_obj)
        log_obj = format_dataframe(
            log_obj,
            case_id=case_id,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            start_timestamp_key=start_timestamp_key,
            timest_format=timest_format,
        )
        return pm4py.convert_to_event_stream(log_obj)


def parse_process_tree(tree_string: str) -> ProcessTree:
    """
    Parses a process tree from a string.

    :param tree_string: String representing a process tree (e.g., "-> ( 'A', O ( 'B', 'C' ), 'D' )"). Operators are '->' for sequence, '+' for parallel, 'X' for XOR choice, '*' for binary loop, and 'O' for choice.
    :return: A ProcessTree object.
    :rtype: ProcessTree

    .. code-block:: python3

        import pm4py

        process_tree = pm4py.parse_process_tree("-> ( 'A', O ( 'B', 'C' ), 'D' )")
    """
    from pm4py.objects.process_tree.utils.generic import parse

    return parse(tree_string)


def parse_powl_model_string(powl_string: str) -> POWL:
    """
    Parses a POWL model from a string representation of the process model
    (with the same format as the __repr__ and __str__ methods of the POWL model).

    :param powl_string: POWL model expressed as a string (__repr__ of the POWL model).
    :return: A POWL object.
    :rtype: POWL

    .. code-block:: python3

        import pm4py

        powl_model = pm4py.parse_powl_model_string('PO=(nodes={ NODE1, NODE2, NODE3 }, order={ NODE1-->NODE2 })')
        print(powl_model)
    """
    from pm4py.objects.powl import parser

    return parser.parse_powl_model_string(powl_string)


def serialize(*args) -> Tuple[str, bytes]:
    """
    Serializes a PM4Py object into a bytes string.

    :param args: PM4Py object(s) to serialize. Supported types include:
                 - An EventLog object.
                 - A Pandas DataFrame object.
                 - A tuple consisting of (PetriNet, Marking, Marking).
                 - A ProcessTree object.
                 - A BPMN object.
                 - A DFG, including the dictionary of directly-follows relations, start activities, and end activities.
    :return: A tuple containing the serialization type as a string and the serialized bytes.
    :rtype: Tuple[str, bytes]

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

        return (
            constants.AvailableSerializations.EVENT_LOG.value,
            xes_exporter.serialize(*args),
        )
    elif pandas_utils.check_is_pandas_dataframe(args[0]):
        from io import BytesIO

        buffer = BytesIO()
        args[0].to_parquet(buffer)
        return (
            constants.AvailableSerializations.DATAFRAME.value,
            buffer.getvalue(),
        )
    elif len(args) == 3 and type(args[0]) is PetriNet:
        from pm4py.objects.petri_net.exporter import exporter as petri_exporter

        return (
            constants.AvailableSerializations.PETRI_NET.value,
            petri_exporter.serialize(*args),
        )
    elif type(args[0]) is ProcessTree:
        from pm4py.objects.process_tree.exporter import (
            exporter as tree_exporter,
        )

        return (
            constants.AvailableSerializations.PROCESS_TREE.value,
            tree_exporter.serialize(*args),
        )
    elif type(args[0]) is BPMN:
        from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter

        return (
            constants.AvailableSerializations.BPMN.value,
            bpmn_exporter.serialize(*args),
        )
    elif len(args) == 3 and (
        isinstance(args[0], dict) or isinstance(args[0], Counter)
    ):
        from pm4py.objects.dfg.exporter import exporter as dfg_exporter

        return (
            constants.AvailableSerializations.DFG.value,
            dfg_exporter.serialize(
                args[0],
                parameters={
                    "start_activities": args[1],
                    "end_activities": args[2],
                },
            ),
        )


def deserialize(ser_obj: Tuple[str, bytes]) -> Any:
    """
    Deserializes a bytes string back into a PM4Py object.

    :param ser_obj: Serialized object as a tuple, consisting of a string indicating the type of the object and a bytes string representing the serialization.
    :return: The deserialized PM4Py object.
    :rtype: Any

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
        from pm4py.objects.process_tree.importer import (
            importer as tree_importer,
        )

        return tree_importer.deserialize(ser_obj[1])
    elif ser_obj[0] == constants.AvailableSerializations.BPMN.value:
        from pm4py.objects.bpmn.importer import importer as bpmn_importer

        return bpmn_importer.deserialize(ser_obj[1])
    elif ser_obj[0] == constants.AvailableSerializations.DFG.value:
        from pm4py.objects.dfg.importer import importer as dfg_importer

        return dfg_importer.deserialize(ser_obj[1])


def get_properties(
    log,
    activity_key: str = "concept:name",
    timestamp_key: str = "time:timestamp",
    case_id_key: str = "case:concept:name",
    resource_key: str = "org:resource",
    group_key: Optional[str] = None,
    start_timestamp_key: Optional[str] = None,
    **kwargs
):
    """
    Retrieves the properties from a log object.

    :param log: Log object.
    :param activity_key: Attribute to be used for the activity.
    :param timestamp_key: Attribute to be used for the timestamp.
    :param start_timestamp_key: (Optional) Attribute to be used for the start timestamp.
    :param case_id_key: Attribute to be used as case identifier.
    :param resource_key: (Optional) Attribute to be used as resource.
    :param group_key: (Optional) Attribute to be used as group identifier.
    :param kwargs: Additional keyword arguments.
    :return: A dictionary of properties.
    :rtype: Dict
    """
    __event_log_deprecation_warning(log)

    from copy import copy

    parameters = (
        copy(log.properties)
        if hasattr(log, "properties")
        else copy(log.attrs) if hasattr(log, "attrs") else {}
    )

    if activity_key is not None:
        parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
        parameters[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = activity_key

    if timestamp_key is not None:
        parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = timestamp_key

    if start_timestamp_key is not None:
        parameters[constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] = (
            start_timestamp_key
        )

    if case_id_key is not None:
        parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] = case_id_key

    if resource_key is not None:
        parameters[constants.PARAMETER_CONSTANT_RESOURCE_KEY] = resource_key

    if group_key is not None:
        parameters[constants.PARAMETER_CONSTANT_GROUP_KEY] = group_key

    for k, v in kwargs.items():
        parameters[k] = v

    return parameters


@deprecation.deprecated(
    deprecated_in="2.3.0",
    removed_in="3.0.0",
    details="This method will be removed in a future release. Please use the method-specific arguments.",
)
def set_classifier(
    log,
    classifier,
    classifier_attribute=constants.DEFAULT_CLASSIFIER_ATTRIBUTE,
):
    """
    Sets the specified classifier on an existing event log.

    :param log: Log object.
    :param classifier: Classifier to set. It can be:
                       - A list of event attributes.
                       - A single event attribute.
                       - A classifier stored in the "classifiers" of the log object.
    :param classifier_attribute: The attribute of the event that will store the concatenation of the attribute values for the given classifier.
    :return: The updated log object as an EventLog or Pandas DataFrame.
    :rtype: Union[EventLog, pd.DataFrame]
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
                event[classifier_attribute] = "+".join(
                    [str(event[x]) for x in classifier]
                )
        log.properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = (
            classifier_attribute
        )
        log.properties[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = (
            classifier_attribute
        )
    elif pandas_utils.check_is_pandas_dataframe(log):
        log[classifier_attribute] = log[classifier[0]]
        for i in range(1, len(classifier)):
            log[classifier_attribute] = (
                log[classifier_attribute] + "+" + log[classifier[i]]
            )
        log.attrs[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = (
            classifier_attribute
        )
        log.attrs[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = (
            classifier_attribute
        )
    else:
        raise Exception(
            "Setting classifier is not defined for this class of objects"
        )

    return log


def parse_event_log_string(
    traces: Collection[str],
    sep: str = ",",
    activity_key: str = xes_constants.DEFAULT_NAME_KEY,
    timestamp_key: str = xes_constants.DEFAULT_TIMESTAMP_KEY,
    case_id_key: str = constants.CASE_CONCEPT_NAME,
    return_legacy_log_object: bool = constants.DEFAULT_READ_XES_LEGACY_OBJECT,
) -> Union[EventLog, pd.DataFrame]:
    """
    Parses a collection of traces expressed as strings (e.g., ["A,B,C,D", "A,C,B,D", "A,D"]) into a log object.

    :param traces: Collection of traces expressed as strings.
    :param sep: Separator used to split the activities in a string trace.
    :param activity_key: The attribute to be used as activity.
    :param timestamp_key: The attribute to be used as timestamp.
    :param case_id_key: The attribute to be used as case identifier.
    :param return_legacy_log_object: If True, returns a legacy log object (EventLog). If False, returns a Pandas DataFrame. Default is False.
    :return: A log object, either as a legacy EventLog or a Pandas DataFrame.
    :rtype: Union[EventLog, pd.DataFrame]

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
            timestamps.append(
                strpfromiso.fix_naivety(
                    datetime.datetime.fromtimestamp(this_timest)
                )
            )
            this_timest += 1

    dataframe = pandas_utils.instantiate_dataframe(
        {
            case_id_key: cases,
            activity_key: activitiess,
            timestamp_key: timestamps,
        }
    )

    if return_legacy_log_object:
        import pm4py

        return pm4py.convert_to_event_log(dataframe, case_id_key=case_id_key)

    return dataframe


def project_on_event_attribute(
    log: Union[EventLog, pd.DataFrame],
    attribute_key=xes_constants.DEFAULT_NAME_KEY,
    case_id_key=None,
) -> List[List[str]]:
    """
    Projects the event log onto a specified event attribute. The result is a
    list containing a list for each case, where each case is represented as a
    list of values for the specified attribute.

    **Example**:

    .. code-block:: python

        pm4py.project_on_event_attribute(log, "concept:name")

    **Output**:

    .. code-block:: python

        [
            ['register request', 'examine casually', 'check ticket', 'decide', 'reinitiate request', 'examine thoroughly', 'check ticket', 'decide', 'pay compensation'],
            ['register request', 'check ticket', 'examine casually', 'decide', 'pay compensation'],
            ['register request', 'examine thoroughly', 'check ticket', 'decide', 'reject request'],
            ['register request', 'examine casually', 'check ticket', 'decide', 'pay compensation'],
            ['register request', 'examine casually', 'check ticket', 'decide', 'reinitiate request', 'check ticket', 'examine casually', 'decide', 'reinitiate request', 'examine casually', 'check ticket', 'decide', 'reject request'],
            ['register request', 'check ticket', 'examine thoroughly', 'decide', 'reject request']
        ]

    :param log: Event log or Pandas DataFrame.
    :param attribute_key: The attribute to be used for projection.
    :param case_id_key: (Optional) The attribute to be used as case identifier.
    :return: A list of lists containing the projected attribute values for each case.
    :rtype: List[List[str]]

    .. code-block:: python3

        import pm4py

        list_list_activities = pm4py.project_on_event_attribute(dataframe, 'concept:name')
    """
    __event_log_deprecation_warning(log)

    output = []
    if check_is_pandas_dataframe(log):
        if is_polars_lazyframe(log):
            check_pandas_dataframe_columns(
                log, activity_key=attribute_key, case_id_key=case_id_key
            )

            import polars as pl  # type: ignore[import-untyped]

            lf = log
            schema = lf.collect_schema()
            column_names = schema.names()

            case_column = (
                case_id_key if case_id_key is not None else constants.CASE_CONCEPT_NAME
            )
            if case_column not in column_names:
                raise Exception(
                    f"The specified case identifier column '{case_column}' is not present in the Polars LazyFrame."
                )

            activity_column = (
                attribute_key if attribute_key is not None else xes_constants.DEFAULT_NAME_KEY
            )
            has_activity_column = (
                activity_column is not None and activity_column in column_names
            )

            index_column = constants.DEFAULT_INDEX_KEY
            if index_column not in column_names:
                index_column = "__pm4py_row_index__"
                lf = lf.with_row_index(index_column)
                schema = lf.collect_schema()
                column_names = schema.names()

            sort_columns = [case_column]
            if xes_constants.DEFAULT_TIMESTAMP_KEY in column_names:
                sort_columns.append(xes_constants.DEFAULT_TIMESTAMP_KEY)
            if index_column in column_names:
                sort_columns.append(index_column)

            lf_sorted = lf.sort(sort_columns, maintain_order=True)

            if has_activity_column:
                lf_selected = lf_sorted.select(
                    pl.col(case_column).alias("__pm_case__"),
                    pl.col(activity_column).alias("__pm_attr__"),
                )
            else:
                lf_selected = lf_sorted.select(
                    pl.col(case_column).alias("__pm_case__"),
                    pl.lit(None).alias("__pm_attr__"),
                )

            aggregated = (
                lf_selected.group_by("__pm_case__", maintain_order=True)
                .agg(pl.col("__pm_attr__").alias("__pm_attr__"))
                .collect()
            )

            output.extend(aggregated["__pm_attr__"].to_list())
        else:
            check_pandas_dataframe_columns(log)
            from pm4py.streaming.conversion import from_pandas

            parameters = {from_pandas.Parameters.ACTIVITY_KEY: attribute_key}
            if case_id_key is not None:
                parameters[from_pandas.Parameters.CASE_ID_KEY] = case_id_key
            it = from_pandas.apply(log, parameters=parameters)
            for trace in it:
                output.append(
                    [
                        (
                            x[xes_constants.DEFAULT_NAME_KEY]
                            if xes_constants.DEFAULT_NAME_KEY is not None
                            else None
                        )
                        for x in trace
                    ]
                )
    else:
        for trace in log:
            output.append(
                [
                    x[attribute_key] if attribute_key is not None else None
                    for x in trace
                ]
            )
    return output


def sample_cases(
    log: Union[EventLog, pd.DataFrame],
    num_cases: int,
    case_id_key: str = "case:concept:name",
) -> Union[EventLog, pd.DataFrame]:
    """
    Randomly samples a given number of cases from the event log.

    :param log: Event log or Pandas DataFrame.
    :param num_cases: Number of cases to sample.
    :param case_id_key: Attribute to be used as case identifier.
    :return: A sampled log object, either as an EventLog or a Pandas DataFrame.
    :rtype: Union[EventLog, pd.DataFrame]

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


def sample_events(
    log: Union[EventStream, OCEL], num_events: int
) -> Union[EventStream, OCEL, pd.DataFrame]:
    """
    Randomly samples a given number of events from the event log.

    :param log: Event stream, OCEL, or Pandas DataFrame.
    :param num_events: Number of events to sample.
    :return: A sampled log object, either as an EventStream, OCEL, or Pandas DataFrame.
    :rtype: Union[EventStream, OCEL, pd.DataFrame]

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

        return sampling.sample_ocel_events(
            log, parameters={"num_entities": num_events}
        )
    elif check_is_pandas_dataframe(log):
        return log.sample(n=num_events)


def __event_log_deprecation_warning(log):
    if constants.SHOW_EVENT_LOG_DEPRECATION and not hasattr(
        log, "deprecation_warning_shown"
    ):
        if constants.SHOW_INTERNAL_WARNINGS:
            if isinstance(log, EventLog) or isinstance(log, Trace):
                warnings.warn(
                    "The EventLog class has been deprecated and will be removed in a future release."
                )
                log.deprecation_warning_shown = True
            elif isinstance(log, Trace):
                warnings.warn(
                    "The Trace class has been deprecated and will be removed in a future release."
                )
                log.deprecation_warning_shown = True
            elif isinstance(log, EventStream):
                warnings.warn(
                    "The EventStream class has been deprecated and will be removed in a future release."
                )
                log.deprecation_warning_shown = True


def __rustxes_usage_warning():
    if (
        Shared.RUSTXES_WARNING_SHOWN is False
        and constants.SHOW_INTERNAL_WARNINGS
    ):
        backend_name = get_rustxes_backend_name()
        message = (
            "Install the optional requirement `r4pm` to import/export files faster. `rustxes` remains supported as a fallback."
        )
        if backend_name == "r4pm":
            message = (
                "In the current version, the import/export operation uses `r4pm` by default for importing/exporting files faster."
            )
        elif backend_name == "rustxes":
            message = (
                "In the current version, the import/export operation uses `rustxes` by default for importing/exporting files faster. Install `r4pm` to use the replacement backend."
            )
        warnings.warn(
            message
        )
        Shared.RUSTXES_WARNING_SHOWN = True

def __rustxes_non_usage_warning():
    if (
        Shared.RUSTXES_WARNING_SHOWN is False
        and constants.SHOW_INTERNAL_WARNINGS
    ):
        backend_name = get_rustxes_backend_name()
        message = (
            "Install the optional requirement `r4pm` to import/export files faster. `rustxes` remains supported as a fallback."
        )
        if backend_name == "r4pm":
            message = (
                "The import/export operation is using the line-by-line backend. `r4pm` is available if you want faster import/export."
            )
        elif backend_name == "rustxes":
            message = (
                "The import/export operation is using the line-by-line backend. Install `r4pm` to use the replacement fast backend. `rustxes` remains supported as a fallback."
            )
        warnings.warn(
            message
        )
        Shared.RUSTXES_WARNING_SHOWN = True


def __event_log_filtering_level_warning():
    if Shared.FILTERING_LEVEL_WARNING_SHOWN is False:
        warnings.warn("The filtering operates at the case level (i.e., cases that contain at least one event satisfying the filter are retained in their entirety).")
        Shared.FILTERING_LEVEL_WARNING_SHOWN = True
