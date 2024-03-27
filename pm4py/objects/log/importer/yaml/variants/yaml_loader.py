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
from enum import Enum
import importlib
import sys, os

from pm4py.util import constants, xes_constants, exec_utils
from pm4py.objects.log.util import sorting
from pm4py.objects.log.obj import EventLog, Trace, Event
import gzip
import yaml
from yaml import SafeLoader, FullLoader
from yaml.cyaml import CSafeLoader, CFullLoader


class LoaderType(Enum):
    SAFE_PYYAML = SafeLoader
    FULL_PYYAML = FullLoader
    C_SAFE_PYYAML = CSafeLoader
    C_FULL_PYYAML = CFullLoader


class Parameters(Enum):
    TIMESTAMP_SORT = "timestamp_sort"
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    REVERSE_SORT = "reverse_sort"
    MAX_TRACES = "max_traces"
    SHOW_PROGRESS_BAR = "show_progress_bar"
    DECOMPRESS_SERIALIZATION = "decompress_serialization"
    ENCODING = "encoding"


def apply(
    filename: str,
    variant: LoaderType = LoaderType.C_SAFE_PYYAML,
    parameters: Parameters = None,
):
    """
    Imports an XES-YAML file into a log object

    Parameters
    ----------
    filename:
        Absolute filename
    parameters
        Parameters of the algorithm, including
            Parameters.TIMESTAMP_SORT -> Specify if we should sort log by timestamp
            Parameters.TIMESTAMP_KEY -> If sort is enabled, then sort the log by using this key
            Parameters.REVERSE_SORT -> Specify in which direction the log should be sorted
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)
            Parameters.SHOW_PROGRESS_BAR -> Enables/disables the progress bar (default: True)
            Parameters.ENCODING -> regulates the encoding (default: utf-8)

    Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        A log
    """
    return import_from_context_with_progress(
        filename=filename, variant=variant, parameters=parameters
    )


def import_from_context_with_progress(
    filename: str, variant: LoaderType, parameters: Parameters = None
):
    if parameters is None:
        parameters = {}

    max_no_traces_to_import = exec_utils.get_param_value(
        Parameters.MAX_TRACES, parameters, sys.maxsize
    )
    timestamp_sort = exec_utils.get_param_value(
        Parameters.TIMESTAMP_SORT, parameters, False
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY
    )
    reverse_sort = exec_utils.get_param_value(
        Parameters.REVERSE_SORT, parameters, False
    )
    show_progress_bar = exec_utils.get_param_value(
        Parameters.SHOW_PROGRESS_BAR, parameters, constants.SHOW_PROGRESS_BAR
    )
    encoding = exec_utils.get_param_value(
        Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING
    )
    is_compressed = filename.lower().endswith(".gz")

    progress = None

    total_size_bytes = os.path.getsize(filename)

    log = EventLog()

    with (
        gzip.open(filename, "rb")
        if is_compressed
        else open(filename, "r", encoding=encoding)
    ) as yaml_file:
        if importlib.util.find_spec("tqdm") and show_progress_bar:
            from tqdm.auto import tqdm

            progress = tqdm(
                total=total_size_bytes,
                desc="parsing log, completed events/documents :: ",
                # bar_format=format_custom,
                unit="B",
                unit_divisor=1048576,
            )

        context = yaml_load(yaml_file, loader=variant)

        for elem, document in enumerate(context):
            if document is None:
                continue

            log_context = document.get(xes_constants.TAG_LOG)
            event_context = document.get(xes_constants.TAG_EVENT)
            trace_context = document.get(xes_constants.TAG_TRACE)

            if elem == 0 and log_context is None:
                raise SyntaxError("file contains no Log object")

            if len(set(document.keys())) != 1:
                raise SyntaxError("YAML document contains more than one root key")

            if log_context is not None:
                # parse Log document
                log = parse_log_object(log_context=log_context)

            elif event_context is not None:
                # parse Event document
                event = parse_event_object(
                    event_context=event_context,
                )

                if len(log) == 0:
                    log.append(Trace())

                log[-1].append(event)

            # parse Trace document
            elif trace_context is not None:
                trace = parse_trace_object(trace_context=trace_context)
                log.append(trace)

            if progress is not None:
                current_position_in_bytes = yaml_file.tell()
                progress.update(current_position_in_bytes - progress.n)

            del log_context, event_context, trace_context

        # gracefully close progress bar
        if progress is not None:
            progress.close()

    del context, progress

    if timestamp_sort:
        log = sorting.sort_timestamp(
            log, timestamp_key=timestamp_key, reverse_sort=reverse_sort
        )

    # sets the activity key as default classifier in the log's properties
    log.properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = (
        xes_constants.DEFAULT_NAME_KEY
    )
    log.properties[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = (
        xes_constants.DEFAULT_NAME_KEY
    )
    # sets the default timestamp key
    log.properties[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = (
        xes_constants.DEFAULT_TIMESTAMP_KEY
    )
    # sets the default resource key
    log.properties[constants.PARAMETER_CONSTANT_RESOURCE_KEY] = (
        xes_constants.DEFAULT_RESOURCE_KEY
    )
    # sets the default transition key
    log.properties[constants.PARAMETER_CONSTANT_TRANSITION_KEY] = (
        xes_constants.DEFAULT_TRANSITION_KEY
    )
    # sets the default group key
    log.properties[constants.PARAMETER_CONSTANT_GROUP_KEY] = (
        xes_constants.DEFAULT_GROUP_KEY
    )

    return log


def yaml_load(stream, loader: LoaderType = LoaderType.SAFE_PYYAML):
    """
    Load a YAML file

    Parameters
    ----------
    stream
        YAML stream
    loader
        Loader type

    Returns
    ----------
    document
        YAML document
    """
    return yaml.load_all(stream, Loader=loader.value)


def parse_log_object(log_context: dict) -> EventLog:
    """
    Parse a YAML document containing a Log object

    Parameters
    --------------
    document
        YAML Log document

    Returns
    --------------
    log
        Event log
    """
    log: EventLog = EventLog()

    for key, value in log_context.items():
        if key == xes_constants.TAG_EXTENSION:
            for ext_key, ext_value in value.items():
                log.extensions[ext_key] = {
                    xes_constants.KEY_PREFIX: ext_key,
                    xes_constants.KEY_URI: ext_value,
                }

        elif key == xes_constants.TAG_GLOBAL:
            global_event_attributes = value.get(xes_constants.TAG_EVENT)
            global_trace_attributes = value.get(xes_constants.TAG_TRACE)

            if global_event_attributes is not None:

                for event_attr_key, event_attr_value in global_event_attributes.items():
                    log.omni_present[xes_constants.TAG_EVENT][
                        event_attr_key
                    ] = event_attr_value

            if global_trace_attributes is not None:
                for trace_attr_key, trace_attr_value in global_trace_attributes.items():
                    log.omni_present[xes_constants.TAG_TRACE][
                        trace_attr_key
                    ] = trace_attr_value

        else:
            parse_and_add_attribute(log.attributes, key, value)

        return log


def parse_event_object(event_context: dict) -> Event:
    """
    Parse the Event object
    """

    event: Event = Event()

    for event_att_key, event_att_value in event_context.items():
        if event_att_value is None:
            event[event_att_key] = ""
        else:
            parse_and_add_attribute(event, event_att_key, event_att_value)

    return event


def parse_trace_object(trace_context: dict) -> Trace:
    """
    Parse the Event object
    """

    trace: Trace = Trace()

    for trace_att_key, trace_att_value in trace_context.items():
        if trace_att_value is None:
            trace[trace_att_key] = ""
        else:
            parse_and_add_attribute(trace.attributes, trace_att_key, trace_att_value)

    return trace


def parse_and_add_attribute(store, attribute_key, attribute_value):

    if isinstance(attribute_value, dict):
        store[attribute_key] = {
            xes_constants.KEY_VALUE: attribute_key,
            xes_constants.KEY_CHILDREN: dict(),
        }

        for inner_key, inner_value in attribute_value.items():
            parse_and_add_attribute(
                store[attribute_key][xes_constants.KEY_CHILDREN],
                inner_key,
                inner_value,
            )

    elif isinstance(attribute_value, list):

        store[attribute_key] = {
            xes_constants.KEY_VALUE: None,
            xes_constants.KEY_CHILDREN: list(),  # items in list are tuples (key, value)
        }

        for list_item in attribute_value:
            composite_att = parse_composite_list_attribute([], list_item)
            store[attribute_key][xes_constants.KEY_CHILDREN].append(composite_att)

    else:
        if isinstance(store, list):
            store.append((attribute_key, attribute_value))

        else:
            store[attribute_key] = attribute_value


def parse_composite_list_attribute(parent, attribute):
    if isinstance(attribute, dict):
        composite_att = {
            xes_constants.KEY_VALUE: "",
            xes_constants.KEY_CHILDREN: dict(),
        }

        for inner_key, inner_value in attribute.items():
            composite_att[xes_constants.KEY_CHILDREN][inner_key] = (
                parse_composite_list_attribute(composite_att, inner_value)
            )

        if isinstance(parent, list):
            return ("", composite_att)

        else:
            return composite_att

    elif isinstance(attribute, list):
        pass

    else:
        return attribute
