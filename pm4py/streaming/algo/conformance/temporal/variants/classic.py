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
import sys
from copy import copy
from enum import Enum
from typing import Optional, Dict, Any, Tuple

from pm4py.objects.log.obj import Event
from pm4py.streaming.algo.interface import StreamingAlgorithm
from pm4py.streaming.util.dictio import generator
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.util import typing
import json


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ZETA = "zeta"
    DICT_VARIANT = "dict_variant"
    DICT_ID = "dict_id"
    CASE_DICT_ID = "case_dict_id"
    DEV_DICT_ID = "dev_dict_id"


class TemporalProfileStreamingConformance(StreamingAlgorithm):
    def __init__(self, temporal_profile: typing.TemporalProfile, parameters: Optional[Dict[Any, Any]] = None):
        """
        Initialize the streaming conformance checking.

        Implements the approach described in:
        Stertz, Florian, Jürgen Mangler, and Stefanie Rinderle-Ma. "Temporal Conformance Checking at Runtime based on Time-infused Process Models." arXiv preprint arXiv:2008.07262 (2020).

        Parameters
        ---------------
        temporal_profile
            Temporal profile
        parameters
            Parameters of the algorithm, including:
             - Parameters.ACTIVITY_KEY => the attribute to use as activity
             - Parameters.START_TIMESTAMP_KEY => the attribute to use as start timestamp
             - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
             - Parameters.ZETA => multiplier for the standard deviation
             - Parameters.CASE_ID_KEY => column to use as case identifier
             - Parameters.DICT_VARIANT => the variant of dictionary to use
             - Parameters.CASE_DICT_ID => the identifier of the case dictionary
             - Parameters.DEV_DICT_ID => the identifier of the deviations dictionary
        """
        if parameters is None:
            parameters = {}

        self.temporal_profile = temporal_profile
        self.activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                                       xes_constants.DEFAULT_NAME_KEY)
        self.timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters,
                                                        xes_constants.DEFAULT_TIMESTAMP_KEY)
        self.start_timestamp_key = exec_utils.get_param_value(Parameters.START_TIMESTAMP_KEY, parameters,
                                                              xes_constants.DEFAULT_TIMESTAMP_KEY)
        self.case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        self.zeta = exec_utils.get_param_value(Parameters.ZETA, parameters, 6.0)
        parameters_gen = copy(parameters)
        dict_variant = exec_utils.get_param_value(Parameters.DICT_VARIANT, parameters, generator.Variants.THREAD_SAFE)
        case_dict_id = exec_utils.get_param_value(Parameters.CASE_DICT_ID, parameters, 0)
        parameters_gen[Parameters.DICT_ID] = case_dict_id
        self.case_dictionary = generator.apply(variant=dict_variant, parameters=parameters_gen)
        parameters_dev = copy(parameters)
        dev_dict_id = exec_utils.get_param_value(Parameters.DEV_DICT_ID, parameters, 1)
        parameters_dev[Parameters.DICT_ID] = dev_dict_id
        self.deviations_dict = generator.apply(variant=dict_variant, parameters=parameters_dev)
        StreamingAlgorithm.__init__(self)

    def _process(self, event: Event):
        """
        Checks the incoming event, and stores it in the cases dictionary

        Parameters
        ---------------
        event
            Event
        """
        if self.case_id_key not in event or self.start_timestamp_key not in event or self.timestamp_key not in event or self.activity_key not in event:
            self.message_event_is_not_complete(event)
        else:
            case = str(event[self.case_id_key])
            start_timestamp = event[self.start_timestamp_key].timestamp()
            end_timestamp = event[self.timestamp_key].timestamp()
            activity = str(event[self.activity_key])
            if case not in self.case_dictionary.keys():
                self.case_dictionary[case] = json.dumps([])
                self.deviations_dict[case] = json.dumps([])
            ev_red = (case, start_timestamp, end_timestamp, activity)
            self.check_conformance(ev_red)
            this_case = json.loads(self.case_dictionary[case])
            this_case.append(ev_red)
            self.case_dictionary[case] = json.dumps(this_case)

    def check_conformance(self, event: Tuple[str, float, float, str]):
        """
        Checks the conformance according to the temporal profile

        Parameters
        ---------------
        event
            Event
        """
        case, start_timestamp, end_timestamp, activity = event
        prev_events = json.loads(self.case_dictionary[case])
        for i in range(len(prev_events)):
            prev_case, prev_start_timestamp, prev_end_timestamp, prev_activity = prev_events[i]
            if start_timestamp >= prev_end_timestamp:
                if (prev_activity, activity) in self.temporal_profile:
                    diff = start_timestamp - prev_end_timestamp
                    mean = self.temporal_profile[(prev_activity, activity)][0]
                    std = self.temporal_profile[(prev_activity, activity)][1]
                    if diff < mean - self.zeta * std or diff > mean + self.zeta * std:
                        this_zeta = abs(diff - mean) / std if std > 0 else sys.maxsize
                        dev_descr = (case, prev_activity, activity, diff, this_zeta)
                        this_dev = json.loads(self.deviations_dict[case])
                        this_dev.append(dev_descr)
                        self.deviations_dict[case] = json.dumps(this_dev)
                        self.message_deviation(dev_descr)

    def message_event_is_not_complete(self, event: Event):
        """
        Method that is called when the event does not contain the case, or the activity, or the timestamp

        Parameters
        --------------
        event
            Incoming event
        """
        logging.error("case or activities or timestamp are none! " + str(event))

    def message_deviation(self, dev_descr: Tuple[str, str, str, float, float]):
        """
        Method that is called to signal a deviation according to the temporal profile

        Parameters
        --------------
        dev_descr
            Description of the deviation to be printed
        """
        logging.error("the temporal profile is broken in the following setting: " + str(dev_descr))

    def _current_result(self) -> typing.TemporalProfileStreamingConfResults:
        """
        Gets the current deviations identified by conformance checking

        Returns
        -------------
        deviations_dict
            Deviations dictionary
        """
        dev_dict = {}
        for x in self.deviations_dict.keys():
            y = json.loads(self.deviations_dict[x])
            if y:
                dev_dict[x] = y
        return dev_dict


def apply(temporal_profile: typing.TemporalProfile, parameters: Optional[Dict[Any, Any]] = None):
    """
    Initialize the streaming conformance checking.

    Implements the approach described in:
    Stertz, Florian, Jürgen Mangler, and Stefanie Rinderle-Ma. "Temporal Conformance Checking at Runtime based on Time-infused Process Models." arXiv preprint arXiv:2008.07262 (2020).

    Parameters
    ---------------
    temporal_profile
        Temporal profile
    parameters
        Parameters of the algorithm, including:
         - Parameters.ACTIVITY_KEY => the attribute to use as activity
         - Parameters.START_TIMESTAMP_KEY => the attribute to use as start timestamp
         - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp
         - Parameters.ZETA => multiplier for the standard deviation
         - Parameters.CASE_ID_KEY => column to use as case identifier
         - Parameters.DICT_VARIANT => the variant of dictionary to use
         - Parameters.CASE_DICT_ID => the identifier of the case dictionary
         - Parameters.DEV_DICT_ID => the identifier of the deviations dictionary
    """
    if parameters is None:
        parameters = {}

    return TemporalProfileStreamingConformance(temporal_profile, parameters=parameters)
