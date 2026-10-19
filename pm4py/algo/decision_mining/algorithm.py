'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''
import sys
from copy import deepcopy, copy
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple

import numpy as np
import pandas as pd

from pm4py.algo.conformance.alignments.petri_net import algorithm as ali
from pm4py.algo.conformance.alignments.petri_net.variants import (
    state_equation_a_star as star,
)
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net import properties as petri_properties
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.statistics.attributes.log.select import (
    select_attributes_from_log_for_tree,
)
from pm4py.statistics.variants.log import get as variants_module
from pm4py.util import constants, xes_constants
from pm4py.util import exec_utils, pandas_utils
from pm4py.visualization.decisiontree.util import dt_to_string


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    LABELS = "labels"


def create_data_petri_nets_with_decisions(
        log: Union[EventLog, pd.DataFrame],
        net: PetriNet,
        initial_marking: Marking,
        final_marking: Marking,
) -> Tuple[PetriNet, Marking, Marking]:
    """
    Given a Petri net, create a data Petri net with the decisions
    given for each place by the decision mining algorithm.

    Parameters
    ----------------
    log
        Event log (EventLog or DataFrame).
    net
        Petri net.
    initial_marking
        Initial marking of the Petri net.
    final_marking
        Final marking of the Petri net.

    Returns
    ------------------
    data_petri_net
        Petri net enriched with guards (conditions).
    initial_marking
        Initial marking (unchanged).
    final_marking
        Final marking (unchanged).
    """
    all_conditions = {}
    all_variables = {}

    # Attempt to build a decision tree for each place in the net
    for place in net.places:
        try:
            dt_classifier, columns, targets = get_decision_tree(
                log,
                net,
                initial_marking,
                final_marking,
                decision_point=place.name,
                parameters={"labels": False},  # by default
            )
            # Convert the scikit-learn tree into string-based conditions
            target_classes_dict, variables_dict = dt_to_string.apply(
                dt_classifier, columns
            )
            # Remap integer-based classes to the actual transitions
            target_classes = {
                targets[int(k)]: v for k, v in target_classes_dict.items()
            }
            variables = {targets[int(k)]: v for k, v in variables_dict.items()}

            # Accumulate results
            for transition_name in target_classes.keys():
                all_conditions[transition_name] = target_classes[transition_name]
                all_variables[transition_name] = variables[transition_name]

        except Exception:
            # If the decision-tree building fails for some place, ignore it
            pass

    # Attach discovered guards (conditions) to transitions
    for transition in net.transitions:
        if transition.name in all_conditions:
            transition.properties[petri_properties.TRANS_GUARD] = all_conditions[
                transition.name
            ]
            transition.properties[petri_properties.READ_VARIABLE] = all_variables[
                transition.name
            ]
            transition.properties[petri_properties.WRITE_VARIABLE] = []

    return net, initial_marking, final_marking


def get_decision_tree(
        log: Union[EventLog, pd.DataFrame],
        net: PetriNet,
        initial_marking: Marking,
        final_marking: Marking,
        decision_point=None,
        attributes=None,
        parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Any:
    """
    Gets a decision tree classifier on a specific point of the model.

    Parameters
    --------------
    log
        Event log (EventLog or DataFrame).
    net
        Petri net.
    initial_marking
        Initial marking.
    final_marking
        Final marking.
    decision_point
        Name of the place in which a decision happens:
        - if not specified, the method raises an Exception with a list of possible decision points.
    attributes
        Attributes of the log. If not specified, an automatic attribute selection is performed.
    parameters
        Parameters of the algorithm.

    Returns
    ---------------
    clf
        Fitted decision tree classifier.
    feature_names
        The names of the features used to fit the classifier.
    classes
        The classes (i.e., transitions) the classifier distinguishes.
    """
    from pm4py.util import ml_utils

    if parameters is None:
        parameters = {}

    # Compute feature matrix X, labels y, and the mapping to actual transitions
    X, y, targets = apply(
        log,
        net,
        initial_marking,
        final_marking,
        decision_point=decision_point,
        attributes=attributes,
        parameters=parameters,
    )

    # Fit a decision tree classifier
    dt_classifier = ml_utils.DecisionTreeClassifier()
    dt_classifier = dt_classifier.fit(X, y)

    # Return the classifier, the feature names, and the classes
    return dt_classifier, list(X.columns.values.tolist()), targets


def apply(
        log: Union[EventLog, pd.DataFrame],
        net: PetriNet,
        initial_marking: Marking,
        final_marking: Marking,
        decision_point=None,
        attributes=None,
        parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Any:
    """
    Gets the essential information (features, target class, and names of the target class)
    in order to learn a classifier.

    Parameters
    --------------
    log
        Event log (EventLog or DataFrame).
    net
        Petri net.
    initial_marking
        Initial marking.
    final_marking
        Final marking.
    decision_point
        The name of the place in which a decision happens.
        - If not specified, raises an Exception with a list of possible places.
    attributes
        Attributes of the log. If not specified, an automatic attribute selection is performed.
    parameters
        Parameters of the algorithm.

    Returns
    ---------------
    X
        DataFrame of features.
    y
        Series of encoded target classes (integer).
    class_name
        Mapping of integer class -> actual transition name.
    """
    if parameters is None:
        parameters = {}

    # Retrieve parameter about labeling
    labels = exec_utils.get_param_value(Parameters.LABELS, parameters, True)

    # Define the default activity key
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )

    # If decision_point is None, we provide a list of valid places and raise an Exception
    if decision_point is None:
        decision_points_names = get_decision_points(net, labels=labels, parameters=parameters)
        raise Exception(
            "Please provide 'decision_point'. Possible decision points: %s" % list(decision_points_names.keys())
        )

    # If attributes not specified, automatically select them
    if attributes is None:
        str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr = select_attributes_from_log_for_tree(log)
        attributes = list(str_ev_attr) + list(num_ev_attr)

    # Build the main "decisions table" from the log and the Petri net
    decision_info, _ = get_decisions_table(
        log,
        net,
        initial_marking,
        final_marking,
        attributes=attributes,
        pre_decision_points=[decision_point],
        parameters=parameters,
    )

    # For the chosen decision point, separate attributes (X) and target transitions (y)
    relevant_data = decision_info[decision_point]
    x_attributes = [a for a in attributes if a != activity_key]

    # We separate string and numeric attributes to handle get_dummies for strings
    str_attributes = set()
    non_str_attributes = set()

    # Lists to store intermediate results
    all_feature_dicts_str = []
    all_feature_dicts_num = []
    all_targets = []

    # For each recorded decision, collect attributes
    for (attr_dict, chosen_transition) in relevant_data:
        # Identify which attributes are string vs numeric
        for attr_name, attr_value in attr_dict.items():
            if attr_name in x_attributes:
                if isinstance(attr_value, str):
                    str_attributes.add(attr_name)
                else:
                    non_str_attributes.add(attr_name)

        # Build two partial dicts:
        # one for string columns, one for numeric columns
        all_feature_dicts_str.append({
            a: v for a, v in attr_dict.items()
            if a in x_attributes and isinstance(v, str)
        })
        all_feature_dicts_num.append({
            a: v for a, v in attr_dict.items()
            if a in x_attributes and not isinstance(v, str)
        })

        # The target is the chosen transition's label/name
        all_targets.append(chosen_transition)

    # Convert to pandas DataFrame, applying get_dummies to string features
    df_str = pandas_utils.instantiate_dataframe(all_feature_dicts_str)
    df_str = pd.get_dummies(data=df_str, columns=list(str_attributes))

    df_num = pandas_utils.instantiate_dataframe(all_feature_dicts_num)
    X = pd.concat([df_str, df_num], axis=1)

    Y = pd.DataFrame(all_targets, columns=["Name"])
    Y, targets = encode_target(Y, "Name")  # encode the target transitions
    y = Y["Target"]

    return X, y, targets


def get_decisions_table(
        log0,
        net,
        initial_marking,
        final_marking,
        attributes=None,
        use_trace_attributes=False,
        k=1,
        pre_decision_points=None,
        trace_attributes=None,
        parameters=None,
):
    """
    Builds a decision table out of a log and an accepting Petri net.

    For each place that has multiple outgoing arcs (a "decision point"),
    we record the attributes that preceded the choice of a particular transition.

    Parameters
    -----------------
    log0
        Event log (EventLog or DataFrame).
    net
        Petri net.
    initial_marking
        Initial marking.
    final_marking
        Final marking.
    attributes
        List of event attributes to consider (if not provided, all are considered).
    use_trace_attributes
        Whether to include trace attributes (e.g., case-level data) in the decision table.
    k
        Number of last events to look back at for each decision. (Default=1)
    pre_decision_points
        List of place names that should be considered. If None, the code infers them automatically.
    trace_attributes
        List of trace attribute names to consider. If None, all are considered (if use_trace_attributes=True).
    parameters
        Additional parameters (e.g., {Parameters.LABELS: True/False}).

    Returns
    --------------
    I
        A dictionary keyed by place name. Values are lists of tuples (dict_of_attributes, chosen_transition).
    decision_points
        The dictionary of decision points (places with multiple outgoing arcs),
        possibly filtered by `pre_decision_points`.
    """
    if parameters is None:
        parameters = {}

    # Convert input log to pm4py EventLog if it's a DataFrame
    log = log_converter.apply(log0, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    # Validate some of the inputs
    _validate_inputs_for_decision_table(
        pre_decision_points, attributes, use_trace_attributes, trace_attributes
    )

    # Identify actual decision points
    # (places that have >=2 outgoing arcs)
    decision_points = get_decision_points(
        net, pre_decision_points=pre_decision_points, parameters=parameters
    )
    # Also get decision point labels if needed
    decision_points_names = get_decision_points(
        net, labels=True, pre_decision_points=pre_decision_points, parameters=parameters
    )

    # Possibly rename trace/event attributes to avoid collisions
    if use_trace_attributes:
        log = prepare_event_log(log)
        if attributes is not None:
            attributes = prepare_attributes(attributes)

    # If no explicit trace_attributes are given, collect from the log
    if use_trace_attributes and trace_attributes is None:
        trace_attributes = set()
        for trace in log:
            trace_attributes.update(trace.attributes.keys())
        trace_attributes = list(trace_attributes)

    # If attributes are still None, collect all event attributes from the log
    if attributes is None:
        attributes = set()
        for trace in log:
            for event in trace:
                attributes.update(list(event.keys()))
        attributes = list(attributes)

    # Now build the dictionary of decision info
    # Each key is a place name, and the value is a list of (attributes_dict, chosen_transition)
    decision_info = _build_decision_info(
        log,
        net,
        initial_marking,
        final_marking,
        decision_points,
        decision_points_names,
        attributes,
        use_trace_attributes,
        trace_attributes,
        k,
        parameters,
    )
    return (decision_info, decision_points)


def prepare_event_log(log):
    """
    If trace attributes are considered, we want to differentiate them from
    event attributes. For trace attributes, we prepend ``t_``. For event
    attributes, we prepend ``e_``.

    This helps avoid collisions when both trace and event attributes share the same name.

    Parameters
    ----------
    log : EventLog
        The original log.

    Returns
    -------
    EventLog
        The modified log with attribute names prefixed.
    """
    for trace in log:
        # Prefix trace attributes with "t_"
        trace_attrs_copy = dict(trace.attributes)
        for attribute in trace_attrs_copy:
            new_key = "t_" + attribute
            trace.attributes[new_key] = trace.attributes.pop(attribute)

        # Prefix event attributes with "e_"
        for event in trace:
            event_attrs_copy = dict(event._dict)
            for attribute in event_attrs_copy:
                new_key = "e_" + attribute
                event._dict[new_key] = event._dict.pop(attribute)

    return log


def prepare_attributes(attributes):
    """
    If trace attributes are considered, we assume all the user-provided
    attributes refer to event attributes and prepend ``e_`` to them.

    Parameters
    ----------
    attributes : list
        List of original attribute names.

    Returns
    -----------------
    list
        List of attribute names, each prefixed by ``e_``.

    """
    new_attributes = []
    for attribute in attributes:
        new_attributes.append("e_" + attribute)
    return new_attributes


def get_decision_points(
        net, labels=False, pre_decision_points=None, parameters=None
):
    """
    Identifies "decision points" in the net, i.e., places with >= 2 outgoing arcs.

    Parameters
    ----------
    net : PetriNet
        The Petri net under analysis.
    labels : bool
        Whether to list the labels of transitions as values rather than the raw transition names.
    pre_decision_points : list or None
        If provided, only return decision points that appear in this list (filter).
    parameters : dict
        (Unused in this function except for consistency.)

    Returns
    -------
    dict
        A dictionary mapping place_name -> list of outgoing transition names or labels.
    """
    if parameters is None:
        parameters = {}

    # Build a dict {place_name -> [outgoing transitions]}
    outgoing_dict = {}
    for place in net.places:
        outgoing_dict[place.name] = []

    # For each arc that starts from a place, record the target transition
    for arc in net.arcs:
        if arc.source in net.places:
            transition_label = arc.target.label if labels else arc.target.name
            outgoing_dict[arc.source.name].append(transition_label)

    # Filter only those with >=2 outgoing arcs
    decision_points = {
        place_name: trans_list
        for place_name, trans_list in outgoing_dict.items()
        if len(trans_list) >= 2
    }

    # If user gave a specific list of decision points, filter further
    if pre_decision_points is not None:
        _check_pre_decision_points(decision_points, pre_decision_points)

    return decision_points


def get_attributes(
        log,
        decision_points,
        attributes,
        use_trace_attributes,
        trace_attributes,
        k,
        net,
        initial_marking,
        final_marking,
        decision_points_names,
        parameters=None,
):
    """
    For each decision place, this collects the final table of
    (attributes -> chosen transition) for each occurrence of a decision.

    This function internally uses token-based replay (or alignment for non-fitting traces)
    to discover the actual transitions that were used from the log.
    Then, for each place with multiple outgoing arcs, we store the attributes
    that led to a certain chosen transition.

    Parameters
    ----------
    log : EventLog
        The event log.
    decision_points : dict
        Dictionary mapping place_name -> list of possible transitions (IDs/names).
    attributes : list
        Attributes to consider from events.
    use_trace_attributes : bool
        Whether to consider trace-level attributes as well.
    trace_attributes : list
        List of trace-level attributes to consider.
    k : int
        Number of events to look back at each decision (the "window size").
    net : PetriNet
        The Petri net.
    initial_marking : Marking
        Initial marking.
    final_marking : Marking
        Final marking.
    decision_points_names : dict
        Dictionary mapping place_name -> list of transition labels (if labels=True).
    parameters : dict
        Additional parameters (e.g. {Parameters.LABELS: True/False}).

    Returns
    -------
    dict
        A dictionary keyed by place name, with each value a list of tuples:
        (attributes_dict, chosen_transition).
    """
    if parameters is None:
        parameters = {}

    # Check if transitions should use .label or .name
    labels = exec_utils.get_param_value(Parameters.LABELS, parameters, True)

    # Prepare the result structure
    decision_info = {place_name: [] for place_name in decision_points.keys()}

    # For collecting variants/traces
    variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    unique_variants = list(variants_idxs.keys())

    filtered_log = EventLog()
    for variant_name in variants_idxs:
        filtered_log.append(log[variants_idxs[variant_name][0]])

    # Token replay over the entire log
    replay_result = token_replay.apply(
        filtered_log, net, initial_marking, final_marking, parameters=parameters
    )

    # For each replayed variant
    for variant_idx, variant_name in enumerate(unique_variants):
        # Check if the replayed variant is perfectly fitting or not
        token_replay_entry = replay_result[variant_idx]

        # For each trace in this variant
        trace_indices = variants_idxs[variant_name]

        if token_replay_entry["trace_fitness"] == 1.0:
            # Perfectly fitting; we can simply rely on "activated_transitions"
            _extract_decisions_perfect_fit(
                log, trace_indices, token_replay_entry, decision_info,
                decision_points, decision_points_names, attributes,
                use_trace_attributes, trace_attributes, k, labels
            )
        else:
            # Not a perfect fit; we must do alignments for each trace in this variant
            # (We align only for the first example trace in that variant to get the alignment.)
            sample_trace_idx = trace_indices[0]
            sample_trace = log[sample_trace_idx]

            alignment_params = copy(parameters)
            alignment_params[star.Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] = True
            alignment_info = ali.apply(
                sample_trace, net, initial_marking, final_marking, parameters=alignment_params
            )

            # Now apply the same alignment to each trace in the variant
            for idx in trace_indices:
                _extract_decisions_alignment(
                    log, idx, alignment_info, decision_info, decision_points,
                    attributes, use_trace_attributes, trace_attributes, k, labels
                )

    return decision_info


def encode_target(df, target_column):
    """
    Adds a 'Target' column to df with integer-encoded classes
    derived from an existing column (target_column).

    Method adapted from:
    http://chrisstrelioff.ws/sandbox/2015/06/08/decision_trees_in_python_with_scikit_learn_and_pandas.html

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the target_column.
    target_column : str
        The name of the column to map to integer classes.

    Returns
    -------
    (df_mod, targets)
        df_mod is the modified DataFrame with a 'Target' column.
        targets is the list of unique target names in their mapped order.
    """
    df_mod = df.copy()
    unique_targets = pandas_utils.format_unique(df_mod[target_column].unique())
    map_to_int = {name: n for n, name in enumerate(unique_targets)}
    df_mod["Target"] = df_mod[target_column].map(map_to_int).astype("int64")
    return df_mod, unique_targets


# ----------------------------------------------------------------
#                          HELPERS
# ----------------------------------------------------------------

def _validate_inputs_for_decision_table(
        pre_decision_points, attributes, use_trace_attributes, trace_attributes
):
    """
    Internal function to validate the input parameters for get_decisions_table,
    giving more user-friendly error messages.
    """
    # Validate pre_decision_points
    if pre_decision_points is not None:
        if not isinstance(pre_decision_points, list):
            raise ValueError(
                "pre_decision_points must be a list of place names (strings)."
            )
        if len(pre_decision_points) == 0:
            raise ValueError(
                "The list pre_decision_points cannot be empty if provided."
            )

    # Validate attributes
    if attributes is not None:
        if not isinstance(attributes, list):
            raise ValueError(
                "attributes must be a list of event attribute names (strings)."
            )
        if len(attributes) == 0:
            raise ValueError(
                "The list attributes cannot be empty if provided."
            )

    # If trace attributes are provided, force use_trace_attributes=True
    if trace_attributes is not None:
        if not isinstance(trace_attributes, list):
            raise ValueError(
                "trace_attributes must be a list of trace attribute names (strings)."
            )
        if len(trace_attributes) == 0:
            raise ValueError(
                "The list trace_attributes cannot be empty if provided."
            )
        if not use_trace_attributes:
            # Warn user, then override
            print(
                "Note: 'trace_attributes' list given, but use_trace_attributes=False. "
                "Enabling use_trace_attributes=True."
            )


def _check_pre_decision_points(decision_points, pre_decision_points):
    """
    Checks which pre_decision_points are actually valid (places with >=2 outgoing arcs).
    Removes from 'decision_points' any place not in 'pre_decision_points',
    and warns if some user-specified place is not a decision point.
    """
    valid_count = 0
    to_remove = []
    for dp in list(decision_points.keys()):
        if dp not in pre_decision_points:
            to_remove.append(dp)
        else:
            valid_count += 1

    # Remove not requested places
    for dp in to_remove:
        del decision_points[dp]

    # Warn if none are valid
    if valid_count == 0:
        raise Exception("None of the given places is a decision point.")

    # Warn if some were invalid
    if valid_count < len(pre_decision_points):
        print(
            "Warning: Some of the places in pre_decision_points are not actual decision points "
            "in the Petri net. Only valid ones have been retained."
        )


def _build_decision_info(
        log,
        net,
        initial_marking,
        final_marking,
        decision_points,
        decision_points_names,
        attributes,
        use_trace_attributes,
        trace_attributes,
        k,
        parameters
):
    """
    Internal function to orchestrate the extraction of attributes that lead to particular transition choices.
    Returns a dictionary keyed by place name with a list of (attributes_dict, chosen_transition).
    """
    # Token replay or align each trace to find the sequences of transitions.
    # Then, for each place that has multiple outgoing arcs, store the attributes
    # that were present before the transition was fired.

    # We re-use get_attributes() because it contains the logic for
    # collecting attributes from the replay or alignments.
    return get_attributes(
        log=log,
        decision_points=decision_points,
        attributes=attributes,
        use_trace_attributes=use_trace_attributes,
        trace_attributes=trace_attributes,
        k=k,
        net=net,
        initial_marking=initial_marking,
        final_marking=final_marking,
        decision_points_names=decision_points_names,
        parameters=parameters,
    )


def _extract_decisions_perfect_fit(
    log,
    trace_indices,
    token_replay_entry,
    decision_info,
    decision_points,
    decision_points_names,
    attributes,
    use_trace_attributes,
    trace_attributes,
    k,
    labels
):
    """
    Extract decisions from a token replay entry with trace_fitness == 1.0 (perfect fit),
    ensuring that we only use attributes known BEFORE firing each transition.
    """
    for trace_index in trace_indices:
        # We'll keep a rolling window of the last k attributes
        window_attributes = [None] * k

        trace = log[trace_index]
        # If we use trace attributes, set them once for the entire trace
        global_attrs = {}
        if use_trace_attributes and trace_attributes:
            for attribute in trace_attributes:
                if attribute in trace.attributes:
                    global_attrs[attribute] = trace.attributes[attribute]

        # Pointer to the current event in the trace
        event_idx = 0

        # For each transition in the replay
        for transition in token_replay_entry["activated_transitions"]:
            # (1) Store decision with the current window (i.e., no new event has been consumed yet)
            transition_name_or_label = transition.label if labels else transition.name
            outgoing_choices = decision_points_names if labels else decision_points
            for place_name, outgoings in outgoing_choices.items():
                if transition_name_or_label in outgoings:
                    # We have a decision at place_name
                    for attr_dict in window_attributes:
                        if attr_dict is not None:
                            # Record the known attributes for the chosen transition
                            decision_info[place_name].append(
                                (attr_dict.copy(), transition_name_or_label)
                            )

            # (2) If this transition corresponds to a visible event (transition.label != None),
            #     then consume the *next* event from the log to update the window
            #     so that it is NOT used to decide the *current* transition.
            if transition.label is not None and event_idx < len(trace):
                # Merge global (trace) attributes + event attributes for the next event
                attr_dict = dict(global_attrs)
                for attr_name in attributes:
                    if attr_name in trace[event_idx]:
                        attr_dict[attr_name] = trace[event_idx][attr_name]

                # Put it in the rolling window
                window_attributes[event_idx % k] = attr_dict.copy()

                # Advance the pointer to the next event
                event_idx += 1


def _extract_decisions_alignment(
        log,
        trace_index,
        alignment_info,
        decision_info,
        decision_points,
        attributes,
        use_trace_attributes,
        trace_attributes,
        k,
        labels
):
    """
    Extract decisions for a single trace using alignment information.
    """
    # The alignment is a list of moves, each move is a tuple:
    # ((model_name, model_label), (log_name, log_label))
    alignment = alignment_info["alignment"]
    trace = log[trace_index]

    # Collect trace-level attributes if requested
    global_attrs = {}
    if use_trace_attributes and trace_attributes:
        for attribute in trace_attributes:
            if attribute in trace.attributes:
                global_attrs[attribute] = trace.attributes[attribute]

    # Prepare a rolling window for the last k attributes
    window_attributes = [None] * k

    # Pointer to the current event in this trace
    event_idx = 0

    for trans_names, trans_labels in alignment:
        # Unpack them for clarity
        log_name, model_name = trans_names
        log_label, model_label = trans_labels

        # CASE A: If model_name != '>>', we have a move in the *model* (either synchronous or model-only)
        if model_name != ">>":
            if labels:
                chosen_transition = model_label if model_label is not None else model_name
            else:
                chosen_transition = model_name

            # Now check if that chosen_transition is in some place's outgoing transitions
            # If your decision_points dict is keyed by place_name -> [labels],
            # then you see if chosen_transition is one of those labels
            for place_name, outgoings in decision_points.items():
                if model_name in outgoings:
                    # For each "window" item, store the decision
                    for attr_dict in window_attributes:
                        if attr_dict is not None:
                            # We append a tuple (attribute_dict, chosen_transition)
                            decision_info[place_name].append((attr_dict.copy(), chosen_transition))

        # CASE B: If log_name != '>>', we consumed an event from the log
        # => update the rolling window with that event's attributes
        if log_name != ">>" and event_idx < len(trace):
            combined_attrs = dict(global_attrs)
            event_attrs = trace[event_idx]

            # Copy only the specified attributes
            for attr_name in attributes:
                if attr_name in event_attrs:
                    combined_attrs[attr_name] = event_attrs[attr_name]

            # Insert into the rolling window
            window_attributes[event_idx % k] = combined_attrs
            event_idx += 1
