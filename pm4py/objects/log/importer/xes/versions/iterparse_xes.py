import logging

from pm4py.util.dt_parsing import factory as dt_parse_factory
from lxml import etree

from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.objects.log.util import sorting
from pm4py.util import xes_constants

# ITERPARSE EVENTS
EVENT_END = 'end'
EVENT_START = 'start'


def import_log(filename, parameters=None):
    """
    Imports an XES file into a log object

    Parameters
    ----------
    filename:
        Absolute filename
    parameters
        Parameters of the algorithm, including
            timestamp_sort -> Specify if we should sort log by timestamp
            timestamp_key -> If sort is enabled, then sort the log by using this key
            reverse_sort -> Specify in which direction the log should be sorted
            index_trace_indexes -> Specify if trace indexes should be added as event attribute for each event
            max_no_traces_to_import -> Specify the maximum number of traces to import from the log
            (read in order in the XML file)

    Returns
    -------
    log : :class:`pm4py.log.log.EventLog`
        A log
    """

    if parameters is None:
        parameters = {}

    date_parser = dt_parse_factory.get()

    timestamp_sort = False
    timestamp_key = "time:timestamp"
    reverse_sort = False
    insert_trace_indexes = False
    max_no_traces_to_import = 1000000000

    if "timestamp_sort" in parameters:
        timestamp_sort = parameters["timestamp_sort"]
    if "timestamp_key" in parameters:
        timestamp_key = parameters["timestamp_key"]
    if "reverse_sort" in parameters:
        reverse_sort = parameters["reverse_sort"]
    if "insert_trace_indexes" in parameters:
        insert_trace_indexes = parameters["insert_trace_indexes"]
    if "max_no_traces_to_import" in parameters:
        max_no_traces_to_import = parameters["max_no_traces_to_import"]

    context = etree.iterparse(filename, events=['start', 'end'])

    log = None
    trace = None
    event = None

    tree = {}

    for tree_event, elem in context:
        if tree_event == EVENT_START:  # starting to read
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

        elif tree_event == EVENT_END:
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
                trace = None
                continue

            elif elem.tag.endswith(xes_constants.TAG_LOG):
                continue

    del context

    if timestamp_sort:
        log = sorting.sort_timestamp(log, timestamp_key=timestamp_key, reverse_sort=reverse_sort)
    if insert_trace_indexes:
        log.insert_trace_index_as_event_attribute()

    return log


def __parse_attribute(elem, store, key, value, tree):
    if len(elem.getchildren()) == 0:
        store[key] = value
    else:
        store[key] = {xes_constants.KEY_VALUE: value, xes_constants.KEY_CHILDREN: {}}
        if elem.getchildren()[0].tag.endswith(xes_constants.TAG_VALUES):
            tree[elem] = store[key][xes_constants.KEY_CHILDREN]
            tree[elem.getchildren()[0]] = tree[elem]
        else:
            tree[elem] = store[key][xes_constants.KEY_CHILDREN]
    return tree
