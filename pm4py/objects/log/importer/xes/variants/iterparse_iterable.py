import logging
from enum import Enum

from pm4py.objects.log.log import EventLog, Trace, Event
from pm4py.util import xes_constants, exec_utils
from pm4py.util.dt_parsing import parser as dt_parser

import random


class Parameters(Enum):
    MAX_TRACES = "max_traces"
    SKIP_PROBABILITY = "skip_probability"


_EVENT_END = 'end'
_EVENT_START = 'start'


class IterableXesReader:
    def __init__(self, path, parameters=None):
        """
        Initialize the iterable log object

        Parameters
        -------------
        path
            Path to the XES log
        """
        if parameters is None:
            parameters = {}
        self.path = path
        self.date_parser = dt_parser.get()
        self.reset()

    def __iter__(self):
        """
        Starts the iteration
        """
        return self

    def __next__(self):
        """
        Gets the next element of the log
        """
        return self.read_trace()

    def reset(self):
        """
        Resets the iterator
        """
        # reset the variables
        from lxml import etree

        self.context = None
        self.tree = None
        # initialize the variables
        self.context = etree.iterparse(self.path, events=[_EVENT_START, _EVENT_END])
        self.trace = None
        self.event = None
        self.reading_trace = False
        self.tree = {}

    def read_trace(self, skip_trace=False):
        """
        Gets the next trace from the iterator

        Parameters
        ------------
        skip_trace
            Skip trace (boolean)

        Returns
        ------------
        trace
            Trace
        """
        tree = self.tree
        while True:
            tree_event, elem = next(self.context)
            if tree_event == _EVENT_START:
                parent = tree[elem.getparent()] if elem.getparent() in tree else None

                if elem.tag.endswith(xes_constants.TAG_TRACE):
                    if not skip_trace:
                        self.trace = Trace()
                        tree[elem] = self.trace.attributes
                        self.reading_trace = True
                    else:
                        self.trace = None
                        self.reading_trace = False
                    continue

                if self.reading_trace:
                    if elem.tag.endswith(xes_constants.TAG_STRING):
                        if parent is not None:
                            tree = parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY),
                                                     elem.get(xes_constants.KEY_VALUE), tree)
                        continue

                    elif elem.tag.endswith(xes_constants.TAG_DATE):
                        try:
                            dt = self.date_parser.apply(elem.get(xes_constants.KEY_VALUE))
                            tree = parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), dt, tree)
                        except TypeError:
                            logging.info("failed to parse date: " + str(elem.get(xes_constants.KEY_VALUE)))
                        except ValueError:
                            logging.info("failed to parse date: " + str(elem.get(xes_constants.KEY_VALUE)))
                        continue

                    elif elem.tag.endswith(xes_constants.TAG_EVENT):
                        self.event = Event()
                        tree[elem] = self.event
                        continue

                    elif elem.tag.endswith(xes_constants.TAG_FLOAT):
                        if parent is not None:
                            try:
                                val = float(elem.get(xes_constants.KEY_VALUE))
                                tree = parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), val, tree)
                            except ValueError:
                                logging.info("failed to parse float: " + str(elem.get(xes_constants.KEY_VALUE)))
                        continue

                    elif elem.tag.endswith(xes_constants.TAG_INT):
                        if parent is not None:
                            try:
                                val = int(elem.get(xes_constants.KEY_VALUE))
                                tree = parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), val, tree)
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
                                tree = parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), val, tree)
                            except ValueError:
                                logging.info("failed to parse boolean: " + str(elem.get(xes_constants.KEY_VALUE)))
                        continue

                    elif elem.tag.endswith(xes_constants.TAG_LIST):
                        if parent is not None:
                            # lists have no value, hence we put None as a value
                            tree = parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY), None, tree)
                        continue

                    elif elem.tag.endswith(xes_constants.TAG_ID):
                        if parent is not None:
                            tree = parse_attribute(elem, parent, elem.get(xes_constants.KEY_KEY),
                                                     elem.get(xes_constants.KEY_VALUE), tree)
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
                    if self.trace is not None:
                        self.trace.append(self.event)
                        self.event = None
                    continue

                elif elem.tag.endswith(xes_constants.TAG_TRACE):
                    self.reading_trace = False
                    return self.trace

        # automatic reset after reading all the traces
        self.reset()
        raise StopIteration


def apply(filename, parameters=None):
    """
    Gets the event log iterable

    Parameters
    -------------
    filename
        File name
    parameters
        Parameters

    Returns
    -------------
    iterable
        Event log iterable
    """
    obj = IterableXesReader(filename, parameters=parameters)
    return obj


def sample(filename, parameters=None):
    """
    Samples the event log, getting if possible the maximum
    number of traces as specified in the parameters, and skipping
    reading a trace by the specified probability

    Parameters
    -------------
    filename
        File name
    parameters
        Parameters of the sampling, including:
        - Parameters.MAX_TRACES => Maximum number of traces
        - Parameters.SKIP_PROBABILITY => Probability to skip reading a trace from a XES log (the log is iterated
        from the start to the end)

    Returns
    ------------
    log_obj
        Log object
    """
    if parameters is None:
        parameters = {}

    obj = IterableXesReader(filename, parameters=parameters)

    max_traces = exec_utils.get_param_value(Parameters.MAX_TRACES, parameters, 1000)
    skip_probability = exec_utils.get_param_value(Parameters.SKIP_PROBABILITY, parameters, 0.5)

    log = EventLog()
    while True:
        try:
            r = random.random()
            if r <= skip_probability:
                skip_trace = True
            else:
                skip_trace = False
            trace = obj.read_trace(skip_trace=skip_trace)
            if trace is not None:
                log.append(trace)
                if len(log) > max_traces:
                    break
        except StopIteration:
            break
    return log


def parse_attribute(elem, store, key, value, tree):
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
