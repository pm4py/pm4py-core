from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.filtering.common.filtering_constants import CASE_CONCEPT_NAME
from pm4py.algo.filtering.log.attributes import attributes_filter as log_attributes
from pm4py.algo.filtering.log.end_activities import end_activities_filter as log_ea_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter as log_sa_filter
from pm4py.algo.filtering.pandas.attributes import attributes_filter as pd_attributes
from pm4py.algo.filtering.pandas.end_activities import end_activities_filter as pd_ea_filter
from pm4py.algo.filtering.pandas.start_activities import start_activities_filter as pd_sa_filter
from pm4py.objects.conversion.heuristics_net import factory as hn_conv_factory
from pm4py.objects.heuristics_net import defaults
from pm4py.objects.heuristics_net.net import HeuristicsNet
from pm4py.objects.log.util import xes
from pm4py.util import constants


def apply(log, parameters=None):
    """
    Discovers a Petri net using Heuristics Miner

    Parameters
    ------------
    log
        Event log
    parameters
        Possible parameters of the algorithm,
        including: activity_key, case_id_glue, timestamp_key,
        dependency_thresh, and_measure_thresh, min_act_count, min_dfg_occurrences, dfg_pre_cleaning_noise_thresh

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    heu_net = apply_heu(log, parameters=parameters)
    net, im, fm = hn_conv_factory.apply(heu_net, parameters=parameters)

    return net, im, fm


def apply_pandas(df, parameters=None):
    """
    Discovers a Petri net using Heuristics Miner

    Parameters
    ------------
    df
        Pandas dataframe
    parameters
        Possible parameters of the algorithm,
        including: activity_key, case_id_glue, timestamp_key,
        dependency_thresh, and_measure_thresh, min_act_count, min_dfg_occurrences, dfg_pre_cleaning_noise_thresh,
        loops_length_two_thresh

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY
    case_id_glue = parameters[
        constants.PARAMETER_CONSTANT_CASEID_KEY] if constants.PARAMETER_CONSTANT_CASEID_KEY in parameters else CASE_CONCEPT_NAME
    timestamp_key = parameters[
        constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] if constants.PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else xes.DEFAULT_TIMESTAMP_KEY

    start_activities = pd_sa_filter.get_start_activities(df, parameters=parameters)
    end_activities = pd_ea_filter.get_end_activities(df, parameters=parameters)
    activities_occurrences = pd_attributes.get_attribute_values(df, activity_key, parameters=parameters)
    activities = list(activities_occurrences.keys())
    if timestamp_key in df:
        dfg = df_statistics.get_dfg_graph(df, case_id_glue=case_id_glue,
                                          activity_key=activity_key, timestamp_key=timestamp_key)
    else:
        dfg = df_statistics.get_dfg_graph(df, case_id_glue=case_id_glue,
                                          activity_key=activity_key, sort_timestamp_along_case_id=False)

    heu_net = apply_heu_dfg(dfg, activities=activities, activities_occurrences=activities_occurrences,
                            start_activities=start_activities, end_activities=end_activities, parameters=parameters)
    net, im, fm = hn_conv_factory.apply(heu_net, parameters=parameters)

    return net, im, fm


def apply_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
              parameters=None):
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

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    heu_net = apply_heu_dfg(dfg, activities=activities, activities_occurrences=activities_occurrences,
                            start_activities=start_activities, end_activities=end_activities, parameters=parameters)
    net, im, fm = hn_conv_factory.apply(heu_net, parameters=parameters)

    return net, im, fm


def apply_heu(log, parameters=None):
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

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[
        constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else xes.DEFAULT_NAME_KEY

    start_activities = log_sa_filter.get_start_activities(log, parameters=parameters)
    end_activities = log_ea_filter.get_end_activities(log, parameters=parameters)
    activities_occurrences = log_attributes.get_attribute_values(log, activity_key, parameters=parameters)
    activities = list(activities_occurrences.keys())
    dfg = dfg_factory.apply(log, parameters=parameters)

    return apply_heu_dfg(dfg, activities=activities, activities_occurrences=activities_occurrences,
                         start_activities=start_activities,
                         end_activities=end_activities, parameters=parameters)


def apply_heu_dfg(dfg, activities=None, activities_occurrences=None, start_activities=None, end_activities=None,
                  parameters=None):
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

    Returns
    ------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    if parameters is None:
        parameters = {}

    dependency_thresh = parameters[
        defaults.DEPENDENCY_THRESH] if defaults.DEPENDENCY_THRESH in parameters else defaults.DEFAULT_DEPENDENCY_THRESH
    and_measure_thresh = parameters[
        defaults.AND_MEASURE_THRESH] if defaults.AND_MEASURE_THRESH in parameters else defaults.DEFAULT_AND_MEASURE_THRESH
    min_act_count = parameters[
        defaults.MIN_ACT_COUNT] if defaults.MIN_ACT_COUNT in parameters else defaults.DEFAULT_MIN_ACT_COUNT
    min_dfg_occurrences = parameters[
        defaults.MIN_DFG_OCCURRENCES] if defaults.MIN_DFG_OCCURRENCES in parameters else defaults.DEFAULT_MIN_DFG_OCCURRENCES
    dfg_pre_cleaning_noise_thresh = parameters[
        defaults.DFG_PRE_CLEANING_NOISE_THRESH] if defaults.DFG_PRE_CLEANING_NOISE_THRESH in parameters else defaults.DEFAULT_DFG_PRE_CLEANING_NOISE_THRESH
    loops_length_two_thresh = parameters[
        defaults.LOOP_LENGTH_TWO_THRESH] if defaults.LOOP_LENGTH_TWO_THRESH in parameters else defaults.DEFAULT_LOOP_LENGTH_TWO_THRESH
    heu_net = HeuristicsNet(dfg, activities=activities, activities_occurrences=activities_occurrences,
                            start_activities=start_activities, end_activities=end_activities)
    heu_net.calculate(dependency_thresh=dependency_thresh, and_measure_thresh=and_measure_thresh,
                      min_act_count=min_act_count, min_dfg_occurrences=min_dfg_occurrences,
                      dfg_pre_cleaning_noise_thresh=dfg_pre_cleaning_noise_thresh,
                      loops_length_two_thresh=loops_length_two_thresh)

    return heu_net
