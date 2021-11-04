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
import csv
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    TRANSFORMATION_FUNCTION = "transformation_function"
    ACCEPTANCE_CONDITION = "acceptance_condition"


class CSVEventStreamReader(object):
    def __init__(self, path, parameters=None):
        self.path = path
        self.parameters = parameters
        self.transformation_function = exec_utils.get_param_value(Parameters.TRANSFORMATION_FUNCTION, parameters,
                                                                  lambda x: x)
        self.acceptance_condition = exec_utils.get_param_value(Parameters.ACCEPTANCE_CONDITION, parameters,
                                                               lambda x: True)
        self.reset()

    def reset(self):
        self.F = open(self.path, "r")
        self.reader = csv.DictReader(self.F)
        self.reading_log = True

    def __iter__(self):
        """
        Starts the iteration
        """
        return self

    def __next__(self):
        """
        Gets the next element of the log
        """
        event = self.read_event()
        if self.reading_log:
            return event
        raise StopIteration

    def to_event_stream(self, event_stream):
        """
        Sends the content of a CSV log to an event stream

        Parameters
        --------------
        event_stream
            Event stream
        """
        while self.reading_log:
            event = self.read_event()
            if event is not None:
                event_stream.append(event)

    def read_event(self):
        """
        Reads an event from the CSV file

        Returns
        ------------
        eve
            Event
        """
        while True:
            try:
                event = next(self.reader)
                if event is not None:
                    event = dict(event)
                    event = self.transformation_function(event)
                    if self.acceptance_condition(event):
                        return event
                else:
                    self.reading_log = False
                    return None
            except StopIteration as exc:
                self.reading_log = False
                return None

def apply(path, parameters=None):
    """
    Creates the CSVEventStreamReaderObject

    Parameters
    -------------
    path
        Path to the CSV file
    parameters
        Parameters

    Returns
    -------------
    stream_read_obj
        Stream reader object
    """
    return CSVEventStreamReader(path, parameters=parameters)
