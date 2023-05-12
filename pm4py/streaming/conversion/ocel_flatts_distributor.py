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
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.ocel import constants as ocel_constants
from copy import copy
from pm4py.streaming.stream.live_event_stream import LiveEventStream


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    OCEL_ACTIVITY_KEY = ocel_constants.PARAM_EVENT_ACTIVITY
    OCEL_TIMESTAMP_KEY = ocel_constants.PARAM_EVENT_TIMESTAMP
    OCEL_TYPE_PREFIX = ocel_constants.PARAM_OBJECT_TYPE_PREFIX_EXTENDED


class OcelFlattsDistributor(object):
    def __init__(self, parameters: Optional[Dict[Any, Any]] = None):
        """
        Instantiate the object, "distributing" an OCEL event among all
        the event streams for the "flattened" events.

        Parameters
        -----------------
        parameters
            Parameters of the algorithm, including:
            - Parameters.ACTIVITY_KEY => the activity key to use in the flattening
            - Parameters.TIMESTAMP_KEY => the timestamp key to use in the flattening
            - Parameters.OCEL_ACTIVITY_KEY => the attribute in the OCEL event that is the activity (default: ocel:activity)
            - Parameters.OCEL_TIMESTAMP_KEY => the attribute in the OCEL event that is the timestamp (default: ocel:timestamp)
            - Parameters.OCEL_TYPE_PREFIX => the prefix of the object types in the OCEL (default: ocel:type)
        """
        if parameters is None:
            parameters = {}

        self.activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                                       xes_constants.DEFAULT_NAME_KEY)
        self.case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        self.timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                                        xes_constants.DEFAULT_TIMESTAMP_KEY)
        self.ocel_activity = exec_utils.get_param_value(Parameters.OCEL_ACTIVITY_KEY, parameters,
                                                        ocel_constants.DEFAULT_EVENT_ACTIVITY)
        self.ocel_timestamp = exec_utils.get_param_value(Parameters.OCEL_TIMESTAMP_KEY, parameters,
                                                         ocel_constants.DEFAULT_EVENT_TIMESTAMP)

        self.ot_prefix = exec_utils.get_param_value(Parameters.OCEL_TYPE_PREFIX, parameters,
                                                    ocel_constants.DEFAULT_OBJECT_TYPE_PREFIX_EXTENDED)
        self.flattened_stream_listeners = {}

    def register(self, object_type: str, live_event_stream: LiveEventStream):
        """
        Register a new event stream (listener) for a given object type.

        Parameters
        -----------------
        object_type
            Given object type
        live_event_stream
            Live event stream
        """
        if object_type not in self.flattened_stream_listeners:
            self.flattened_stream_listeners[object_type] = []
        self.flattened_stream_listeners[object_type].append(live_event_stream)

    def append(self, event: Dict[str, Any]):
        """
        Flattens an OCEL among all the available object types, and send its flattening to each
        corresponding event stream.

        Parameters
        -------------
        event
            OCEL event (obtained for example using the ocel_iterator)
        """
        base_event = {x: y for x, y in event.items() if not x.startswith(self.ot_prefix)}
        base_event[self.activity_key] = base_event[self.ocel_activity]
        base_event[self.timestamp_key] = base_event[self.ocel_timestamp]
        del base_event[self.ocel_activity]
        del base_event[self.ocel_timestamp]

        ev_objects = {x.split(self.ot_prefix)[1]: y for x, y in event.items() if x.startswith(self.ot_prefix)}

        for ot in ev_objects:
            if ot in self.flattened_stream_listeners:
                for obj in ev_objects[ot]:
                    fl_ev = copy(base_event)
                    fl_ev[self.case_id_key] = obj
                    for listener in self.flattened_stream_listeners[ot]:
                        listener.append(fl_ev)
