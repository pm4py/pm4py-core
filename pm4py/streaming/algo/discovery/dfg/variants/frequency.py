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
from collections import Counter
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.streaming.util.dictio import generator
from pm4py.streaming.algo.interface import StreamingAlgorithm
from enum import Enum
from copy import copy
import logging


class Parameters(Enum):
    DICT_VARIANT = "dict_variant"
    DICT_ID = "dict_id"
    CASE_DICT_ID = "case_dict_id"
    DFG_DICT_ID = "dfg_dict_id"
    ACT_DICT_ID = "act_dict_id"
    START_ACT_DICT_ID = "start_act_dict_id"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


class StreamingDfgDiscovery(StreamingAlgorithm):
    def __init__(self, parameters=None):
        """
        Initialize the StreamingDFGDiscovery object

        Parameters
        ---------------
        parameters of the algorithm, including:
         - Parameters.ACTIVITY_KEY: the key of the event to use as activity
         - Parameters.CASE_ID_KEY: the key of the event to use as case identifier
        """
        if parameters is None:
            parameters = {}

        self.parameters = parameters
        self.activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                                       xes_constants.DEFAULT_NAME_KEY)
        self.case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters,
                                                      constants.CASE_CONCEPT_NAME)
        self.build_dictionaries(parameters)
        StreamingAlgorithm.__init__(self)

    def build_dictionaries(self, parameters):
        """
        Builds the dictionaries that are needed by the
        discovery operation

        Parameters
        ---------------
        parameters
            Parameters:
             - Parameters.DICT_VARIANT: type of dictionary to use
             - Parameters.CASE_DICT_ID: identifier of the case dictionary (hosting the last activity of a case) (0)
             - Parameters.DFG_DICT_ID: identifier of the DFG dictionary (1)
             - Parameters.ACT_ID: identifier of the dictionary hosting the count of the activities (2)
             - Parameters.START_ACT_DICT_ID: identifier of the dictionary hosting the count of the start activities (3)
        """
        dict_variant = exec_utils.get_param_value(Parameters.DICT_VARIANT, parameters, generator.Variants.THREAD_SAFE)
        case_dict_id = exec_utils.get_param_value(Parameters.CASE_DICT_ID, parameters, 0)
        dfg_dict_id = exec_utils.get_param_value(Parameters.DFG_DICT_ID, parameters, 1)
        act_dict_id = exec_utils.get_param_value(Parameters.ACT_DICT_ID, parameters, 2)
        start_act_dict_id = exec_utils.get_param_value(Parameters.START_ACT_DICT_ID, parameters, 3)
        parameters_case_dict = copy(parameters)
        parameters_case_dict[Parameters.DICT_ID] = case_dict_id
        parameters_dfg = copy(parameters)
        parameters_dfg[Parameters.DICT_ID] = dfg_dict_id
        parameters_activities = copy(parameters)
        parameters_activities[Parameters.DICT_ID] = act_dict_id
        parameters_start_activities = copy(parameters)
        parameters_start_activities[Parameters.DICT_ID] = start_act_dict_id
        self.case_dict = generator.apply(variant=dict_variant, parameters=parameters_case_dict)
        self.dfg = generator.apply(variant=dict_variant, parameters=parameters_dfg)
        self.activities = generator.apply(variant=dict_variant, parameters=parameters_activities)
        self.start_activities = generator.apply(variant=dict_variant, parameters=parameters_start_activities)

    def event_without_activity_or_case(self, event):
        """
        Print an error message when an event is without the
        activity or the case identifier

        Parameters
        ----------------
        event
            Event
        """
        logging.warning("event without activity or case: " + str(event))

    def encode_str(self, stru):
        """
        Encodes a string for storage in generic dictionaries
        """
        return str(stru)

    def encode_tuple(self, tup):
        """
        Encodes a tuple for storage in generic dictionaries
        """
        return str(tup)

    def _process(self, event):
        """
        Receives an event from the live event stream,
        and appends it to the current DFG discovery

        Parameters
        ---------------
        event
            Event
        """
        if self.case_id_key in event and self.activity_key in event:
            case = self.encode_str(event[self.case_id_key])
            activity = self.encode_str(event[self.activity_key])
            if case not in self.case_dict:
                if activity not in self.start_activities:
                    self.start_activities[activity] = 1
                else:
                    self.start_activities[activity] = int(self.start_activities[activity]) + 1
            else:
                df = self.encode_tuple((self.case_dict[case], activity))
                if df not in self.dfg:
                    self.dfg[df] = 1
                else:
                    self.dfg[df] = int(self.dfg[df]) + 1
            if activity not in self.activities:
                self.activities[activity] = 1
            else:
                self.activities[activity] = int(self.activities[activity]) + 1
            self.case_dict[case] = activity
        else:
            self.event_without_activity_or_case(event)

    def _current_result(self):
        """
        Gets the current state of the DFG

        Returns
        ----------------
        dfg
            Directly-Follows Graph
        activities
            Activities
        start_activities
            Start activities
        end_activities
            End activities
        """
        dfg = {eval(x): int(self.dfg[x]) for x in self.dfg}
        activities = {x: int(self.activities[x]) for x in self.activities}
        start_activities = {x: int(self.start_activities[x]) for x in self.start_activities}
        end_activities = dict(Counter(self.case_dict[x] for x in self.case_dict))
        return dfg, activities, start_activities, end_activities


def apply(parameters=None):
    """
    Creates a StreamingDFGDiscovery object

    Parameters
    --------------
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    return StreamingDfgDiscovery(parameters=parameters)
