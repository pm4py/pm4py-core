from pm4py import util as pmutil
from pm4py.objects import log as log_lib
from pm4py.evaluation.precision import utils as precision_utils
from pm4py.objects import petri
from pm4py.objects.petri import align_utils as utils
from pm4py.statistics.start_activities.log.get import get_start_activities
from pm4py.objects.petri.align_utils import get_visible_transitions_eventually_enabled_by_marking

PARAM_ACTIVITY_KEY = pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY

PARAMETERS = [PARAM_ACTIVITY_KEY]


def apply(log, net, marking, final_marking, parameters=None):
    """
    Get Align-ET Conformance precision

    Parameters
    ----------
    log
        Trace log
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key
    """

    if parameters is None:
        parameters = {}

    debug_level = parameters["debug_level"] if "debug_level" in parameters else 0

    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY
    # default value for precision, when no activated transitions (not even by looking at the initial marking) are found
    precision = 1.0
    sum_ee = 0
    sum_at = 0
    unfit = 0

    if not petri.check_soundness.check_relaxed_soundness_net_in_fin_marking(net, marking, final_marking):
        raise Exception("trying to apply Align-ETConformance on a Petri net that is not a relaxed sound net!!")

    prefixes, prefix_count = precision_utils.get_log_prefixes(log, activity_key=activity_key)
    prefixes_keys = list(prefixes.keys())
    fake_log = precision_utils.form_fake_log(prefixes_keys, activity_key=activity_key)

    align_stop_marking = align_fake_log_stop_marking(fake_log, net, marking, final_marking, parameters=parameters)
    all_markings = transform_markings_from_sync_to_original_net(align_stop_marking, net, parameters=parameters)

    for i in range(len(prefixes)):
        markings = all_markings[i]

        if markings is not None:
            log_transitions = set(prefixes[prefixes_keys[i]])
            activated_transitions_labels = set()
            for m in markings:
                # add to the set of activated transitions in the model the activated transitions
                # for each prefix
                activated_transitions_labels = activated_transitions_labels.union(
                    x.label for x in utils.get_visible_transitions_eventually_enabled_by_marking(net, m) if
                    x.label is not None)
            escaping_edges = activated_transitions_labels.difference(log_transitions)

            sum_at += len(activated_transitions_labels) * prefix_count[prefixes_keys[i]]
            sum_ee += len(escaping_edges) * prefix_count[prefixes_keys[i]]

            if debug_level > 1:
                print("")
                print("prefix=", prefixes_keys[i])
                print("log_transitions=", log_transitions)
                print("activated_transitions=", activated_transitions_labels)
                print("escaping_edges=", escaping_edges)
        else:
            unfit += prefix_count[prefixes_keys[i]]

    if debug_level > 0:
        print("\n")
        print("overall unfit", unfit)
        print("overall activated transitions", sum_at)
        print("overall escaping edges", sum_ee)

    # fix: also the empty prefix should be counted!
    start_activities = set(get_start_activities(log, parameters=parameters))
    trans_en_ini_marking = set([x.label for x in get_visible_transitions_eventually_enabled_by_marking(net, marking)])
    diff = trans_en_ini_marking.difference(start_activities)
    sum_at += len(log) * len(trans_en_ini_marking)
    sum_ee += len(log) * len(diff)
    # end fix

    if sum_at > 0:
        precision = 1 - float(sum_ee) / float(sum_at)

    return precision


def transform_markings_from_sync_to_original_net(markings0, net, parameters=None):
    """
    Transform the markings of the sync net (in which alignment stops) into markings of the original net
    (in order to measure the precision)

    Parameters
    -------------
    markings0
        Markings on the sync net (expressed as place name with count)
    net
        Petri net
    parameters
        Parameters of the Petri net

    Returns
    -------------
    markings
        Markings of the original model (expressed as place with count)
    """
    if parameters is None:
        parameters = {}

    places_corr = {p.name: p for p in net.places}

    markings = []

    for i in range(len(markings0)):
        res_list = markings0[i]

        # res_list shall be a list of markings.
        # If it is None, then there is no correspondence markings
        # in the original Petri net
        if res_list is not None:
            # saves all the markings reached by the optimal alignment
            # as markings of the original net
            markings.append([])

            for j in range(len(res_list)):
                res = res_list[j]

                atm = petri.petrinet.Marking()
                for pl, count in res.items():
                    if pl[0] == utils.SKIP:
                        atm[places_corr[pl[1]]] = count
                markings[-1].append(atm)
        else:
            markings.append(None)

    return markings


def align_fake_log_stop_marking(fake_log, net, marking, final_marking, parameters=None):
    """
    Align the 'fake' log with all the prefixes in order to get the markings in which
    the alignment stops

    Parameters
    -------------
    fake_log
        Fake log
    net
        Petri net
    marking
        Marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm

    Returns
    -------------
    alignment
        For each trace in the log, return the marking in which the alignment stops (expressed as place name with count)
    """
    if parameters is None:
        parameters = {}
    align_result = []
    for i in range(len(fake_log)):
        trace = fake_log[i]
        sync_net, sync_initial_marking, sync_final_marking = build_sync_net(trace, net, marking, final_marking,
                                                                            parameters=parameters)
        stop_marking = petri.petrinet.Marking()
        for pl, count in sync_final_marking.items():
            if pl.name[1] == utils.SKIP:
                stop_marking[pl] = count
        cost_function = utils.construct_standard_cost_function(sync_net, utils.SKIP)

        # perform the alignment of the prefix
        res = precision_utils.__search(sync_net, sync_initial_marking, sync_final_marking, stop_marking, cost_function,
                                       utils.SKIP)

        if res is not None:
            align_result.append([])
            for mark in res:
                res2 = {}
                for pl in mark:
                    # transforms the markings for easier correspondence at the end
                    # (distributed engine friendly!)
                    res2[(pl.name[0], pl.name[1])] = mark[pl]

                align_result[-1].append(res2)
        else:
            # if there is no path from the initial marking
            # replaying the given prefix, then add None
            align_result.append(None)

    return align_result


def build_sync_net(trace, petri_net, initial_marking, final_marking, parameters=None):
    """
    Build the sync product net between the Petri net and the trace prefix

    Parameters
    ---------------
    trace
        Trace prefix
    petri_net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    parameters
        Possible parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        PARAM_ACTIVITY_KEY] if PARAM_ACTIVITY_KEY in parameters else log_lib.util.xes.DEFAULT_NAME_KEY

    trace_net, trace_im, trace_fm = petri.utils.construct_trace_net(trace, activity_key=activity_key)

    sync_prod, sync_initial_marking, sync_final_marking = petri.synchronous_product.construct(trace_net, trace_im,
                                                                                              trace_fm, petri_net,
                                                                                              initial_marking,
                                                                                              final_marking,
                                                                                              utils.SKIP)

    return sync_prod, sync_initial_marking, sync_final_marking
