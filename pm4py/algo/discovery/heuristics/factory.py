from pm4py.algo.discovery.heuristics.versions import classic
import pandas
from pm4py.objects.conversion.log import factory as conv_factory


CLASSIC = "classic"

VERSIONS = {CLASSIC: classic.apply}
VERSIONS_PANDAS = {CLASSIC: classic.apply_pandas}
VERSIONS_DFG = {CLASSIC: classic.apply_dfg}
VERSIONS_HEU = {CLASSIC: classic.apply_heu}
VERSIONS_DFG_HEU = {CLASSIC: classic.apply_heu_dfg}


def apply(log, parameters=None, variant=CLASSIC):
    """
    Discovers a Petri net using Heuristics Miner

    Parameters
    ------------
    log
        Event log
    parameters
        Possible parameters of the algorithm,
        including: activity_key, case_id_glue, timestamp_key,
        dependency_thresh, and_measure_thresh, min_act_count, min_dfg_occurrences, dfg_pre_cleaning_noise_thresh,
        loops_length_two_thresh
    variant
        Variant of the algorithm (classic)

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if isinstance(log, pandas.core.frame.DataFrame):
        return VERSIONS_PANDAS[variant](log, parameters=parameters)

    return VERSIONS[variant](conv_factory.apply(log, parameters=parameters), parameters=parameters)


def apply_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
              parameters=None, variant=CLASSIC):
    """
    Discovers a Petri net using Heuristics Miner

    Parameters
    ------------
    dfg
        Directly-Follows Graph
    activities
        (If provided) list of activities of the log
    activities_occurrences
        (If provided) dictionary of activities occurrences
    start_activities
        (If provided) dictionary of start activities occurrences
    end_activities
        (If provided) dictionary of end activities occurrences
    parameters
        Possible parameters of the algorithm,
        including: activity_key, case_id_glue, timestamp_key,
        dependency_thresh, and_measure_thresh, min_act_count, min_dfg_occurrences, dfg_pre_cleaning_noise_thresh,
        loops_length_two_thresh
    variant
        Variant of the algorithm (classic)

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    return VERSIONS_DFG[variant](dfg, activities=activities, activities_occurrences=activities_occurrences,
                                 start_activities=start_activities, end_activities=end_activities,
                                 parameters=parameters)


def apply_heu(log, parameters=None, variant=CLASSIC):
    """
    Discovers an Heuristics Net using Heuristics Miner

    Parameters
    ------------
    log
        Event log
    parameters
        Possible parameters of the algorithm,
        including: activity_key, case_id_glue, timestamp_key,
        dependency_thresh, and_measure_thresh, min_act_count, min_dfg_occurrences, dfg_pre_cleaning_noise_thresh,
        loops_length_two_thresh
    variant
        Variant of the algorithm (classic)

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    return VERSIONS_HEU[variant](log, parameters=parameters)


def apply_heu_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
                  parameters=None, variant=CLASSIC):
    """
    Discovers an Heuristics Net using Heuristics Miner

    Parameters
    ------------
    dfg
        Directly-Follows Graph
    activities
        (If provided) list of activities of the log
    activities_occurrences
        (If provided) dictionary of activities occurrences
    start_activities
        (If provided) dictionary of start activities occurrences
    end_activities
        (If provided) dictionary of end activities occurrences
    parameters
        Possible parameters of the algorithm,
        including: activity_key, case_id_glue, timestamp_key,
        dependency_thresh, and_measure_thresh, min_act_count, min_dfg_occurrences, dfg_pre_cleaning_noise_thresh,
        loops_length_two_thresh
    variant
        Variant of the algorithm (classic)

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    return VERSIONS_DFG_HEU[variant](dfg, activities=activities, activities_occurrences=activities_occurrences,
                                     start_activities=start_activities, end_activities=end_activities,
                                     parameters=parameters)
