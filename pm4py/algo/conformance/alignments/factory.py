from copy import copy

import pm4py
from pm4py import util as pmutil
from pm4py.algo.conformance import alignments as ali
from pm4py.algo.conformance.alignments import versions
from pm4py.algo.conformance.alignments.utils import STD_MODEL_LOG_MOVE_COST
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_MODEL_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_SYNC_COST_FUNCTION
from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_TRACE_COST_FUNCTION
from pm4py.objects.conversion.log import factory as log_converter
from pm4py.objects.log.util import general as log_util
from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ACTIVITY_KEY

VERSION_STATE_EQUATION_A_STAR = 'state_equation_a_star'
VERSIONS = {VERSION_STATE_EQUATION_A_STAR: versions.state_equation_a_star.apply}
VERSIONS_COST = {VERSION_STATE_EQUATION_A_STAR: versions.state_equation_a_star.get_best_worst_cost}


def apply(obj, petri_net, initial_marking, final_marking, parameters=None, version=VERSION_STATE_EQUATION_A_STAR):
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = log_util.CASE_ATTRIBUTE_GLUE
    if isinstance(obj, pm4py.objects.log.log.Trace):
        return apply_trace(obj, petri_net, initial_marking, final_marking, parameters, version)
    else:
        return apply_log(log_converter.apply(obj, parameters, log_converter.TO_EVENT_LOG), petri_net, initial_marking,
                         final_marking, parameters, version)


def apply_trace(trace, petri_net, initial_marking, final_marking, parameters=None,
                version=VERSION_STATE_EQUATION_A_STAR):
    """
    apply alignments to a trace

    Parameters
    -----------
    trace
        :class:`pm4py.log.log.Trace` trace of events
    petri_net
        :class:`pm4py.objects.petri.petrinet.PetriNet` the model to use for the alignment
    initial_marking
        :class:`pm4py.objects.petri.petrinet.Marking` initial marking of the net
    final_marking
        :class:`pm4py.objects.petri.petrinet.Marking` final marking of the net
    version
        :class:`str` selected variant of the algorithm, possible values: {\'state_equation_a_star\'}
    parameters
        :class:`dict` parameters of the algorithm, for key \'state_equation_a_star\':
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Attribute in the log that contains the activity
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION ->
            mapping of each transition in the model to corresponding synchronous costs
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION ->
            mapping of each transition in the model to corresponding model cost
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION ->
            mapping of each index of the trace to a positive cost value


    Returns
    -----------
    alignment
        :class:`dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and
        **traversed_arcs**
        The alignment is a sequence of labels of the form (a,t), (a,>>), or (>>,t)
        representing synchronous/log/model-moves.
    """
    if parameters is None:
        parameters = copy({PARAMETER_CONSTANT_ACTIVITY_KEY: DEFAULT_NAME_KEY})
    if PARAM_TRACE_COST_FUNCTION not in parameters:
        parameters[PARAM_TRACE_COST_FUNCTION] = list(
            map(lambda e: STD_MODEL_LOG_MOVE_COST, trace))
    return VERSIONS[version](trace, petri_net, initial_marking, final_marking, parameters)


def apply_log(log, petri_net, initial_marking, final_marking, parameters=None, version=VERSION_STATE_EQUATION_A_STAR):
    """
    apply alignments to a trace

    Parameters
    -----------
    log
        object of the form :class:`pm4py.log.log.Trace` trace of events
    petri_net
        :class:`pm4py.objects.petri.petrinet.PetriNet` the model to use for the alignment
    initial_marking
        :class:`pm4py.objects.petri.petrinet.Marking` initial marking of the net
    final_marking
        :class:`pm4py.objects.petri.petrinet.Marking` final marking of the net
    version
        :class:`str` selected variant of the algorithm, possible values: {\'state_equation_a_star\'}
    parameters
        :class:`dict` parameters of the algorithm,
        for key \'state_equation_a_star\':
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Attribute in the log that contains the activity
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_MODEL_COST_FUNCTION ->
            mapping of each transition in the model to corresponding synchronous costs
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_SYNC_COST_FUNCTION ->
            mapping of each transition in the model to corresponding model cost
            pm4py.algo.conformance.alignments.versions.state_equation_a_star.PARAM_TRACE_COST_FUNCTION ->
            mapping of each index of the trace to a positive cost value


    Returns
    -----------
    alignment
        :class:`dict` with keys **alignment**, **cost**, **visited_states**, **queued_states** and
        **traversed_arcs**
        The alignment is a sequence of labels of the form (a,t), (a,>>), or (>>,t)
        representing synchronous/log/model-moves.
    """
    if parameters is None:
        parameters = dict()
    activity_key = parameters[
        PARAMETER_CONSTANT_ACTIVITY_KEY] if PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else DEFAULT_NAME_KEY
    model_cost_function = parameters[
        PARAM_MODEL_COST_FUNCTION] if PARAM_MODEL_COST_FUNCTION in parameters else None
    sync_cost_function = parameters[
        PARAM_SYNC_COST_FUNCTION] if PARAM_SYNC_COST_FUNCTION in parameters else None
    if model_cost_function is None or sync_cost_function is None:
        # reset variables value
        model_cost_function = dict()
        sync_cost_function = dict()
        for t in petri_net.transitions:
            if t.label is not None:
                model_cost_function[t] = ali.utils.STD_MODEL_LOG_MOVE_COST
                sync_cost_function[t] = 0
            else:
                model_cost_function[t] = 1

    parameters[pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = activity_key
    parameters[
        PARAM_MODEL_COST_FUNCTION] = model_cost_function
    parameters[
        PARAM_SYNC_COST_FUNCTION] = sync_cost_function
    best_worst_cost = VERSIONS_COST[version](petri_net, initial_marking, final_marking, parameters=parameters)
    alignments = list(map(
        lambda trace: apply_trace(trace, petri_net, initial_marking, final_marking, parameters=copy(parameters),
                                  version=version),
        log))

    # assign fitness to traces
    for index, align in enumerate(alignments):
        # align_cost = align['cost'] // ali.utils.STD_MODEL_LOG_MOVE_COST
        # align['fitness'] = 1 - ((align['cost']  // ali.utils.STD_MODEL_LOG_MOVE_COST) / best_worst_cost)
        align['fitness'] = 1 - (
                (align['cost'] // ali.utils.STD_MODEL_LOG_MOVE_COST) / (len(log[index]) + best_worst_cost))

    return alignments
