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
import gzip
import logging
import pkgutil
import sys
from enum import Enum
from io import BytesIO

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.log.util import sorting
from pm4py.util import exec_utils, constants
from pm4py.util import xes_constants
from pm4py.util.dt_parsing import parser as dt_parser


class Parameters(Enum):
    TIMESTAMP_SORT = "timestamp_sort"
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    REVERSE_SORT = "reverse_sort"
    MAX_TRACES = "max_traces"
    SHOW_PROGRESS_BAR = "show_progress_bar"
    DECOMPRESS_SERIALIZATION = "decompress_serialization"
    ENCODING = "encoding"


# ITERPARSE EVENTS
_EVENT_END = 'end'
_EVENT_START = 'start'


def count_traces(context):
    """
    Efficiently count the number of traces of a XES event log

    Parameters
    -------------
    context
        XML iterparse context
    Returns
    -------------
    num_traces
        Number of traces of the XES log
    """
    num_traces = 0

    for tree_event, elem in context:
        if tree_event == _EVENT_START:  # starting to read
            if elem.tag.endswith(xes_constants.TAG_TRACE):
                num_traces = num_traces + 1
        elem.clear()

    del context

    return num_traces


def import_from_context(context, num_traces, parameters=None):
    """
    Import a XES log from an iterparse context

    Parameters
    --------------
    context
        Iterparse context
    num_traces
        Number of traces of the XES log
    parameters
        Parameters of the algorithm

    Returns
    --------------
    log
        Event log
    """
    if parameters is None:
        parameters = {}

    max_no_traces_to_import = exec_utils.get_param_value(Parameters.MAX_TRACES, parameters, sys.maxsize)
    timestamp_sort = exec_utils.get_param_value(Parameters.TIMESTAMP_SORT, parameters, False)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                               xes_constants.DEFAULT_TIMESTAMP_KEY)
    reverse_sort = exec_utils.get_param_value(Parameters.REVERSE_SORT, parameters, False)
    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, True)

    date_parser = dt_parser.get()
    progress = None
    if pkgutil.find_loader("tqdm") and show_progress_bar:
        from tqdm.auto import tqdm
        progress = tqdm(total=num_traces, desc="parsing log, completed traces :: ")

    log = None
    trace = None
    event = None

    tree = {}

    for tree_event, elem in context:
        if tree_event == _EVENT_START:  # starting to read
            parent = tree[elem.getparent()] if elem.getparent() in tree else None

            if elem.tag.endswith(xes_constants.TAG_STRING):
                if parent is not None:
                    tree = __parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY),
                                             elem.get(xes_constants.KEY_VALUE), tree)
                continue

            elif elem.tag.endswith(xes_constants.TAG_DATE):
                try:
                    dt = date_parser.apply(elem.get(xes_constants.KEY_VALUE))
                    tree = __parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), dt, tree)
                except TypeError:
                    logging.info("failed to parse date: " + str(elem.get(xes_constants.KEY_VALUE)))
                except ValueError:
                    logging.info("failed to parse date: " + str(elem.get(xes_constants.KEY_VALUE)))
                continue

            elif elem.tag.endswith(xes_constants.TAG_EVENT):
                if event is not None:
                    raise SyntaxError('file contains <event> in another <event> tag')
                event = Event()
                tree[elem] = event
                continue

            elif elem.tag.endswith(xes_constants.TAG_TRACE):
                if len(log) >= max_no_traces_to_import:
                    break
                if trace is not None:
                    raise SyntaxError('file contains <trace> in another <trace> tag')
                trace = Trace()
                tree[elem] = trace.attributes
                continue

            elif elem.tag.endswith(xes_constants.TAG_FLOAT):
                if parent is not None:
                    try:
                        val = float(elem.get(xes_constants.KEY_VALUE))
                        tree = __parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), val, tree)
                    except ValueError:
                        logging.info("failed to parse float: " + str(elem.get(xes_constants.KEY_VALUE)))
                continue

            elif elem.tag.endswith(xes_constants.TAG_INT):
                if parent is not None:
                    try:
                        val = int(elem.get(xes_constants.KEY_VALUE))
                        tree = __parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), val, tree)
                    except ValueError:
                        logging.info("failed to parse int: " + str(elem.get(xes_constants.KEY_VALUE)))
                continue

            elif elem.tag.endswith(xes_constants.TAG_BOOLEAN):
                if parent is not None:
                    try:
                        val0 = elem.get(xes_constants.KEY_VALUE)
                        val = False
                        if str(val0).lower() == "true":
                            val = True
                        tree = __parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), val, tree)
                    except ValueError:
                        logging.info("failed to parse boolean: " + str(elem.get(xes_constants.KEY_VALUE)))
                continue

            elif elem.tag.endswith(xes_constants.TAG_LIST):
                if parent is not None:
                    # lists have no value, hence we put None as a value
                    tree = __parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), None, tree)
                continue

            elif elem.tag.endswith(xes_constants.TAG_ID):
                if parent is not None:
                    tree = __parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY),
                                             elem.get(xes_constants.KEY_VALUE), tree)
                continue

            elif elem.tag.endswith(xes_constants.TAG_EXTENSION):
                if log is None:
                    raise SyntaxError('extension found outside of <log> tag')
                if elem.get(xes_constants.KEY_NAME) is not None and elem.get(
                        xes_constants.KEY_PREFIX) is not None and elem.get(xes_constants.KEY_URI) is not None:
                    log.extensions[elem.get(xes_constants.KEY_NAME)] = {
                        xes_constants.KEY_PREFIX: elem.get(xes_constants.KEY_PREFIX),
                        xes_constants.KEY_URI: elem.get(xes_constants.KEY_URI)}
                continue

            elif elem.tag.endswith(xes_constants.TAG_GLOBAL):
                if log is None:
                    raise SyntaxError('global found outside of <log> tag')
                if elem.get(xes_constants.KEY_SCOPE) is not None:
                    log.omni_present[elem.get(xes_constants.KEY_SCOPE)] = {}
                    tree[elem] = log.omni_present[elem.get(xes_constants.KEY_SCOPE)]
                continue

            elif elem.tag.endswith(xes_constants.TAG_CLASSIFIER):
                if log is None:
                    raise SyntaxError('classifier found outside of <log> tag')
                if elem.get(xes_constants.KEY_KEYS) is not None:
                    classifier_value = elem.get(xes_constants.KEY_KEYS)
                    if "'" in classifier_value:
                        log.classifiers[elem.get(xes_constants.KEY_NAME)] = [x for x in classifier_value.split("'")
                                                                             if x.strip()]
                    else:
                        log.classifiers[elem.get(xes_constants.KEY_NAME)] = classifier_value.split()
                continue

            elif elem.tag.endswith(xes_constants.TAG_LOG):
                if log is not None:
                    raise SyntaxError('file contains > 1 <log> tags')
                log = EventLog()
                tree[elem] = log.attributes
                continue

        elif tree_event == _EVENT_END:
            if elem in tree:
                del tree[elem]
            elem.clear()
            if elem.getprevious() is not None:
                try:
                    del elem.getparent()[0]
                except TypeError:
                    pass

            if elem.tag.endswith(xes_constants.TAG_EVENT):
                if trace is not None:
                    trace.append(event)
                    event = None
                continue

            elif elem.tag.endswith(xes_constants.TAG_TRACE):
                log.append(trace)

                if progress is not None:
                    progress.update()

                trace = None
                continue

            elif elem.tag.endswith(xes_constants.TAG_LOG):
                continue

    # gracefully close progress bar
    if progress is not None:
        progress.close()
    del context, progress

    if timestamp_sort:
        log = sorting.sort_timestamp(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)

    # sets the activity key as default classifier in the log's properties
    log.properties[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_constants.DEFAULT_NAME_KEY
    log.properties[constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = xes_constants.DEFAULT_NAME_KEY
    # sets the default timestamp key
    log.properties[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_constants.DEFAULT_TIMESTAMP_KEY
    # sets the default resource key
    log.properties[constants.PARAMETER_CONSTANT_RESOURCE_KEY] = xes_constants.DEFAULT_RESOURCE_KEY
    # sets the default transition key
    log.properties[constants.PARAMETER_CONSTANT_TRANSITION_KEY] = xes_constants.DEFAULT_TRANSITION_KEY
    # sets the default group key
    log.properties[constants.PARAMETER_CONSTANT_GROUP_KEY] = xes_constants.DEFAULT_GROUP_KEY

    return log


def apply(filename, parameters=None):
    """
    Imports an XES file into a log object

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
    return import_log(filename, parameters)


def import_log(filename, parameters=None):
    """
    Imports an XES file into a log object

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
    from lxml import etree

    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)
    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, True)
    is_compressed = filename.lower().endswith(".gz")

    if pkgutil.find_loader("tqdm") and show_progress_bar:
        if is_compressed:
            f = gzip.open(filename, "rb")
        else:
            f = open(filename, "rb")
        context = etree.iterparse(f, events=[_EVENT_START, _EVENT_END], encoding=encoding)
        num_traces = count_traces(context)
    else:
        # avoid the iteration to calculate the number of traces is "tqdm" is not used
        num_traces = 0

    if is_compressed:
        f = gzip.open(filename, "rb")
    else:
        f = open(filename, "rb")
    context = etree.iterparse(f, events=[_EVENT_START, _EVENT_END], encoding=encoding)

    return import_from_context(context, num_traces, parameters=parameters)


def import_from_string(log_string, parameters=None):
    """
    Deserialize a text/binary string representing a XES log

    Parameters
    -----------
    log_string
        String that contains the XES
    parameters
        Parameters of the algorithm, including
            Parameters.TIMESTAMP_SORT -> Specify if we should sort log by timestamp
            Parameters.TIMESTAMP_KEY -> If sort is enabled, then sort the log by using this key
            Parameters.REVERSE_SORT -> Specify in which direction the log should be sorted
            Parameters.INSERT_TRACE_INDICES -> Specify if trace indexes should be added as event attribute for each event
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)
            Parameters.SHOW_PROGRESS_BAR -> Enables/disables the progress bar (default: True)
            Parameters.ENCODING -> regulates the encoding (default: utf-8)

    Returns
    -----------
    log
        Trace log object
    """
    from lxml import etree

    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, constants.DEFAULT_ENCODING)
    show_progress_bar = exec_utils.get_param_value(Parameters.SHOW_PROGRESS_BAR, parameters, True)
    decompress_serialization = exec_utils.get_param_value(Parameters.DECOMPRESS_SERIALIZATION, parameters, False)

    if type(log_string) is str:
        log_string = log_string.encode(constants.DEFAULT_ENCODING)

    if pkgutil.find_loader("tqdm") and show_progress_bar:
        # first iteration: count the number of traces
        b = BytesIO(log_string)
        if decompress_serialization:
            s = gzip.GzipFile(fileobj=b, mode="rb")
        else:
            s = b
        context = etree.iterparse(s, events=[_EVENT_START, _EVENT_END], encoding=encoding)
        num_traces = count_traces(context)
    else:
        # avoid the iteration to calculate the number of traces is "tqdm" is not used
        num_traces = 0

    # second iteration: actually read the content
    b = BytesIO(log_string)
    if decompress_serialization:
        s = gzip.GzipFile(fileobj=b, mode="rb")
    else:
        s = b
    context = etree.iterparse(s, events=[_EVENT_START, _EVENT_END], encoding=encoding)

    return import_from_context(context, num_traces, parameters=parameters)


def __parse_attribute(elem, store, key, value, tree):
    if len(elem.getchildren()) == 0:
        if type(store) is list:
            # changes to the store of lists: not dictionaries anymore
            # but pairs of key-values.
            store.append((key, value))
        else:
            store[key] = value
    else:
        if elem.getchildren()[0].tag.endswith(xes_constants.TAG_VALUES):
            store[key] = {xes_constants.KEY_VALUE: value, xes_constants.KEY_CHILDREN: list()}
            tree[elem] = store[key][xes_constants.KEY_CHILDREN]
            tree[elem.getchildren()[0]] = tree[elem]
        else:
            store[key] = {xes_constants.KEY_VALUE: value, xes_constants.KEY_CHILDREN: dict()}
            tree[elem] = store[key][xes_constants.KEY_CHILDREN]
    return tree
