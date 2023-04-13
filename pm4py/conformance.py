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
__doc__ = """
The ``pm4py.conformance`` module contains the conformance checking algorithms implemented in ``pm4py``
"""

import warnings
from typing import List, Dict, Any, Union, Optional, Tuple, Set

from pm4py.objects.log.obj import EventLog, Trace, Event, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.convert import convert_to_event_log
from collections import Counter
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util import xes_constants, constants
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
import pandas as pd
import deprecation


def conformance_diagnostics_token_based_replay(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking,
                                               final_marking: Marking, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", return_diagnostics_dataframe: bool = constants.DEFAULT_RETURN_DIAGNOSTICS_DATAFRAME) -> List[Dict[str, Any]]:
    """
    Apply token-based replay for conformance checking analysis.
    The methods return the full token-based-replay diagnostics.

    Token-based replay matches a trace and a Petri net model, starting from the initial place, in order to discover which transitions are executed and in which places we have remaining or missing tokens for the given process instance. Token-based replay is useful for Conformance Checking: indeed, a trace is fitting according to the model if, during its execution, the transitions can be fired without the need to insert any missing token. If the reaching of the final marking is imposed, then a trace is fitting if it reaches the final marking without any missing or remaining tokens.

    In PM4Py there is an implementation of a token replayer that is able to go across hidden transitions (calculating shortest paths between places) and can be used with any Petri net model with unique visible transitions and hidden transitions. When a visible transition needs to be fired and not all places in the preset are provided with the correct number of tokens, starting from the current marking it is checked if for some place there is a sequence of hidden transitions that could be fired in order to enable the visible transition. The hidden transitions are then fired and a marking that permits to enable the visible transition is reached.
    The approach is described in:
    Berti, Alessandro, and Wil MP van der Aalst. "Reviving Token-based Replay: Increasing Speed While Improving Diagnostics." ATAED@ Petri Nets/ACSD. 2019.

    The output of the token-based replay, stored in the variable replayed_traces, contains for each trace of the log:

    - trace_is_fit: boolean value (True/False) that is true when the trace is according to the model.
    - activated_transitions: list of transitions activated in the model by the token-based replay.
    - reached_marking: marking reached at the end of the replay.
    - missing_tokens: number of missing tokens.
    - consumed_tokens: number of consumed tokens.
    - remaining_tokens: number of remaining tokens.
    - produced_tokens: number of produced tokens.

    :param log: event log
    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param return_diagnostics_dataframe: if possible, returns a dataframe with the diagnostics (instead of the usual output)
    :rtype: ``List[Dict[str, Any]]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        tbr_diagnostics = pm4py.conformance_diagnostics_token_based_replay(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if return_diagnostics_dataframe:
        log = convert_to_event_log(log, case_id_key=case_id_key)
        case_id_key = None

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
    result = token_replay.apply(log, petri_net, initial_marking, final_marking, parameters=properties)

    if return_diagnostics_dataframe:
        return token_replay.get_diagnostics_dataframe(log, result, parameters=properties)

    return result


def conformance_diagnostics_alignments(log: Union[EventLog, pd.DataFrame], *args, multi_processing: bool = constants.ENABLE_MULTIPROCESSING_DEFAULT, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", variant_str : Optional[str] = None, return_diagnostics_dataframe: bool = constants.DEFAULT_RETURN_DIAGNOSTICS_DATAFRAME) -> List[Dict[str, Any]]:
    """
    Apply the alignments algorithm between a log and a process model.
    The methods return the full alignment diagnostics.

    Alignment-based replay aims to find one of the best alignment between the trace and the model. For each trace, the output of an alignment is a list of couples where the first element is an event (of the trace) or » and the second element is a transition (of the model) or ». For each couple, the following classification could be provided:

    - Sync move: the classification of the event corresponds to the transition label; in this case, both the trace and the model advance in the same way during the replay.
    - Move on log: for couples where the second element is », it corresponds to a replay move in the trace that is not mimicked in the model. This kind of move is unfit and signal a deviation between the trace and the model.
    - Move on model: for couples where the first element is », it corresponds to a replay move in the model that is not mimicked in the trace. For moves on model, we can have the following distinction:
        * Moves on model involving hidden transitions: in this case, even if it is not a sync move, the move is fit.
        * Moves on model not involving hidden transitions: in this case, the move is unfit and signals a deviation between the trace and the model.

    With each trace, a dictionary containing among the others the following information is associated:

    alignment: contains the alignment (sync moves, moves on log, moves on model)
    cost: contains the cost of the alignment according to the provided cost function
    fitness: is equal to 1 if the trace is perfectly fitting.

    :param log: event log
    :param args: specification of the process model
    :param multi_processing: boolean value that enables the multiprocessing
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param variant_str: variant specification (for Petri net alignments)
    :param return_diagnostics_dataframe: if possible, returns a dataframe with the diagnostics (instead of the usual output)
    :rtype: ``List[Dict[str, Any]]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        alignments_diagnostics = pm4py.conformance_diagnostics_alignments(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if return_diagnostics_dataframe:
        log = convert_to_event_log(log, case_id_key=case_id_key)
        case_id_key = None

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if len(args) == 3:
        if type(args[0]) is PetriNet:
            # Petri net alignments
            from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
            variant = alignments.DEFAULT_VARIANT
            if variant_str is not None:
                variant = variant_str
            if multi_processing:
                result = alignments.apply_multiprocessing(log, args[0], args[1], args[2], parameters=properties, variant=variant)
            else:
                result = alignments.apply(log, args[0], args[1], args[2], parameters=properties, variant=variant)

            if return_diagnostics_dataframe:
                return alignments.get_diagnostics_dataframe(log, result, parameters=properties)

            return result
        elif isinstance(args[0], dict):
            # DFG alignments
            from pm4py.algo.conformance.alignments.dfg import algorithm as dfg_alignment
            result = dfg_alignment.apply(log, args[0], args[1], args[2], parameters=properties)

            return result
    elif len(args) == 1:
        if type(args[0]) is ProcessTree:
            # process tree alignments
            from pm4py.algo.conformance.alignments.process_tree.variants import search_graph_pt
            if multi_processing:
                result = search_graph_pt.apply_multiprocessing(log, args[0], parameters=properties)
            else:
                result = search_graph_pt.apply(log, args[0], parameters=properties)

            return result
    # try to convert to Petri net
    import pm4py
    from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
    net, im, fm = pm4py.convert_to_petri_net(*args)
    if multi_processing:
        result = alignments.apply_multiprocessing(log, net, im, fm, parameters=properties)
    else:
        result = alignments.apply(log, net, im, fm, parameters=properties)

    if return_diagnostics_dataframe:
        return alignments.get_diagnostics_dataframe(log, result, parameters=properties)

    return result


def fitness_token_based_replay(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> \
        Dict[
            str, float]:
    """
    Calculates the fitness using token-based replay.
    The fitness is calculated on a log-based level.

    Token-based replay matches a trace and a Petri net model, starting from the initial place, in order to discover which transitions are executed and in which places we have remaining or missing tokens for the given process instance. Token-based replay is useful for Conformance Checking: indeed, a trace is fitting according to the model if, during its execution, the transitions can be fired without the need to insert any missing token. If the reaching of the final marking is imposed, then a trace is fitting if it reaches the final marking without any missing or remaining tokens.

    In PM4Py there is an implementation of a token replayer that is able to go across hidden transitions (calculating shortest paths between places) and can be used with any Petri net model with unique visible transitions and hidden transitions. When a visible transition needs to be fired and not all places in the preset are provided with the correct number of tokens, starting from the current marking it is checked if for some place there is a sequence of hidden transitions that could be fired in order to enable the visible transition. The hidden transitions are then fired and a marking that permits to enable the visible transition is reached.
    The approach is described in:
    Berti, Alessandro, and Wil MP van der Aalst. "Reviving Token-based Replay: Increasing Speed While Improving Diagnostics." ATAED@ Petri Nets/ACSD. 2019.

    The calculation of the replay fitness aim to calculate how much of the behavior in the log is admitted by the process model. We propose two methods to calculate replay fitness, based on token-based replay and alignments respectively.

    For token-based replay, the percentage of traces that are completely fit is returned, along with a fitness value that is calculated as indicated in the scientific contribution

    :param log: event log
    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, float]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        fitness_tbr = pm4py.fitness_token_based_replay(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
    result = replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.TOKEN_BASED, parameters=properties)

    return result


def fitness_alignments(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking, final_marking: Marking, multi_processing: bool = constants.ENABLE_MULTIPROCESSING_DEFAULT, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> \
        Dict[str, float]:
    """
    Calculates the fitness using alignments

    Alignment-based replay aims to find one of the best alignment between the trace and the model. For each trace, the output of an alignment is a list of couples where the first element is an event (of the trace) or » and the second element is a transition (of the model) or ». For each couple, the following classification could be provided:

    - Sync move: the classification of the event corresponds to the transition label; in this case, both the trace and the model advance in the same way during the replay.
    - Move on log: for couples where the second element is », it corresponds to a replay move in the trace that is not mimicked in the model. This kind of move is unfit and signal a deviation between the trace and the model.
    - Move on model: for couples where the first element is », it corresponds to a replay move in the model that is not mimicked in the trace. For moves on model, we can have the following distinction:
        * Moves on model involving hidden transitions: in this case, even if it is not a sync move, the move is fit.
        * Moves on model not involving hidden transitions: in this case, the move is unfit and signals a deviation between the trace and the model.

    The calculation of the replay fitness aim to calculate how much of the behavior in the log is admitted by the process model. We propose two methods to calculate replay fitness, based on token-based replay and alignments respectively.

    For alignments, the percentage of traces that are completely fit is returned, along with a fitness value that is calculated as the average of the fitness values of the single traces.

    :param log: event log
    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :param multi_processing: boolean value that enables the multiprocessing
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``Dict[str, float]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        fitness_alignments = pm4py.fitness_alignments(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["multiprocessing"] = multi_processing
    result = replay_fitness.apply(log, petri_net, initial_marking, final_marking,
                                variant=replay_fitness.Variants.ALIGNMENT_BASED, parameters=parameters)

    return result


def precision_token_based_replay(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking,
                                 final_marking: Marking, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> float:
    """
    Calculates the precision precision using token-based replay

    Token-based replay matches a trace and a Petri net model, starting from the initial place, in order to discover which transitions are executed and in which places we have remaining or missing tokens for the given process instance. Token-based replay is useful for Conformance Checking: indeed, a trace is fitting according to the model if, during its execution, the transitions can be fired without the need to insert any missing token. If the reaching of the final marking is imposed, then a trace is fitting if it reaches the final marking without any missing or remaining tokens.

    In PM4Py there is an implementation of a token replayer that is able to go across hidden transitions (calculating shortest paths between places) and can be used with any Petri net model with unique visible transitions and hidden transitions. When a visible transition needs to be fired and not all places in the preset are provided with the correct number of tokens, starting from the current marking it is checked if for some place there is a sequence of hidden transitions that could be fired in order to enable the visible transition. The hidden transitions are then fired and a marking that permits to enable the visible transition is reached.
    The approach is described in:
    Berti, Alessandro, and Wil MP van der Aalst. "Reviving Token-based Replay: Increasing Speed While Improving Diagnostics." ATAED@ Petri Nets/ACSD. 2019.

    The reference paper for the TBR-based precision (ETConformance) is:
    Muñoz-Gama, Jorge, and Josep Carmona. "A fresh look at precision in process conformance." International Conference on Business Process Management. Springer, Berlin, Heidelberg, 2010.

    In this approach, the different prefixes of the log are replayed (whether possible) on the model. At the reached marking, the set of transitions that are enabled in the process model is compared with the set of activities that follow the prefix. The more the sets are different, the more the precision value is low. The more the sets are similar, the more the precision value is high.

    :param log: event log
    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        precision_tbr = pm4py.precision_token_based_replay(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    result = precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN, parameters=properties)

    return result


def precision_alignments(log: Union[EventLog, pd.DataFrame], petri_net: PetriNet, initial_marking: Marking,
                         final_marking: Marking, multi_processing: bool = constants.ENABLE_MULTIPROCESSING_DEFAULT, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> float:
    """
    Calculates the precision of the model w.r.t. the event log using alignments

    Alignment-based replay aims to find one of the best alignment between the trace and the model. For each trace, the output of an alignment is a list of couples where the first element is an event (of the trace) or » and the second element is a transition (of the model) or ». For each couple, the following classification could be provided:

    - Sync move: the classification of the event corresponds to the transition label; in this case, both the trace and the model advance in the same way during the replay.
    - Move on log: for couples where the second element is », it corresponds to a replay move in the trace that is not mimicked in the model. This kind of move is unfit and signal a deviation between the trace and the model.
    - Move on model: for couples where the first element is », it corresponds to a replay move in the model that is not mimicked in the trace. For moves on model, we can have the following distinction:
        * Moves on model involving hidden transitions: in this case, even if it is not a sync move, the move is fit.
        * Moves on model not involving hidden transitions: in this case, the move is unfit and signals a deviation between the trace and the model.

    The reference paper for the alignments-based precision (Align-ETConformance) is:
    Adriansyah, Arya, et al. "Measuring precision of modeled behavior." Information systems and e-Business Management 13.1 (2015): 37-67

    In this approach, the different prefixes of the log are replayed (whether possible) on the model. At the reached marking, the set of transitions that are enabled in the process model is compared with the set of activities that follow the prefix. The more the sets are different, the more the precision value is low. The more the sets are similar, the more the precision value is high.

    :param log: event log
    :param petri_net: petri net
    :param initial_marking: initial marking
    :param final_marking: final marking
    :param multi_processing: boolean value that enables the multiprocessing
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        precision_alignments = pm4py.precision_alignments(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
    parameters = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    parameters["multiprocessing"] = multi_processing
    result = precision_evaluator.apply(log, petri_net, initial_marking, final_marking,
                                     variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE,
                                     parameters=parameters)

    return result


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="conformance checking using footprints will not be exposed in a future release")
def __convert_to_fp(*args) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Internal method to convert the provided event log / process model argument
    to footprints (using footprints discovery)

    :param args: event log / process model
    :rtype: ``Union[List[Dict[str, Any]], Dict[str, Any]]``
    """
    import pm4py
    while type(args) is tuple:
        if len(args) == 1:
            args = args[0]
        else:
            fp = pm4py.discover_footprints(*args)
            return fp
    if isinstance(args, list) or isinstance(args, dict):
        return args
    fp = pm4py.discover_footprints(args)
    return fp


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="conformance checking using footprints will not be exposed in a future release")
def conformance_diagnostics_footprints(*args) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Provide conformance checking diagnostics using footprints

    :param args: provided arguments (the first argument is supposed to be an event log (or the footprints discovered from the event log); the other arguments are supposed to be the process model (or the footprints discovered from the process model).
    :rtype: ``Union[List[Dict[str, Any]], Dict[str, Any]]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        footprints_diagnostics = pm4py.conformance_diagnostics_footprints(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints import algorithm as footprints_conformance
    if isinstance(fp1, list):
        result = footprints_conformance.apply(fp1, fp2, variant=footprints_conformance.Variants.TRACE_EXTENSIVE)
    else:
        result = footprints_conformance.apply(fp1, fp2, variant=footprints_conformance.Variants.LOG_EXTENSIVE)

    return result


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="conformance checking using footprints will not be exposed in a future release")
def fitness_footprints(*args) -> Dict[str, float]:
    """
    Calculates fitness using footprints. The output is a dictionary containing two keys:
    - perc_fit_traces => percentage of fit traces (over the log)
    - log_fitness => the fitness value over the log

    :param args: provided arguments (the first argument is supposed to be an event log (or the footprints discovered from the event log); the other arguments are supposed to be the process model (or the footprints discovered from the process model).
    :rtype: ``Dict[str, float]``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        fitness_fp = pm4py.fitness_footprints(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    fp_conf = conformance_diagnostics_footprints(*args)
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints.util import evaluation
    result = evaluation.fp_fitness(fp1, fp2, fp_conf)

    return result


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="conformance checking using footprints will not be exposed in a future release")
def precision_footprints(*args) -> float:
    """
    Calculates precision using footprints

    :param args: provided arguments (the first argument is supposed to be an event log (or the footprints discovered from the event log); the other arguments are supposed to be the process model (or the footprints discovered from the process model).
    :rtype: ``float``

    .. code-block:: python3

        import pm4py

        net, im, fm = pm4py.discover_petri_net_inductive(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        precision_fp = pm4py.precision_footprints(dataframe, net, im, fm, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    fp1 = __convert_to_fp(args[0])
    fp2 = __convert_to_fp(args[1:])
    from pm4py.algo.conformance.footprints.util import evaluation
    result = evaluation.fp_precision(fp1, fp2)

    return result


@deprecation.deprecated(removed_in="2.3.0", deprecated_in="3.0.0", details="this method will be removed in a future release.")
def __check_is_fit_process_tree(trace, tree) -> bool:
    """
    Check if a trace object is fit against a process tree model

    :param trace: trace
    :param tree: process tree
    :rtype: ``bool``
    """
    __event_log_deprecation_warning(trace)

    from pm4py.discovery import discover_footprints
    log = EventLog()
    log.append(trace)
    fp_tree = discover_footprints(tree)
    fp_log = discover_footprints(log)
    fp_conf_res = conformance_diagnostics_footprints(fp_log, fp_tree)[0]
    # CHECK 1) if footprints already say is not fit, then return False
    # (if they say True, it might be a false positive)
    if not fp_conf_res["is_footprints_fit"]:
        return False
    else:
        from pm4py.convert import convert_to_petri_net
        net, im, fm = convert_to_petri_net(tree)
        tbr_conf_res = conformance_diagnostics_token_based_replay(log, net, im, fm, return_diagnostics_dataframe=False)[0]
        # CHECK 2) if TBR says that is fit, then return True
        # (if they say False, it might be a false negative)
        if tbr_conf_res["trace_is_fit"]:
            return True
        else:
            # CHECK 3) alignments definitely say if the trace is fit or not if the previous methods fail
            align_conf_res = conformance_diagnostics_alignments(log, tree, return_diagnostics_dataframe=False)[0]
            return align_conf_res["fitness"] == 1.0


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="this method will be removed in a future release.")
def __check_is_fit_petri_net(trace, net, im, fm, activity_key=xes_constants.DEFAULT_NAME_KEY) -> bool:
    """
    Checks if a trace object is fit against Petri net object

    :param trace: trace
    :param net: petri net
    :param im: initial marking
    :param fm: final marking
    :param activity_key: attribute to be used as activity
    :rtype: ``bool``
    """
    __event_log_deprecation_warning(trace)

    # avoid checking footprints on Petri net (they are too slow)
    activities_model = set(trans.label for trans in net.transitions if trans.label is not None)
    activities_trace = set([x[activity_key] for x in trace])
    diff = activities_trace.difference(activities_model)
    if diff:
        # CHECK 1) there are activities in the trace that are not in the model
        return False
    else:
        log = EventLog()
        log.append(trace)
        tbr_conf_res = conformance_diagnostics_token_based_replay(log, net, im, fm, return_diagnostics_dataframe=False)[0]
        # CHECK 2) if TBR says that is fit, then return True
        # (if they say False, it might be a false negative)
        if tbr_conf_res["trace_is_fit"]:
            return True
        else:
            # CHECK 3) alignments definitely say if the trace is fit or not if the previous methods fail
            align_conf_res = conformance_diagnostics_alignments(log, net, im, fm, return_diagnostics_dataframe=False)[0]
            return align_conf_res["fitness"] == 1.0


@deprecation.deprecated(deprecated_in="2.3.0", removed_in="3.0.0", details="this method will be removed in a future release.")
def check_is_fitting(*args, activity_key=xes_constants.DEFAULT_NAME_KEY) -> bool:
    """
    Checks if a trace object is fit against a process model

    :param args: arguments (trace object; process model (process tree, petri net, BPMN))
    :rtype: ``bool``
    """
    from pm4py.util import variants_util
    from pm4py.convert import convert_to_process_tree, convert_to_petri_net

    trace = args[0]
    model = args[1:]

    try:
        model = convert_to_process_tree(*model)
    except:
        # the model cannot be expressed as a process tree, let's say if at least can be expressed as a Petri net
        model = convert_to_petri_net(*model)

    if not isinstance(trace, Trace):
        activities = variants_util.get_activities_from_variant(trace)
        trace = Trace()
        for act in activities:
            trace.append(Event({activity_key: act}))

    if isinstance(model, ProcessTree):
        return __check_is_fit_process_tree(trace, model)
    elif isinstance(model, tuple) and isinstance(model[0], PetriNet):
        return __check_is_fit_petri_net(trace, model[0], model[1], model[2], activity_key=activity_key)


def conformance_temporal_profile(log: Union[EventLog, pd.DataFrame], temporal_profile: Dict[Tuple[str, str], Tuple[float, float]], zeta: float = 1.0, activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name") -> List[List[Tuple[float, float, float, float]]]:
    """
    Performs conformance checking on the provided log with the provided temporal profile.
    The result is a list of time-based deviations for every case.
    E.g. if the log on top of which the conformance is applied is the following (1 case):
    A (timestamp: 2000-01)    B (timestamp: 2002-01)
    The difference between the timestamps of A and B is two years. If the temporal profile:
    {('A', 'B'): (1.5 months, 0.5 months), ('A', 'C'): (5 months, 0), ('A', 'D'): (2 months, 0)}
    is specified, and zeta is set to 1, then the aforementioned case would be deviating
    (considering the couple of activities ('A', 'B')), because 2 years > 1.5 months + 0.5 months.

    :param log: log object
    :param temporal_profile: temporal profile. E.g., if the log has two cases: A (timestamp: 1980-01)   B (timestamp: 1980-03)    C (timestamp: 1980-06); A (timestamp: 1990-01)   B (timestamp: 1990-02)    D (timestamp: 1990-03); The temporal profile will contain: {('A', 'B'): (1.5 months, 0.5 months), ('A', 'C'): (5 months, 0), ('A', 'D'): (2 months, 0)}
    :param zeta: number of standard deviations allowed from the average. E.g. zeta=1 allows every timestamp between AVERAGE-STDEV and AVERAGE+STDEV.
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :rtype: ``List[List[Tuple[float, float, float, float]]]``

    .. code-block:: python3

        import pm4py

        temporal_profile = pm4py.discover_temporal_profile(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        conformance_temporal_profile = pm4py.conformance_temporal_profile(dataframe, temporal_profile, zeta=1, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)
    properties["zeta"] = zeta

    from pm4py.algo.conformance.temporal_profile import algorithm as temporal_profile_conformance
    result = temporal_profile_conformance.apply(log, temporal_profile, parameters=properties)

    return result


def conformance_log_skeleton(log: Union[EventLog, pd.DataFrame], log_skeleton: Dict[str, Any], activity_key: str = "concept:name", timestamp_key: str = "time:timestamp", case_id_key: str = "case:concept:name", return_diagnostics_dataframe: bool = constants.DEFAULT_RETURN_DIAGNOSTICS_DATAFRAME) -> List[Set[Any]]:
    """
    Performs conformance checking using the log skeleton

    Reference paper:
    Verbeek, H. M. W., and R. Medeiros de Carvalho. "Log skeletons: A classification approach to process discovery." arXiv preprint arXiv:1806.08247 (2018).

    A log skeleton is a declarative model which consists of six different constraints:
    - "directly_follows": specifies for some activities some strict bounds on the activities directly-following. For example,
                        'A should be directly followed by B' and 'B should be directly followed by C'.
    - "always_before": specifies that some activities may be executed only if some other activities are executed somewhen before
                        in the history of the case.
                        For example, 'C should always be preceded by A'
    - "always_after": specifies that some activities should always trigger the execution of some other activities
                        in the future history of the case.
                        For example, 'A should always be followed by C'
    - "equivalence": specifies that a given couple of activities should happen with the same number of occurrences inside
                        a case.
                        For example, 'B and C should always happen the same number of times'.
    - "never_together": specifies that a given couple of activities should never happen together in the history of the case.
                        For example, 'there should be no case containing both C and D'.
    - "activ_occurrences": specifies the allowed number of occurrences per activity:
                        E.g. A is allowed to be executed 1 or 2 times, B is allowed to be executed 1 or 2 or 3 or 4 times.

    :param log: log object
    :param log_skeleton: log skeleton object, expressed as dictionaries of the six constraints (never_together, always_before ...) along with the discovered rules.
    :param activity_key: attribute to be used for the activity
    :param timestamp_key: attribute to be used for the timestamp
    :param case_id_key: attribute to be used as case identifier
    :param return_diagnostics_dataframe: if possible, returns a dataframe with the diagnostics (instead of the usual output)
    :rtype: ``List[Set[Any]]``

    .. code-block:: python3

        import pm4py

        log_skeleton = pm4py.discover_log_skeleton(dataframe, noise_threshold=0.1, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
        conformance_lsk = pm4py.conformance_log_skeleton(dataframe, log_skeleton, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
    """
    if type(log) not in [pd.DataFrame, EventLog, EventStream]: raise Exception("the method can be applied only to a traditional event log!")
    __event_log_deprecation_warning(log)

    if check_is_pandas_dataframe(log):
        check_pandas_dataframe_columns(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    if return_diagnostics_dataframe:
        log = convert_to_event_log(log, case_id_key=case_id_key)
        case_id_key = None

    properties = get_properties(log, activity_key=activity_key, timestamp_key=timestamp_key, case_id_key=case_id_key)

    from pm4py.algo.conformance.log_skeleton import algorithm as log_skeleton_conformance
    result = log_skeleton_conformance.apply(log, log_skeleton, parameters=properties)

    if return_diagnostics_dataframe:
        return log_skeleton_conformance.get_diagnostics_dataframe(log, result, parameters=properties)

    return result
