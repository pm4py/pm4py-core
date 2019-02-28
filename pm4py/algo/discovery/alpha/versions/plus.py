from pm4py.objects.log.log import EventLog, Trace
from pm4py.objects.log.util import xes as xes_util


import time

from pm4py import util as pmutil
from pm4py.objects import petri
from pm4py.objects.petri.petrinet import Marking

def preprocessing(log, parameters=None):
    """
    Preprocessing step for the Aplha+ algorithm. Removing all transitions from the log with a loop of length one.
    :param log:
    :param parameters:
    :return: the filtered log and a list of the filtered transitions
    """
    loops_in_first_place = set()
    loops_in_last_place = set()

    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    # List for values that have a loop of length one
    loop_one_list = []
    #Log without activities that have a loop of length one
    filtered_log = EventLog()
    #dictionary A: activity before the loop-length-one activity
    A = {}
    # dictionary B: activity after the loop-length-one activity
    B = {}
    A_filtered = {}
    B_filtered = {}
    #inserting artificial start and end activity, since it is not allowed to have a loop at the source place (according to paper)
    for trace in log:
        trace.insert(0, {activity_key:'artificial_start'})
        trace.append({activity_key:'artificial_end'})
    for trace in log:
        i = 0
        while i < len(trace)-1:
            test=trace[1]
            current = trace[i][activity_key]
            successor = trace[i + 1][activity_key]
            if current == successor:
                if current not in loop_one_list:
                    loop_one_list.append(current)
            i+=1
    for trace in log:
        i = 0
        filtered_trace = Trace()
        while i < len(trace)-1:
            current = trace[i][activity_key]
            successor = trace[i + 1][activity_key]
            if not current in loop_one_list:
                filtered_trace.append(current)
            if successor in loop_one_list:
                if not current in loop_one_list:
                    if current in A:
                        A[successor].append(current)
                    else:
                        A[successor] = [current]
            if current in loop_one_list:
                if not successor in loop_one_list:
                    if current in B:
                        B[current].append(successor)
                    else:
                        B[current] = [successor]
            if i==len(trace)-2:
                if not successor in loop_one_list:
                    filtered_trace.append(successor)
            i+=1
        filtered_log.append(filtered_trace)
    #Making sets instead of lists
    for key, value in A.items():
        A_filtered[key]=set(value)
    # Making sets instead of lists
    for key, value in B.items():
        B_filtered[key] = set(value)
    for trace in log:
        if trace.__getitem__(0) in loop_one_list:
            loops_in_first_place.add(trace.__getitem__(0))
        if trace.__getitem__(len(trace) - 1) in loop_one_list:
            loops_in_last_place.add(trace.__getitem__(len(trace) - 1))
    loops_in_first_place = list(loops_in_first_place)
    loops_in_last_place = list(loops_in_last_place)

    return (filtered_log, loop_one_list, A_filtered, B_filtered, loops_in_first_place, loops_in_last_place)

def get_relations(log, parameters=None):
    """
    Applying the classic Alpha Algorithm
    :param log: Filtered log
    :param parameters:
    :return:
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    #finding loops of length two
    #ordering relations
    triangle = {}
    for trace in log:
        i = 0
        while i < len(trace) - 2:
            current = trace.__getitem__(i)
            successor = trace.__getitem__(i+1)
            successor2 = trace.__getitem__(i+2)
            if current == successor2:
                if current in triangle:
                    triangle[current].append(successor)
                else:
                    triangle[current] = [successor]
            i+=1
    for key, value in triangle.items():
        triangle[key] = set(value)
    square = {}
    for key in triangle:
        for element in triangle[key]:
            if element in triangle:
                if key in triangle[element]:
                    if key in square:
                        square[key].append(element)
                        square[element].append(key)
                    else:
                        square[key] = [element]
                        square[element]=[key]
    for key, value in square.items():
        square[key]=set(value)
    #ordering relation following
    follows = {}
    for trace in log:
        i = 0
        while i < len(trace)-1:
            current = trace.__getitem__(i)
            successor = trace.__getitem__(i+1)
            if current in follows:
                if successor not in follows[current]:
                    follows[current].append(successor)
            else:
                follows[current] = [successor]
            i+=1
    #transforming list to set
    for key, value in follows.items():
        follows[key]=set(value)
    # ordering relation causal
    causal = {}
    if len(square) != 0:
        for key in follows:
            for element in follows[key]:
                if element in follows:
                    if key in square:
                        if (not(key in follows[element])) or (element in square[key]):
                            if key in causal:
                                causal[key].append(element)
                            else:
                                causal[key]= [element]
                    else:
                        if (not(key in follows[element])):
                            if key in causal:
                                causal[key].append(element)
                            else:
                                causal[key]= [element]
                else:
                    if key in causal:
                        causal[key].append(element)
                    else:
                        causal[key]= [element]
    else:
        for key in follows:
            for element in follows[key]:
                if element in follows:
                    if (not (key in follows[element])):
                        if key in causal:
                            causal[key].append(element)
                        else:
                            causal[key] = [element]
                else:
                    if key in causal:
                        causal[key].append(element)
                    else:
                        causal[key] = [element]

    for key, value in causal.items():
        causal[key]=set(value)
    # ordering relation unrelated if no other ordering is applied
    #ordering relation parallel
    parallel = {}
    if len(square) != 0:
        for key in follows:
            for element in follows[key]:
                if element in follows:
                    if key in follows[element]:
                        if element in follows[key]:
                            if key in square:
                                if not element in square[key]:
                                    if key in parallel:
                                        parallel[key].append(element)
                                    else:
                                        parallel[key] = [element]
                            else:
                                if key in parallel:
                                    parallel[key].append(element)
                                else:
                                    parallel[key] = [element]

    else:
        for key in follows:
            for element in follows[key]:
                if element in follows:
                    if key in follows[element]:
                        if element in follows[key]:
                            if key in parallel:
                                parallel[key].append(element)
                            else:
                                parallel[key] = [element]

    for key, value in parallel.items():
        parallel[key] = set(value)
    return causal, parallel, follows

def processing(log, causal, follows, parameters=None):
    """
    Applying the Alpha Miner with the new relations
    :param log: Filtered log, i.e. without loops of length one
    :param causal: Pairs that have a causal relation (->)
    :param follows: Pairs that have a follow relation (>)
    :return:
    """
    #create list of all events
    labels = set()
    start_activities = set()
    end_activities = set()
    for trace in log:
        start_activities.add(trace.__getitem__(0))
        end_activities.add(trace.__getitem__(len(trace)-1))
        for events in trace:
            labels.add(events)
    labels = list(labels)
    pairs = []


    for key, element in causal.items():
        for item in element:
            if get_sharp_relation(follows, key, key):
                if get_sharp_relation(follows, item, item):
                    pairs.append(({key},{item}))


    #combining pairs
    for i in range(0, len(pairs)):
        t1 = pairs[i]
        for j in range(i, len(pairs)):
            t2 = pairs[j]
            if t1 != t2:
                if t1[0].issubset(t2[0]) or t1[1].issubset(t2[1]):
                    if get_sharp_relations_for_sets(follows, t1[0], t2[0]) and get_sharp_relations_for_sets(follows, t1[1], t2[1]):
                        new_alpha_pair = (t1[0] | t2[0], t1[1] | t2[1])
                        if new_alpha_pair not in pairs:
                            pairs.append((t1[0] | t2[0], t1[1] | t2[1]))
    #maximize pairs
    cleaned_pairs = list(filter(lambda p: __pair_maximizer(pairs, p), pairs))
    #create transitions
    net = petri.petrinet.PetriNet('alpha_plus_net_' + str(time.time()))
    label_transition_dict = {}
    for label in labels:
        if label is not 'artificial_start' and label is not 'artificial_end':
            label_transition_dict[label] = petri.petrinet.PetriNet.Transition(label, label)
            net.transitions.add(label_transition_dict[label])
        else:
            label_transition_dict[label] = petri.petrinet.PetriNet.Transition(label, None)
            net.transitions.add(label_transition_dict[label])
    #and source and sink
    src = add_source(net, start_activities, label_transition_dict)
    sink = add_sink(net, end_activities, label_transition_dict)
    #create places
    for pair in cleaned_pairs:
        place = petri.petrinet.PetriNet.Place(str(pair))
        net.places.add(place)
        for in_arc in pair[0]:
            petri.utils.add_arc_from_to(label_transition_dict[in_arc], place, net)
        for out_arc in pair[1]:
            petri.utils.add_arc_from_to(place, label_transition_dict[out_arc], net)


    return  net, Marking({src: 1}), Marking({sink: 1}), cleaned_pairs

def get_sharp_relation(follows, instance_one, instance_two):
    """
    Returns true if sharp relations holds
    :param follows:
    :param instance_one:
    :param instance_two:
    :return: bool
    """
    if instance_one in follows:
        if instance_two in follows:
            if not instance_two in follows[instance_one] and not instance_one in follows[instance_two]:
                return True
    if not instance_one in follows and not instance_two in follows:
        return True
    if instance_one in follows:
        if instance_two in follows[instance_one]:
            return False
    if instance_two in follows:
        if instance_one in follows[instance_two]:
            return False

def get_sharp_relations_for_sets(follows, set_1, set_2):
    for item_1 in set_1:
        for item_2 in set_2:
            if not get_sharp_relation(follows, item_1, item_2):
                return False
    return True

def postprocessing(net, initial_marking, final_marking, A, B ,pairs, parameters=None):
    """
    Adding the filtered transition to the petri net
    :param loop_list: List of looped activities
    :param classical_alpha_result: Result after applying the classic alpha algorithm to the filtered log
    :param A: See Paper for definition
    :param B: See Paper for definition
    :param parameters:
    :return: Alpha+ result
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    #F L1L
    #Key is specific loop element
    for key, value in A.items():
        if key in B:
            A_without_B = value-B[key]
            B_without_A = B[key]-value
            pair = (A_without_B, B_without_A)
            for pair_try in pairs:
                in_part = pair_try[0]
                out_part = pair_try[1]
                if pair[0].issubset(in_part) and pair[1].issubset(out_part):
                    pair_try_place = petri.petrinet.PetriNet.Place(str(pair_try))
                    petri.utils.add_arc_from_to(petri.petrinet.PetriNet.Transition(key, key), pair_try_place, net)
                    petri.utils.add_arc_from_to(pair_try_place, petri.petrinet.PetriNet.Transition(key, key), net)
    return net,initial_marking, final_marking

def apply(trace_log, parameters=None):
    """
    Apply the Alpha Algorithm to a given log
    :param trace_log: Log to that the algorithm will apply
    :param parameters:
    :return: Net and corresponding source and sink markings
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]


    filtered_log, loop_one_list, A_filtered, B_filtered, loops_in_first, loops_in_last = preprocessing(trace_log)
    causal, parallel, follows = get_relations(filtered_log)
    net, initial_marking, final_marking, pairs = processing(filtered_log, causal, follows)
    net, initial_marking, final_marking = postprocessing(net, initial_marking, final_marking, A_filtered, B_filtered, pairs)
    return net, initial_marking, final_marking



#Helping methods
#maximizing pairs
def __pair_maximizer(alpha_pairs, pair):
    for alt in alpha_pairs:
        if pair != alt and pair[0].issubset(alt[0]) and pair[1].issubset(alt[1]):
            return False
    return True

#adding source pe
def add_source(net, start_activities, label_transition_dict):
    source = petri.petrinet.PetriNet.Place('start')
    net.places.add(source)
    for s in start_activities:
        petri.utils.add_arc_from_to(source, label_transition_dict[s], net)
    return source


def add_sink(net, end_activities, label_transition_dict):
    end = petri.petrinet.PetriNet.Place('end')
    net.places.add(end)
    for e in end_activities:
        petri.utils.add_arc_from_to(label_transition_dict[e], end, net)
    return end