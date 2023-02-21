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
from enum import Enum

from pm4py.objects.log.obj import Trace, Event
from pm4py.util import xes_constants, exec_utils
from pm4py.util.dt_parsing import parser as dt_parser


class Parameters(Enum):
    ACCEPTANCE_CONDITION = "acceptance_condition"


_EVENT_END = 'end'
_EVENT_START = 'start'


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


class StreamingTraceXesReader:
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
        self.acceptance_condition = exec_utils.get_param_value(Parameters.ACCEPTANCE_CONDITION, parameters,
                                                               lambda x: True)
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
        trace = self.read_trace()
        if self.reading_log:
            return trace
        raise StopIteration

    def to_trace_stream(self, trace_stream):
        """
        Sends the content of a XES log to a trace stream

        Parameters
        --------------
        trace_stream
            Trace stream
        """
        while self.reading_log:
            trace = self.read_trace()
            if trace is not None:
                trace_stream.append(trace)

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
        self.reading_log = True
        self.reading_trace = False
        self.tree = {}

    def read_trace(self):
        """
        Gets the next trace from the iterator

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
                    self.trace = Trace()
                    tree[elem] = self.trace.attributes
                    self.reading_trace = True
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
                    if self.acceptance_condition(self.trace):
                        return self.trace
                    continue

                elif elem.tag.endswith(xes_constants.TAG_LOG):
                    self.reading_log = False
                    break


def apply(path, parameters=None):
    """
    Creates a StreamingTraceXesReader object

    Parameters
    ---------------
    path
        Path
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    stream_read_obj
        Stream reader object
    """
    return StreamingTraceXesReader(path, parameters=parameters)
