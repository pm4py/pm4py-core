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
import difflib
from enum import Enum
from typing import Optional, Dict, Any, List, Set, Union

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.log.util import log_regex
from pm4py.objects.petri_net.utils import align_utils
from pm4py.util import exec_utils
from pm4py.util import string_distance
from pm4py.util import typing
from pm4py.util import constants, xes_constants
import pandas as pd
from pm4py.objects.conversion.log import converter as log_converter


class Parameters(Enum):
    PERFORM_ANTI_ALIGNMENT = "perform_anti_alignment"
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(log1: EventLog, log2: EventLog, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> typing.ListAlignments:
    """
    Aligns each trace of the first log against the second log, minimizing the edit distance

    Parameters
    --------------
    log1
        First log
    log2
        Second log
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    aligned_traces
        List that contains, for each trace of the first log, the corresponding alignment
    """
    if parameters is None:
        parameters = {}

    log1 = log_converter.apply(log1, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)
    log2 = log_converter.apply(log2, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    anti_alignment = exec_utils.get_param_value(Parameters.PERFORM_ANTI_ALIGNMENT, parameters, False)

    aligned_traces = []

    # form a mapping dictionary associating each activity of the two logs to an ASCII character
    mapping = log_regex.form_encoding_dictio_from_two_logs(log1, log2, parameters=parameters)
    # encode the second log (against which we want to align each trace of the first log)
    list_encodings = log_regex.get_encoded_log(log2, mapping, parameters=parameters)
    # optimization: keep one item per variant
    set_encodings = set(list_encodings)
    list_encodings = list(set_encodings)
    # this initial sort helps in reducing the execution time in the following phases,
    # since the expense of all the successive sorts is reduced
    if anti_alignment:
        list_encodings = sorted(list_encodings, key=lambda x: -len(x))
    else:
        list_encodings = sorted(list_encodings, key=lambda x: len(x))

    # keeps an alignment cache (to avoid re-calculating the same edit distances :) )
    cache_align = {}

    best_worst_cost = min(len(x) for x in list_encodings)

    for trace in log1:
        # gets the alignment
        align_result = align_trace(trace, list_encodings, set_encodings, mapping, cache_align=cache_align,
                                   parameters=parameters)
        aligned_traces.append(align_result)

    # assign fitness to traces
    for index, align in enumerate(aligned_traces):
        if align is not None:
            unfitness_upper_part = align['cost'] // align_utils.STD_MODEL_LOG_MOVE_COST
            if unfitness_upper_part == 0:
                align['fitness'] = 1
            elif (len(log1[index]) + best_worst_cost) > 0:
                align['fitness'] = 1 - (
                        (align['cost'] // align_utils.STD_MODEL_LOG_MOVE_COST) / (len(log1[index]) + best_worst_cost))
            else:
                align['fitness'] = 0
            align["bwc"] = (len(log1[index]) + best_worst_cost) * align_utils.STD_MODEL_LOG_MOVE_COST

    return aligned_traces


def align_trace(trace: Trace, list_encodings: List[str], set_encodings: Set[str], mapping: Dict[str, str],
                cache_align: Optional[Dict[Any, Any]] = None,
                parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> typing.AlignmentResult:
    """
    Aligns a trace against a list of traces, minimizing the edit distance

    Parameters
    --------------
    trace
        Trace
    list_encodings
        List of encoded traces (the same as set_encodings, but as a list)
    set_encodings
        Set of encoded traces (the same as list_encodings, but as a set),
        useful to quickly check if the provided trace is contained in the traces of the other log
    mapping
        Mapping (of activities to characters)
    cache_align
        Cache of the alignments
    parameters
        Parameters of the algorithm

    Returns
    --------------
    aligned_trace
        Aligned trace
    """
    if parameters is None:
        parameters = {}

    # keeps an alignment cache (to avoid re-calculating the same edit distances :) )
    if cache_align is None:
        cache_align = {}

    anti_alignment = exec_utils.get_param_value(Parameters.PERFORM_ANTI_ALIGNMENT, parameters, False)
    comparison_function = string_distance.argmax_levenshtein if anti_alignment else string_distance.argmin_levenshtein

    # encode the current trace using the mapping dictionary
    encoded_trace = log_regex.get_encoded_trace(trace, mapping, parameters=parameters)
    inv_mapping = {y: x for x, y in mapping.items()}

    if encoded_trace not in cache_align:
        if not anti_alignment and encoded_trace in set_encodings:
            # the trace is already in the encodings. we don't need to calculate any edit distance
            argmin_dist = encoded_trace
        else:
            # finds the encoded trace of the other log that is at minimal distance
            argmin_dist = comparison_function(encoded_trace, list_encodings)

        seq_match = difflib.SequenceMatcher(None, encoded_trace, argmin_dist).get_matching_blocks()
        i = 0
        j = 0
        align_trace = []
        total_cost = 0
        for el in seq_match:
            while i < el.a:
                align_trace.append((inv_mapping[encoded_trace[i]], ">>"))
                total_cost += align_utils.STD_MODEL_LOG_MOVE_COST
                i = i + 1
            while j < el.b:
                align_trace.append((">>", inv_mapping[argmin_dist[j]]))
                total_cost += align_utils.STD_MODEL_LOG_MOVE_COST
                j = j + 1
            for z in range(el.size):
                align_trace.append((inv_mapping[encoded_trace[i]], inv_mapping[argmin_dist[j]]))
                i = i + 1
                j = j + 1

        align = {"alignment": align_trace, "cost": total_cost}
        # saves the alignment in the cache
        cache_align[encoded_trace] = align
        return align
    else:
        return cache_align[encoded_trace]


def project_log_on_variant(log: Union[EventLog, pd.DataFrame], variant: List[str], parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> EventLog:
    """
    Projects the traces of an event log to the specified variant, in order to assess the conformance of the different
    directly-follows relationships and their performance (as the timestamps are recorded).
    The result is a event log where each 'projected' trace can be replayed on the given variant.
    Each event of a 'projected' trace has the '@@is_conforming' attribute set to:
    - True when the activity is mimicked by the original trace (sync move)
    - False when the activity is not reflected in the original trace (move-on-model)
    Move-on-log (activities of the trace that are not mimicked by the variant) are skipped altogether.

    Minimum Viable Example:

        import pm4py
        from pm4py.algo.conformance.alignments.edit_distance.variants import edit_distance

        log = pm4py.read_xes("tests/input_data/receipt.xes", return_legacy_log_object=True)
        variant = ('Confirmation of receipt', 'T02 Check confirmation of receipt', 'T04 Determine confirmation of receipt',
           'T05 Print and send confirmation of receipt', 'T06 Determine necessity of stop advice',
           'T10 Determine necessity to stop indication')

        projected_log = edit_distance.project_log_on_variant(log, variant)
        pm4py.write_xes(projected_log, "projected_log2.xes")


    Parameters
    ---------------
    log
        Event log
    variant
        Considered variant
    parameters
        Parameters of the method, including:
            - Parameters.ACTIVITY_KEY => the attribute of the event log to be used as activity
            - Parameters.TIMESTAMP_KEY => the attribute of the event log to be used as timestamp

    Returns
    ---------------
    projected_log
        Projected event log with the aforementioned features
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    timestamp_key = exec_utils.get_param_value(Parameters.TIMESTAMP_KEY, parameters, xes_constants.DEFAULT_TIMESTAMP_KEY)

    log = log_converter.apply(log, parameters=parameters)

    log2 = EventLog()
    trace = Trace()
    log2.append(trace)
    for act in variant:
        trace.append(Event({activity_key: act}))

    aligned_traces = apply(log, log2, parameters=parameters)

    projected_log = EventLog()
    projected_log.attributes["@@aligned_variant"] = ",".join(variant)

    for i in range(len(log)):
        projected_trace = Trace()
        projected_trace.attributes["@@original_trace"] = ",".join(x[activity_key] for x in log[i])

        if len(log[i]) > 0:
            trace = log[i]
            alignment = aligned_traces[i]["alignment"]
            z = 0
            curr_timestamp = trace[z][timestamp_key]

            for j in range(len(alignment)):
                if alignment[j][1] == ">>":
                    # move on log
                    pass
                elif alignment[j][0] == ">>" or alignment[j][0] == alignment[j][1]:
                    is_conforming = False
                    if alignment[j][0] != ">>":
                        # sync move
                        curr_timestamp = trace[z][timestamp_key]
                        is_conforming = True
                        z = z + 1
                    event = Event({activity_key: alignment[j][1], timestamp_key: curr_timestamp,
                                   "@@is_conforming": is_conforming})
                    projected_trace.append(event)

            projected_log.append(projected_trace)

    return projected_log
