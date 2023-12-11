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
from pm4py.util import constants, exec_utils, xes_constants, pandas_utils
from pm4py.streaming.util.dictio import generator
from pm4py.streaming.algo.interface import StreamingAlgorithm
import logging
from copy import copy


class Parameters:
    DICT_VARIANT = "dict_variant"
    DICT_ID = "dict_id"
    CASE_DICT_ID = "case_dict_id"
    DEV_DICT_ID = "dev_dict_id"
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY


START_ACTIVITIES = "start_activities"
END_ACTIVITIES = "end_activities"
ACTIVITIES = "activities"
SEQUENCE = "sequence"
PARALLEL = "parallel"


class FootprintsStreamingConformance(StreamingAlgorithm):
    def __init__(self, footprints, parameters=None):
        """
        Initialize the footprints streaming conformance object

        Parameters
        ---------------
        footprints
            Footprints
        parameters
            Parameters of the algorithm
        """
        self.footprints = footprints
        self.case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        self.activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                                       xes_constants.DEFAULT_NAME_KEY)
        self.start_activities = footprints[START_ACTIVITIES]
        self.end_activities = footprints[END_ACTIVITIES]
        self.activities = footprints[ACTIVITIES]
        self.all_fps = set(footprints[SEQUENCE]).union(set(footprints[PARALLEL]))
        self.build_dictionaries(parameters=parameters)
        StreamingAlgorithm.__init__(self)

    def build_dictionaries(self, parameters):
        """
        Builds the dictionaries needed to store the information during the replay

        Parameters
        ---------------
        parameters
            Parameters:
             - Parameters.DICT_VARIANT: type of dictionary to use
             - Parameters.CASE_DICT_ID: identifier of the dictionary hosting the last activity of a case (1)
             - Parameters.DEV_DICT_ID: identifier of the dictionary hosting the deviations (2)
        """
        dict_variant = exec_utils.get_param_value(Parameters.DICT_VARIANT, parameters, generator.Variants.THREAD_SAFE)
        case_dict_id = exec_utils.get_param_value(Parameters.CASE_DICT_ID, parameters, 0)
        dev_dict_id = exec_utils.get_param_value(Parameters.DEV_DICT_ID, parameters, 1)
        parameters_case_dict = copy(parameters)
        parameters_case_dict[Parameters.DICT_ID] = case_dict_id
        parameters_dev_dict = copy(parameters)
        parameters_dev_dict[Parameters.DICT_ID] = dev_dict_id
        self.case_dict = generator.apply(variant=dict_variant, parameters=parameters_case_dict)
        self.dev_dict = generator.apply(variant=dict_variant, parameters=parameters_dev_dict)

    def encode_str(self, stru):
        """
        Encodes a string for storage in generic dictionaries
        """
        return str(stru)

    def _process(self, event):
        """
        Check an event and updates the case dictionary

        Parameters
        ----------------
        event
            Event (dictionary)
        """
        case = event[self.case_id_key] if self.case_id_key in event else None
        activity = event[self.activity_key] if self.activity_key in event else None
        if case is not None and activity is not None:
            self.verify_footprints(self.encode_str(case), self.encode_str(activity))
        else:
            self.message_case_or_activity_not_in_event(event)

    def verify_footprints(self, case, activity):
        """
        Verify the event according to the footprints
        (assuming it has a case and an activity)

        Parameters
        ----------------
        case
            Case ID
        activity
            Activity
        """
        if case not in self.case_dict.keys():
            self.dev_dict[case] = 0
        if activity in self.activities:
            if case not in self.case_dict.keys():
                self.verify_start_case(case, activity)
            else:
                self.verify_intra_case(case, activity)
            self.case_dict[case] = activity
        else:
            self.dev_dict[case] = int(self.dev_dict[case]) + 1
            self.message_activity_not_possible(activity, case)

    def verify_intra_case(self, case, activity):
        """
        Verify the footprints of the current event

        Parameters
        ----------------
        case
            Case
        activity
            Activity
        """
        prev = self.case_dict[case]
        df = (prev, activity)
        if df not in self.all_fps:
            self.dev_dict[case] = int(self.dev_dict[case]) + 1
            self.message_footprints_not_possible(df, case)

    def verify_start_case(self, case, activity):
        """
        Verify the start activity of a case

        Parameters
        ---------------
        case
            Case
        activity
            Activity
        """
        if activity not in self.start_activities:
            self.dev_dict[case] = int(self.dev_dict[case]) + 1
            self.message_start_activity_not_possible(activity, case)

    def get_status(self, case):
        """
        Gets the current status of a case

        Parameters
        -----------------
        case
            Case

        Returns
        -----------------
        boolean
            Boolean value (True if there are no deviations)
        """
        if case in self.case_dict.keys():
            num_dev = int(self.dev_dict[case])
            if num_dev == 0:
                return True
            else:
                return False
        else:
            self.message_case_not_in_dictionary(case)

    def terminate(self, case):
        """
        Terminate a case (checking its end activity)

        Parameters
        -----------------
        case
            Case

        Returns
        -----------------
        boolean
            Boolean value (True if there are no deviations)
        """
        if case in self.case_dict.keys():
            curr = self.case_dict[case]
            if curr not in self.end_activities:
                self.message_end_activity_not_possible(curr, case)
                self.dev_dict[case] = int(self.dev_dict[case]) + 1
            num_dev = int(self.dev_dict[case])
            del self.case_dict[case]
            del self.dev_dict[case]
            if num_dev == 0:
                return True
            else:
                return False
        else:
            self.message_case_not_in_dictionary(case)

    def terminate_all(self):
        """
        Terminate all cases
        """
        cases = list(self.case_dict.keys())
        for case in cases:
            self.terminate(case)

    def message_case_or_activity_not_in_event(self, event):
        """
        Sends a message if the case or the activity are not
        there in the event
        """
        logging.error("case or activities are none! " + str(event))

    def message_activity_not_possible(self, activity, case):
        """
        Sends a message if the activity is not contained in the footprints

        Parameters
        --------------
        activity
            Activity
        case
            Case
        """
        logging.error(
            "the activity " + str(activity) + " is not possible according to the footprints! case: " + str(case))

    def message_footprints_not_possible(self, df, case):
        """
        Sends a message if the directly-follows between two activities is
        not possible

        Parameters
        ---------------
        df
            Directly-follows relations
        case
            Case
        """
        logging.error("the footprints " + str(df) + " are not possible! case: " + str(case))

    def message_start_activity_not_possible(self, activity, case):
        """
        Sends a message if the activity is not a possible start activity

        Parameters
        ---------------
        activity
            Activity
        case
            Case
        """
        logging.error("the activity " + str(activity) + " is not a possible start activity! case: " + str(case))

    def message_end_activity_not_possible(self, activity, case):
        """
        Sends a message if the activity is not a possible end activity

        Parameters
        ----------------
        activity
            Activity
        case
            Case
        """
        logging.error("the activity " + str(activity) + " is not a possible end activity! case: " + str(case))

    def message_case_not_in_dictionary(self, case):
        """
        Sends a message if the case is not in the current dictionary

        Parameters
        ----------------
        case
            Case
        """
        logging.error("the case " + str(case) + " is not in the dictionary! case: " + str(case))

    def _current_result(self):
        """
        Gets a diagnostics dataframe with the status of the cases

        Returns
        -------
        diagn_df
            Diagnostics dataframe
        """
        import pandas as pd

        cases = list(self.case_dict.keys())

        diagn_stream = []

        for case in cases:
            status = self.get_status(case)
            diagn_stream.append({"case": case, "is_fit": status})

        return pandas_utils.instantiate_dataframe(diagn_stream)


def apply(footprints, parameters=None):
    """
    Gets a footprints conformance checking object

    Parameters
    --------------
    footprints
        Footprints object
    parameters
        Parameters of the algorithm

    Returns
    --------------
    fp_check_obj
        Footprints conformance checking object
    """
    if parameters is None:
        parameters = {}

    return FootprintsStreamingConformance(footprints, parameters=parameters)
