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
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.algo.conformance.alignments.decomposed import algorithm as decomp_alignments
from pm4py.util import exec_utils
from enum import Enum
from pm4py.util import constants
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, Trace
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.util import typing


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    TOKEN_REPLAY_VARIANT = "token_replay_variant"
    CLEANING_TOKEN_FLOOD = "cleaning_token_flood"
    MULTIPROCESSING = "multiprocessing"


def evaluate(aligned_traces: typing.ListAlignments, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, float]:
    """
    Transforms the alignment result to a simple dictionary
    including the percentage of fit traces and the average fitness

    Parameters
    ----------
    aligned_traces
        Alignments calculated for the traces in the log
    parameters
        Possible parameters of the evaluation

    Returns
    ----------
    dictionary
        Containing two keys (percFitTraces and averageFitness)
    """
    if parameters is None:
        parameters = {}
    str(parameters)
    no_traces = len([x for x in aligned_traces if x is not None])
    no_fit_traces = 0
    sum_fitness = 0.0
    sum_bwc = 0.0
    sum_cost = 0.0

    for tr in aligned_traces:
        if tr is not None:
            if tr["fitness"] == 1.0:
                no_fit_traces = no_fit_traces + 1
            sum_fitness += tr["fitness"]
            if "bwc" in tr and "cost" in tr:
                sum_bwc += tr["bwc"]
                sum_cost += tr["cost"]

    perc_fit_traces = 0.0
    average_fitness = 0.0
    log_fitness = 0.0

    if no_traces > 0:
        perc_fit_traces = (100.0 * float(no_fit_traces)) / (float(no_traces))
        average_fitness = float(sum_fitness) / float(no_traces)
        log_fitness = float(sum_cost) / float(sum_bwc) if sum_bwc > 0 else 0
        log_fitness = 1.0 - log_fitness

    return {"percFitTraces": perc_fit_traces, "averageFitness": average_fitness,
            "percentage_of_fitting_traces": perc_fit_traces,
            "average_trace_fitness": average_fitness, "log_fitness": log_fitness}


def apply(log: EventLog, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, align_variant=alignments.DEFAULT_VARIANT, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Dict[str, float]:
    """
    Evaluate fitness based on alignments

    Parameters
    ----------------
    log
        Event log
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    align_variant
        Variants of the alignments to apply
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    dictionary
        Containing two keys (percFitTraces and averageFitness)
    """
    if parameters is None:
        parameters = {}

    multiprocessing = exec_utils.get_param_value(Parameters.MULTIPROCESSING, parameters, constants.ENABLE_MULTIPROCESSING_DEFAULT)

    if align_variant == decomp_alignments.Variants.RECOMPOS_MAXIMAL.value:
        alignment_result = decomp_alignments.apply(log, petri_net, initial_marking, final_marking,
                                                   variant=align_variant, parameters=parameters)
    else:
        if multiprocessing:
            alignment_result = alignments.apply_multiprocessing(log, petri_net, initial_marking, final_marking, variant=align_variant,
                                                parameters=parameters)
        else:
            alignment_result = alignments.apply(log, petri_net, initial_marking, final_marking, variant=align_variant,
                                                parameters=parameters)
    return evaluate(alignment_result)


def apply_trace(trace: Trace, petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, best_worst: Any, activity_key: str) -> typing.AlignmentResult:
    """
    Performs the basic alignment search, given a trace, a net and the costs of the \"best of the worst\".
    The costs of the best of the worst allows us to deduce the fitness of the trace.
    We compute the fitness by means of 1 - alignment costs / best of worst costs (i.e. costs of 0 => fitness 1)

    Parameters
    ----------
    trace: :class:`list` input trace, assumed to be a list of events (i.e. the code will use the activity key to
    get the attributes)
    petri_net: :class:`pm4py.objects.petri.net.PetriNet` the Petri net to use in the alignment
    initial_marking: :class:`pm4py.objects.petri.net.Marking` initial marking in the Petri net
    final_marking: :class:`pm4py.objects.petri.net.Marking` final marking in the Petri net
    best_worst: cost of the best worst alignment of a trace (empty trace aligned to the model)
    activity_key: :class:`str` (optional) key to use to identify the activity described by the events

    Returns
    -------
    dictionary: `dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and **traversed_arcs**
    """
    alignment = alignments.apply_trace(trace, petri_net, initial_marking, final_marking,
                                       {Parameters.ACTIVITY_KEY: activity_key})
    fixed_costs = alignment['cost'] // alignments.utils.STD_MODEL_LOG_MOVE_COST
    if best_worst > 0:
        fitness = 1 - (fixed_costs / best_worst)
    else:
        fitness = 1
    return {'trace': trace, 'alignment': alignment['alignment'], 'cost': fixed_costs, 'fitness': fitness,
            'visited_states': alignment['visited_states'], 'queued_states': alignment['queued_states'],
            'traversed_arcs': alignment['traversed_arcs']}
