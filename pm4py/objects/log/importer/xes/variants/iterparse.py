import logging
from enum import Enum

from lxml import etree

from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.log.util import sorting, index_attribute
from pm4py.objects.log.util import xes as xes_util
from pm4py.util import parameters as param_util
from pm4py.util import xes_constants
from pm4py.util.dt_parsing import parser as dt_parser

import pkgutil


class Parameters(Enum):
    TIMESTAMP_SORT = False
    TIMESTAMP_KEY = xes_util.DEFAULT_TIMESTAMP_KEY
    REVERSE_SORT = False
    INSERT_TRACE_INDICES = False
    MAX_TRACES = 1000000000


# ITERPARSE EVENTS
_EVENT_END = 'end'
_EVENT_START = 'start'


def apply(filename, parameters=None):
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
            Parameters.INSERT_TRACE_INDICES -> Specify if trace indexes should be added as event attribute for each event
            Parameters.MAX_TRACES -> Specify the maximum number of traces to import from the log (read in order in the XML file)

    Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        A log
    """

    parameters = dict() if parameters is None else parameters

    insert_trace_indexes = param_util.fetch(Parameters.INSERT_TRACE_INDICES, parameters)
    max_no_traces_to_import = param_util.fetch(Parameters.MAX_TRACES, parameters)

    date_parser = dt_parser.get()
    context = etree.iterparse(filename, events=[_EVENT_START, _EVENT_END])

    # check to see if log has a namespace before looking for traces  (but this might be more effort than worth)
    # but you could just assume that log use on the standard namespace desbried in XES
    # to only find elements that start a trace use tag="{http://www.xes-standard.org}trace"
    # or just use the {*} syntax to match to all namespaces with a trace element

    #count number of traces and setup progress bar
    no_trace = sum ( [ 1 for trace in  etree.iterparse(filename, events=[_EVENT_START],tag="{*}trace") ])

    # make tqdm facultative
    progress = None
    if pkgutil.find_loader("tqdm"):
        from tqdm.auto import tqdm
        progress = tqdm(total=no_trace,desc="parsing log, completed traces :: ")

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

                #update progress bar as we have a completed trace
                if progress is not None:
                    progress.update()

                trace = None
                continue

            elif elem.tag.endswith(xes_constants.TAG_LOG):
                continue
            
    #gracefully close progress bar
    if progress is not None:
        progress.close()
    del context, progress

    if Parameters.TIMESTAMP_SORT in parameters and parameters[Parameters.TIMESTAMP_SORT]:
        log = sorting.sort_timestamp(log,
                                     timestamp_key=param_util.fetch(Parameters.TIMESTAMP_KEY, parameters),
                                     reverse_sort=param_util.fetch(Parameters.REVERSE_SORT, parameters))
    if insert_trace_indexes:
        log = index_attribute.insert_event_index_as_event_attribute(log)

    return log


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
