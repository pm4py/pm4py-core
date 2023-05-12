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
from typing import Optional, Dict, Any

import numpy as np
import pandas as pd

from pm4py.objects.log.obj import Trace, Event
from pm4py.streaming.stream.live_trace_stream import LiveTraceStream
from pm4py.util import constants, xes_constants, exec_utils, pandas_utils


class Parameters(Enum):
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    INDEX_KEY = "index_key"


class PandasDataframeAsIterable(object):
    def __init__(self, dataframe: pd.DataFrame, parameters: Optional[Dict[Any, Any]] = None):
        if parameters is None:
            parameters = {}

        case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
        timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                                   xes_constants.DEFAULT_TIMESTAMP_KEY)
        index_key = exec_utils.get_param_value(Parameters.INDEX_KEY, parameters, constants.DEFAULT_INDEX_KEY)

        if not (hasattr(dataframe, "attrs") and dataframe.attrs):
            # dataframe has not been initialized through format_dataframe
            dataframe = pandas_utils.insert_index(dataframe, index_key)
            dataframe.sort_values([case_id_key, timestamp_key, index_key])

        cases = dataframe[case_id_key].to_numpy()

        self.activities = dataframe[activity_key].to_numpy()
        self.timestamps = dataframe[timestamp_key].to_numpy()
        self.c_unq, self.c_ind, self.c_counts = np.unique(cases, return_index=True, return_counts=True)
        self.no_traces = len(self.c_ind)
        self.i = 0

    def read_trace(self) -> Trace:
        if self.i < self.no_traces:
            case_id = self.c_unq[self.i]
            si = self.c_ind[self.i]
            ei = si + self.c_counts[self.i]
            trace = Trace(attributes={xes_constants.DEFAULT_TRACEID_KEY: case_id})
            for j in range(si, ei):
                event = Event({xes_constants.DEFAULT_NAME_KEY: self.activities[j],
                               xes_constants.DEFAULT_TIMESTAMP_KEY: self.timestamps[j]})
                trace.append(event)
            self.i = self.i + 1
            return trace

    def reset(self):
        self.i = 0

    def __iter__(self):
        """
        Starts the iteration
        """
        return self

    def __next__(self):
        """
        Gets the next trace
        """
        trace = self.read_trace()
        if trace is None:
            raise StopIteration
        return trace

    def to_trace_stream(self, trace_stream: LiveTraceStream):
        """
        Sends the content of the dataframe to a trace stream

        Parameters
        --------------
        trace_stream
            Trace stream
        """
        trace = self.read_trace()
        while trace is not None:
            trace_stream.append(trace)
            trace = self.read_trace()


def apply(dataframe, parameters=None) -> PandasDataframeAsIterable:
    """
    Transforms the Pandas dataframe object to an iterable

    Parameters
    ----------------
    dataframe
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.CASE_ID_KEY => the attribute to be used as case identifier (default: constants.CASE_CONCEPT_NAME)
        - Parameters.ACTIVITY_KEY => the attribute to be used as activity (default: xes_constants.DEFAULT_NAME_KEY)
        - Parameters.TIMESTAMP_KEY => the attribute to be used as timestamp (default: xes_constants.DEFAULT_TIMESTAMP_KEY)

    Returns
    ----------------
    log_iterable
        Iterable log object, which can be iterated directly or added to a live trace stream
                                (using the method to_trace_stream).
    """
    return PandasDataframeAsIterable(dataframe, parameters=parameters)
