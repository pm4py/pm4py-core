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
import sys
from copy import deepcopy, copy
from enum import Enum
from typing import Optional, Dict, Any, Union, Tuple
import numpy as np

from pm4py.algo.conformance.alignments.petri_net import algorithm as ali
from pm4py.algo.conformance.alignments.petri_net.variants import state_equation_a_star as star
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.obj import EventLog
from pm4py.objects.petri_net import properties as petri_properties
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.statistics.attributes.log.select import select_attributes_from_log_for_tree
from pm4py.statistics.variants.log import get as variants_module
from pm4py.util import constants, xes_constants
from pm4py.util import exec_utils, pandas_utils
from pm4py.visualization.decisiontree.util import dt_to_string
import pandas as pd


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    LABELS = "labels"


def create_data_petri_nets_with_decisions(log: Union[EventLog, pd.DataFrame], net: PetriNet, initial_marking: Marking,
                                          final_marking: Marking) -> Tuple[PetriNet, Marking, Marking]:
    """
    Given a Petri net, create a data Petri net with the decisions given for each place by the decision
    mining algorithm

    Parameters
    ----------------
    log
        Event log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking

    Returns
    ------------------
    data_petri_net
        Data petri net
    initial_marking
        Initial marking (unchanged)
    final_marking
        Final marking (unchanged)
    """
    all_conditions = {}
    all_variables = {}
    for place in net.places:
        try:
            clf, columns, targets = get_decision_tree(log, net, initial_marking, final_marking,
                                                      decision_point=place.name,
                                                      parameters={"labels": False})
            target_classes, variables = dt_to_string.apply(clf, columns)
            target_classes = {targets[int(k)]: v for k, v in target_classes.items()}
            variables = {targets[int(k)]: v for k, v in variables.items()}
            for k in target_classes.keys():
                all_conditions[k] = target_classes[k]
                all_variables[k] = variables[k]
        except:
            pass
    for trans in net.transitions:
        if trans.name in all_conditions:
            trans.properties[petri_properties.TRANS_GUARD] = all_conditions[trans.name]
            trans.properties[petri_properties.READ_VARIABLE] = all_variables[trans.name]
            trans.properties[petri_properties.WRITE_VARIABLE] = []
    return net, initial_marking, final_marking


def get_decision_tree(log: Union[EventLog, pd.DataFrame], net: PetriNet, initial_marking: Marking, final_marking: Marking,
                      decision_point=None, attributes=None,
                      parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Any:
    """
    Gets a decision tree classifier on a specific point of the model

    Parameters
    --------------
    log
        Event log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    decision_point
        Point of the process in which a decision happens:
        - if not specified, the method crashes, but provides a list of possible decision points
        - if specified, the method goes on and produce the decision tree
    attributes
        Attributes of the log. If not specified, then an automatic attribute selection
        is performed.
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    clf
        Decision tree
    feature_names
        The names of the features
    classes
        The classes
    """
    from pm4py.util import ml_utils

    if parameters is None:
        parameters = {}

    X, y, targets = apply(log, net, initial_marking, final_marking, decision_point=decision_point,
                          attributes=attributes, parameters=parameters)

    dt = ml_utils.DecisionTreeClassifier()
    dt = dt.fit(X, y)
    return dt, list(X.columns.values.tolist()), targets


def apply(log: Union[EventLog, pd.DataFrame], net: PetriNet, initial_marking: Marking, final_marking: Marking, decision_point=None,
          attributes=None, parameters: Optional[Dict[Union[str, Parameters], Any]] = None) -> Any:
    """
    Gets the essential information (features, target class and names of the target class)
    in order to learn a classifier

    Parameters
    --------------
    log
        Event log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    decision_point
        Point of the process in which a decision happens:
        - if not specified, the method crashes, but provides a list of possible decision points
        - if specified, the method goes on and produce the decision tree
    attributes
        Attributes of the log. If not specified, then an automatic attribute selection
        is performed.
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    X
        features
    y
        Target class
    class_name
        Target class names
    """
    import pandas as pd

    if parameters is None:
        parameters = {}

    labels = exec_utils.get_param_value(Parameters.LABELS, parameters, True)

    activity_key = exec_utils.get_param_value(Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY)
    if decision_point is None:
        decision_points_names = get_decision_points(net, labels=labels, parameters=parameters)
        raise Exception("please provide decision_point as argument of the method. Possible decision points: ",
                        decision_points_names)
    if attributes is None:
        str_tr_attr, str_ev_attr, num_tr_attr, num_ev_attr = select_attributes_from_log_for_tree(log)
        attributes = list(str_ev_attr) + list(num_ev_attr)
    I, dp = get_decisions_table(log, net, initial_marking, final_marking, attributes=attributes,
                                pre_decision_points=[decision_point], parameters=parameters)
    x_attributes = [a for a in attributes if not a == activity_key]
    str_attributes = set()
    non_str_attributes = set()
    x = []
    x2 = []
    y = []
    for el in I[decision_point]:
        for a, v in el[0].items():
            if a in x_attributes:
                if type(v) is str:
                    str_attributes.add(a)
                else:
                    non_str_attributes.add(a)
        x.append({a: v for a, v in el[0].items() if a in x_attributes and type(v) is str})
        x2.append({a: v for a, v in el[0].items() if a in x_attributes and type(v) is not str})
        y.append(el[1])
    X = pandas_utils.instantiate_dataframe(x)
    X = pd.get_dummies(data=X, columns=list(str_attributes))
    X2 = pandas_utils.instantiate_dataframe(x2)
    X = pandas_utils.concat([X, X2], axis=1)
    Y = pandas_utils.instantiate_dataframe(y, columns=["Name"])
    Y, targets = encode_target(Y, "Name")
    y = Y['Target']
    return X, y, targets


def get_decisions_table(log0, net, initial_marking, final_marking, attributes=None, use_trace_attributes=False, k=1,
                        pre_decision_points=None, trace_attributes=None, parameters=None):
    """
    Gets a decision table out of a log and an accepting Petri net

    Parameters
    -----------------
    log0
        Event log
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    attributes
        List of attributes which are considered
        (if not provided, all the attributes are considered)
    use_trace_attributes
        Include trace attributes in the decision table
    k
        Number that determines the number of last activities to take into account
    pre_decision_points
        List of Strings of place Names that have to be considered as decision points.
        If not provided, the decision points are inferred from the Petri net
    trace_attributes
        List of trace attributes to consider
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    I
        decision table
    decision_points
        The decision points as places of the Petri net, which are the keys of a dictionary
        having as values the list of transitions that are target
    """
    if parameters is None:
        parameters = {}

    labels = exec_utils.get_param_value(Parameters.LABELS, parameters, True)

    log = deepcopy(log0)
    log = log_converter.apply(log, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

    if pre_decision_points != None:
        if not isinstance(pre_decision_points, list):
            print(
                "Error: The parameter pre_decision_points has to be a list of names of the places that have to be considered.")
            sys.exit()
        if len(pre_decision_points) == 0:
            print("Error: There must be at least one element in the list of pre_decision_points.")
            sys.exit()
    if attributes != None:
        if not isinstance(attributes, list):
            print(
                "Error: The parameter attributes has to be a list of names of event attributes that have to be considered.")
            sys.exit()
        if len(attributes) == 0:
            print("Error: There must be at least one element in the list of attributes.")
            sys.exit()
    if use_trace_attributes == False and trace_attributes != None and isinstance(trace_attributes, list):
        print(
            "Note: Since a list of considerable trace attributes is provided, and use_trace_attributes was set on False, we set it on True")
        use_trace_attributes = True
    if trace_attributes != None:
        if not isinstance(trace_attributes, list):
            print(
                "Error: The parameter trace_attributes has to be a list of names of trace attributes that have to be considered.")
            sys.exit()
        if len(trace_attributes) == 0:
            print("Error: There must be at least one element in the list of trace_attributes.")
            sys.exit()

    # alignment = ali.apply(log, net, initial_marking, final_marking, variant=True, parameters={star.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE:True})
    decision_points = get_decision_points(net, pre_decision_points=pre_decision_points, parameters=parameters)
    decision_points_names = get_decision_points(net, labels=labels, pre_decision_points=pre_decision_points,
                                                parameters=parameters)
    if use_trace_attributes:
        # Made to ensure distinguishness between event and trace attributes.
        log = prepare_event_log(log)
        if attributes != None:
            attributes = prepare_attributes(attributes)

    if use_trace_attributes and trace_attributes == None:
        # if no list of trace attributes is provided, we create one
        trace_attributes = []
        if use_trace_attributes:
            for trace in log:
                trace_attributes += list(trace.attributes)
        trace_attributes = list(set(trace_attributes))
    if attributes == None:
        # if no list is given, every attribute of the events are considered
        attributes = []
        for trace in log:
            for event in trace:
                attributes += list(event.keys())
    attributes = list(set(attributes))
    I = get_attributes(log, decision_points,
                       attributes, use_trace_attributes, trace_attributes,
                       k, net, initial_marking, final_marking, decision_points_names, parameters=parameters)
    return (I, decision_points)


def prepare_event_log(log):
    """
    If trace attributes are considered, it is possible that trace attributes have the same name as event attributes.
    To tackle this issue, the attributes get renamed.
    For trace attributes, we add "t_" at the beginning of the dictionary keys.
    For event attributes, we add "e_" at the beginning of the dict keys.
    :param log:
    :return:
    """
    for trace in log:
        attributes = trace.attributes.copy()
        for attribute in attributes:
            trace.attributes["t_" + attribute] = trace.attributes.pop(attribute)
        for event in trace:
            attributes = event._dict.copy()
            for attribute in attributes:
                event._dict["e_" + attribute] = event._dict.pop(attribute)
    return log


def prepare_attributes(attributes):
    """
    Method that "e_" in front of every attribute if trace attributes are considered.
    :param attributes: List of event attributes that the user wants to consider.
    :return: list of edited attribute names
    """
    new_attributes = []
    for attribute in attributes:
        new_attributes.append("e_" + attribute)
    return new_attributes


def get_decision_points(net, labels=False, pre_decision_points=None, parameters=None):
    """
    The goal is to get all decision places. These are places where there are at least two outgoing arcs.
    :param net: Petri Net where decision points are discovered (places with at least two outgoing arcs)
    :param labels: If someone wants to get the labels of the transitions after a decision point and not the "ID"
    :return:
    """
    if parameters is None:
        parameters = {}
    counter = {}
    for place in net.places:
        counter[place.name] = []
    for arc in net.arcs:
        if arc.source in net.places:
            if labels == True:
                counter[arc.source.name].append(arc.target.label)
            else:
                counter[arc.source.name].append(arc.target.name)
    decision_points = {key: val for key, val in counter.items() if len(val) >= 2}
    i = 0
    # i counts how many given decision points of the user are detected
    if pre_decision_points != None:
        for el in list(decision_points):
            if el in pre_decision_points:
                i += 1
            else:
                del decision_points[el]
        if i == len(pre_decision_points):
            # print("All given decision points were identified as decision points in the Petri Net.")
            pass
        elif i == 0:
            raise Exception("None of the given points is a decision point.")
            # sys.exit()
        else:
            print(
                "Not all of the given places were identified as decision points. However, we only take the correct decision points from your list into account.")
    return decision_points


def simplify_token_replay(replay):
    variant = {}
    for element in replay:
        if tuple(element['activated_transitions']) not in variant:
            variant[tuple(element['activated_transitions'])] = True
    smaller_replay = []
    for element in replay:
        if variant[tuple(element['activated_transitions'])]:
            smaller_replay.append(element)
            variant[tuple(element['activated_transitions'])] = False
    return smaller_replay


def get_attributes(log, decision_points, attributes, use_trace_attributes, trace_attributes, k, net, initial_marking,
                   final_marking, decision_points_names, parameters=None):
    """
    This method aims to construct for each decision place a table where for each decision place a list if given with the
     label of the later decision and as value the given attributes
    :param log: Log on which the method is applied
    :param alignments: Computed alignments for a log and a model
    :param decision_points: Places that have multiple outgoing arcs
    :param attributes: Attributes that are considered
    :param use_trace_attributes: If trace attributes have to be considered or not
    :param trace_attributes: List of trace attributes that are considered
    :param k: Taking k last activities into account
    :return: Dictionary that has as keys the decision places. The value for this key is a list.
    The content of these lists are tuples. The first element of these tuples is information regrading the attributes,
    the second element of these tuples is the transition which chosen in a decision.
    """
    if parameters is None:
        parameters = {}
    labels = exec_utils.get_param_value(Parameters.LABELS, parameters, True)

    I = {}
    for key in decision_points:
        I[key] = []
    A = {}
    for attri in attributes:
        A[attri] = None
    i = 0
    # first, take a look at the variants
    variants_idxs = variants_module.get_variants_from_log_trace_idx(log, parameters=parameters)
    one_variant = []
    for variant in variants_idxs:
        one_variant.append(variant)
        # TODO: Token based replay code mit paramter für nur varianten einbeziehen ausstatten
    replay_result = token_replay.apply(log, net, initial_marking, final_marking, parameters=parameters)
    replay_result = simplify_token_replay(replay_result)
    count = 0
    for variant in replay_result:
        if variant['trace_fitness'] == 1.0:
            for trace_index in variants_idxs[one_variant[count]]:
                last_k_list = [None] * k
                trace = log[trace_index]
                if use_trace_attributes:
                    for attribute in trace_attributes:
                        # can be done here since trace attributes does not change for whole trace
                        A[attribute] = trace.attributes[attribute]
                j = 0
                # j is a pointer which points to the current event inside a trace
                for transition in variant['activated_transitions']:
                    for key, value in decision_points_names.items():
                        tr_to_str = transition.label if labels else transition.name
                        if tr_to_str in value:
                            for element in last_k_list:
                                if element != None:
                                    I[key].append((element.copy(), tr_to_str))
                    for attri in attributes:
                        # print(variant, transition.label, j)
                        if attri in trace[j]:
                            # only add the attribute information if it is present in the event
                            A[attri] = trace[j][attri]
                    # add A to last_k_list. Using modulo to access correct entry
                    last_k_list[j % k] = A.copy()
                    if transition.label != None:
                        if not j + 1 >= len(trace):
                            # Problem otherwise: If there are tau-transition after the last event related transition,
                            # the pointer j which points to the current event in a trace, gets out of range
                            j += 1
        else:
            example_trace = log[variants_idxs[one_variant[count]][0]]
            align_parameters = copy(parameters)
            align_parameters[star.Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE] = True
            alignment = ali.apply(example_trace, net, initial_marking, final_marking,
                                  parameters=align_parameters)['alignment']
            for trace_index in variants_idxs[one_variant[count]]:
                last_k_list = [None] * k
                trace = log[trace_index]
                if use_trace_attributes:
                    for attribute in trace_attributes:
                        # can be done here since trace attributes does not change for whole trace
                        A[attribute] = trace.attributes[attribute]
                j = 0
                for el in alignment:
                    if el[1][1] != '>>':
                        # If move in model
                        for key, value in decision_points.items():
                            if el[0][1] in value:
                                for element in last_k_list:
                                    if element != None:
                                        # only add those entries where information is provided
                                        if el[1][1] == None:
                                            # for some dt algorithms, the entry None might be a problem, since it is left out later
                                            I[key].append((element.copy(), el[0][1]))
                                        else:
                                            I[key].append((element.copy(), el[1][1]))
                    if el[1][0] != '>>' and el[1][1] != '>>':
                        # If there is a move in log and model
                        for attri in attributes:
                            if attri in trace[j]:
                                # only add the attribute information if it is present in the event
                                A[attri] = trace[j][attri]
                        # add A to last_k_list. Using modulo to access correct entry
                        last_k_list[j % k] = A.copy()
                    if el[1][0] != '>>':
                        # only go to next event in trace if the current event has been aligned
                        # TODO: Discuss if this is correct or can lead to problems
                        j += 1
        count += 1
    return I


def encode_target(df, target_column):
    """Add column to df with integers for the target.
    Method taken from: http://chrisstrelioff.ws/sandbox/2015/06/08/decision_trees_in_python_with_scikit_learn_and_pandas.html
    Args
    ----
    df -- pandas DataFrame.
    target_column -- column to map to int, producing
                     new Target column.

    Returns
    -------
    df_mod -- modified DataFrame.
    targets -- list of target names.
    """
    df_mod = df.copy()
    targets = pandas_utils.format_unique(df_mod[target_column].unique())
    map_to_int = {name: n for n, name in enumerate(targets)}
    df_mod["Target"] = df_mod[target_column].replace(map_to_int)

    return (df_mod, targets)
