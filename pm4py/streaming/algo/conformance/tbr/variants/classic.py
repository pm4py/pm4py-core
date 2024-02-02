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
from pm4py.util import constants, exec_utils, xes_constants
from pm4py.streaming.util.dictio import generator
import logging
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.streaming.algo.interface import StreamingAlgorithm
from pm4py.objects.petri_net import semantics
from pm4py.util import pandas_utils, nx_utils
from copy import copy
import sys


class Parameters:
    DICT_VARIANT = "dict_variant"
    DICT_ID = "dict_id"
    CASE_DICT_ID = "case_dict_id"
    MISSING_DICT_ID = "missing_dict_id"
    REMAINING_DICT_ID = "remaining_dict_id"
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    MAXIMUM_ITERATIONS_INVISIBLES = "maximum_iterations_invisibles"


class TbrStreamingConformance(StreamingAlgorithm):
    def __init__(self, net, im, fm, parameters=None):
        """
        Initialize the token-based replay streaming conformance

        Parameters
        --------------
        net
            Petri net
        im
            Initial marking
        fm
            Final marking
        """
        if parameters is None:
            parameters = {}
        self.case_id_key = exec_utils.get_param_value(Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME)
        self.activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters,
                                                       xes_constants.DEFAULT_NAME_KEY)
        self.maximum_iterations_invisibles = exec_utils.get_param_value(Parameters.MAXIMUM_ITERATIONS_INVISIBLES,
                                                                        parameters, 10)
        self.net = net
        self.im = im
        self.fm = fm
        self.places_inv_dict = {x.name: x for x in net.places}
        self.activities = list(set(x.label for x in self.net.transitions))
        self.dictio_spaths = self.get_paths_net()
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
             - Parameters.CASE_DICT_ID: identifier of the dictionary hosting the markings (0)
             - Parameters.MISSING_DICT_ID: identifier of the dictionary hosting the missing tokens (1)
             - Parameters.REMAINING_DICT_ID: identifier of the dictionary hosting the remaining tokens (2)
        """
        dict_variant = exec_utils.get_param_value(Parameters.DICT_VARIANT, parameters, generator.Variants.THREAD_SAFE)
        case_dict_id = exec_utils.get_param_value(Parameters.CASE_DICT_ID, parameters, 0)
        missing_dict_id = exec_utils.get_param_value(Parameters.MISSING_DICT_ID, parameters, 1)
        remaining_dict_id = exec_utils.get_param_value(Parameters.REMAINING_DICT_ID, parameters, 2)
        parameters_case_dict = copy(parameters)
        parameters_case_dict[Parameters.DICT_ID] = case_dict_id
        parameters_missing = copy(parameters)
        parameters_case_dict[Parameters.DICT_ID] = missing_dict_id
        parameters_remaining = copy(parameters)
        parameters_remaining[Parameters.DICT_ID] = remaining_dict_id
        self.case_dict = generator.apply(variant=dict_variant, parameters=parameters_case_dict)
        self.missing = generator.apply(variant=dict_variant, parameters=parameters_missing)
        self.remaining = generator.apply(variant=dict_variant, parameters=parameters_remaining)

    def get_paths_net(self):
        """
        Gets the dictionary of shortest paths using invisibles transitions

        Returns
        ---------------
        dictio_spaths
            Dictionary of shortest paths
        """
        G = nx_utils.DiGraph()
        for pl in self.net.places:
            G.add_node(pl)
        for tr in self.net.transitions:
            G.add_node(tr)
            if tr.label is None:
                for a in tr.out_arcs:
                    target_place = a.target
                    G.add_edge(tr, target_place)
            for a in tr.in_arcs:
                source_place = a.source
                G.add_edge(source_place, tr)
        shortest_path = nx_utils.all_pairs_shortest_path(G)
        dictio_spaths = {}
        for el in shortest_path:
            if type(el[0]) is PetriNet.Place:
                for sel in el[1]:
                    spath = [x for x in el[1][sel][1:-2] if type(x) is PetriNet.Transition]
                    if spath:
                        if not el[0] in dictio_spaths:
                            dictio_spaths[el[0]] = {}
                        dictio_spaths[el[0]][sel] = spath
        return dictio_spaths

    def _process(self, event):
        """
        Checks the event according to the TBR

        Parameters
        ---------------
        event
            Event (dictionary)

        Returns
        ---------------
        boolean
            Boolean value
        """
        case = event[self.case_id_key] if self.case_id_key in event else None
        activity = event[self.activity_key] if self.activity_key in event else None
        if case is not None and activity is not None:
            self.verify_tbr(self.encode_str(case), activity)
        else:
            self.message_case_or_activity_not_in_event(event)

    def encode_str(self, stru):
        """
        Encodes a string for storage in generic dictionaries
        """
        return str(stru)

    def encode_marking(self, mark):
        """
        Encodes a marking for storage in generic dictionaries
        """
        em = {}
        for pl in mark:
            em[pl.name] = mark[pl]
        return str(em)

    def decode_marking(self, ems):
        """
        Decodes a marking from a generic dictionary
        to a Marking object
        """
        em = eval(ems)
        mark = Marking()
        for p in em:
            mark[self.places_inv_dict[p]] = em[p]
        return mark

    def verify_tbr(self, case, activity):
        """
        Verifies an activity happening in a case

        Parameters
        --------------
        case
            Case
        activity
            Activity
        """
        if activity in self.activities:
            if case not in self.case_dict:
                self.case_dict[case] = self.encode_marking(copy(self.im))
                self.missing[case] = 0
                self.remaining[case] = 0
            marking = self.decode_marking(self.case_dict[case])
            new_marking = marking
            prev_marking = None
            correct_exec = False
            numb_it = 0
            while new_marking is not None and prev_marking != new_marking:
                numb_it = numb_it + 1
                if numb_it > self.maximum_iterations_invisibles:
                    break
                enabled_transitions = semantics.enabled_transitions(self.net, new_marking)
                matching_transitions = [x for x in enabled_transitions if x.label == activity]
                if matching_transitions:
                    new_marking = semantics.weak_execute(matching_transitions[0], new_marking)
                    self.case_dict[case] = self.encode_marking(new_marking)
                    correct_exec = True
                    break
                prev_marking = new_marking
                new_marking = self.enable_trans_with_invisibles(new_marking, activity)
                correct_exec = False
            if correct_exec is False:
                self.message_missing_tokens(activity, case)
                # enables one of the matching transitions
                matching_transitions = [x for x in self.net.transitions if x.label == activity]
                t = matching_transitions[0]
                for a in t.in_arcs:
                    pl = a.source
                    mark = a.weight
                    if pl not in marking or new_marking[pl] < mark:
                        self.missing[case] = int(self.missing[case]) + (mark - marking[pl])
                        marking[pl] = mark
                new_marking = semantics.weak_execute(t, marking)
                self.case_dict[case] = self.encode_marking(new_marking)
        else:
            self.message_activity_not_possible(activity, case)

    def enable_trans_with_invisibles(self, marking, activity):
        """
        Enables a visible transition (that is not enabled) through
        invisible transitions

        Parameters
        ----------------
        marking
            Marking
        activity
            Activity to enable

        Returns
        ---------------
        new_marking
            New marking (where the transition CAN be enabled)
        """
        corr_trans_to_act = [x for x in self.net.transitions if x.label == activity]
        spath = None
        spath_length = sys.maxsize
        for pl in marking:
            for tr in corr_trans_to_act:
                if pl in self.dictio_spaths:
                    if tr in self.dictio_spaths[pl]:
                        new_path = self.dictio_spaths[pl][tr]
                        if len(new_path) < spath_length:
                            spath = new_path
                            spath_length = len(spath)
        if spath is not None:
            # try to fire the transitions
            for tr in spath:
                if tr in semantics.enabled_transitions(self.net, marking):
                    marking = semantics.weak_execute(tr, marking)
                else:
                    return None
            return marking
        return None

    def get_status(self, case):
        """
        Gets the status of an open case

        Parameters
        ----------------
        case
            Case
        """
        if case in self.case_dict:
            return {"marking": self.decode_marking(self.case_dict[case]), "missing": int(self.missing[case])}
        else:
            self.message_case_not_in_dictionary(case)

    def terminate(self, case):
        """
        Terminate a case, checking if the final marking is reached

        Parameters
        ----------------
        case
            Case ID

        Returns
        ---------------
        dictio
            Dictionary containing: the marking, the count of missing and remaining tokens
        """
        case = self.encode_str(case)
        if case in self.case_dict:
            remaining = 0
            if not self.decode_marking(self.case_dict[case]) == self.fm:
                new_marking = self.reach_fm_with_invisibles(self.case_dict[case])
                if new_marking is None:
                    new_marking = self.decode_marking(self.case_dict[case])
                if not new_marking == self.fm:
                    self.message_final_marking_not_reached(case, new_marking)
                    fm_copy = copy(self.fm)
                    for m in fm_copy:
                        if not m in new_marking:
                            new_marking[m] = 0
                        self.missing[case] = int(self.missing[case]) + (fm_copy[m] - new_marking[m])
                    for m in new_marking:
                        if not m in fm_copy:
                            fm_copy[m] = 0
                        remaining += new_marking[m] - fm_copy[m]
            missing = int(self.missing[case])
            is_fit = missing == 0 and remaining == 0
            ret = {"marking": self.decode_marking(self.case_dict[case]), "missing": missing, "remaining": remaining, "is_fit": is_fit}
            del self.case_dict[case]
            del self.missing[case]
            del self.remaining[case]
            return ret
        else:
            self.message_case_not_in_dictionary(case)

    def terminate_all(self):
        """
        Terminate all open cases
        """
        cases = list(self.case_dict.keys())
        for case in cases:
            self.terminate(case)

    def reach_fm_with_invisibles(self, marking):
        """
        Reaches the final marking using invisible transitions

        Parameters
        --------------
        marking
            Marking

        Returns
        --------------
        new_marking
            New marking (hopely equal to the final marking)
        """
        spath = None
        spath_length = sys.maxsize
        for pl in marking:
            if pl in self.dictio_spaths:
                for pl2 in self.fm:
                    if pl2 in self.dictio_spaths[pl]:
                        new_path = self.dictio_spaths[pl][pl2]
                        if len(new_path) < spath_length:
                            spath = new_path
                            spath_length = len(spath)
        if spath is not None:
            # try to fire the transitions
            for tr in spath:
                if tr in semantics.enabled_transitions(self.net, marking):
                    marking = semantics.weak_execute(tr, marking)
                else:
                    return None
            return marking
        return None

    def message_case_or_activity_not_in_event(self, event):
        """
        Sends a message if the case or the activity are not
        there in the event
        """
        logging.error("case or activities are none! " + str(event))

    def message_activity_not_possible(self, activity, case):
        """
        Sends a message if the activity is not possible
        according to the model

        Parameters
        ---------------
        activity
            Activity
        case
            Case
        """
        logging.error("the activity " + str(activity) + " is not possible according to the model! case: " + str(case))

    def message_missing_tokens(self, activity, case):
        """
        Sends a message if the insertion of missing
        tokens occur

        Parameters
        ---------------
        activity
            Activity
        case
            Case
        """
        logging.error(
            "the activity " + str(activity) + " could not be executed without inserting missing tokens! case: " + str(
                case))

    def message_case_not_in_dictionary(self, case):
        """
        Sends a message if the provided case is not in the dictionary

        Parameters
        ---------------
        activity
            Activity
        case
            Case
        """
        logging.error("the case " + str(case) + " is not in the dictionary! case: " + str(case))

    def message_final_marking_not_reached(self, case, marking):
        """
        Sends a message if the final marking could not be reached
        for the current case

        Parameters
        ---------------
        case
            Case
        """
        logging.error("the final marking is not reached! case: " + str(case) + " marking: " + str(
            marking) + " final marking: " + str(self.fm))
        pass

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
            missing = status["missing"]
            is_fit = missing == 0
            diagn_stream.append({"case": case, "is_fit": is_fit, "missing": missing})

        return pandas_utils.instantiate_dataframe(diagn_stream)


def apply(net, im, fm, parameters=None):
    """
    Method that creates the TbrStreamingConformance object

    Parameters
    ----------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    conf_stream_obj
        Conformance streaming object
    """
    return TbrStreamingConformance(net, im, fm, parameters=parameters)
