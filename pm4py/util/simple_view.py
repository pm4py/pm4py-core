from pm4py.algo.filtering.common import filtering_constants
from pm4py.util import constants
from pm4py.entities.log.util import xes as xes_util
from pm4py.entities.log.util import insert_classifier
from pm4py import util as pmutil
from pm4py.algo.filtering.tracelog.auto_filter import auto_filter
from copy import copy
from pm4py.algo.filtering.tracelog.attributes import attributes_filter as activities_module
from pm4py.algo.discovery.dfg import replacement as dfg_replacement, factory as dfg_factory
from pm4py.visualization.dfg import factory as dfg_vis_factory
from pm4py.algo.discovery.alpha import factory as alpha_factory
from pm4py.algo.discovery.inductive import factory as inductive_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.algo.discovery.transition_system import factory as ts_factory
from pm4py.visualization.transition_system import factory as ts_vis_factory
from pm4py.algo.discovery.transition_system.parameters import *
from pm4py.visualization.common.save import *
from pm4py.visualization.common.gview import *

def apply(original_log, parameters=None):
    """
    Get a picture representing a simplified version of the original log

    Parameters
    -----------
    original_log
        Log
    parameters
        Parameters of the algorithm, including:
            algorithm -> Process discovery algorithm to use (e.g. alpha, inductive, dfg)
            decoration -> Decoration to use in the diagram (e.g. frequency, performance)
            format -> Produced image format
            activity key -> Must be specified if different from concept:name
            decreasingFactor -> The higher is the decreasing factor, the more simplified is the process model represented
            replayEnabled -> Boolean that tells if the decoration is enabled or not
            aggregationMeasure -> Aggregation measure
    """
    if parameters is None:
        parameters = {}

    activity_key = parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] if constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters else None
    discoveryAlgorithm = parameters["algorithm"] if "algorithm" in parameters else "inductive"
    replayMeasure = parameters["decoration"] if "decoration" in parameters else "frequency"
    imageFormat = parameters["format"] if "format" in parameters else "png"
    decreasingFactor = parameters["simplicity"] if "simplicity" in parameters else filtering_constants.DECREASING_FACTOR
    replayEnabled = parameters["replayEnabled"] if "replayEnabled" in parameters else True
    if "frequency" in replayMeasure:
        aggregationMeasure = parameters["aggregationMeasure"] if "aggregationMeasure" in parameters else "min"
    elif "performance" in replayMeasure:
        aggregationMeasure = parameters["aggregationMeasure"] if "aggregationMeasure" in parameters else "mean"

    original_log, classifier_key = insert_classifier.search_and_insert_event_classifier_attribute(original_log,
                                                                                                  force_activity_transition_insertion=True)
    if activity_key is None:
        activity_key = classifier_key
    if activity_key is None:
        activity_key = xes_util.DEFAULT_NAME_KEY

    parameters_viz = {"format": imageFormat, pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key, "aggregationMeasure": aggregationMeasure}
    # apply automatically a filter
    parameters_autofilter = {constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key,
                             constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: activity_key,
                             "decreasingFactor": decreasingFactor}

    log = auto_filter.apply_auto_filter(copy(original_log), parameters=parameters_autofilter)
    # apply a process discovery algorithm
    parameters_discovery = {pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key, "aggregationMeasure": aggregationMeasure}
    if discoveryAlgorithm == "tsystem" or discoveryAlgorithm == "tsystem2":
        parameters_discovery[PARAM_KEY_WINDOW] = 2
        ts_from_log = ts_factory.apply(log, parameters=parameters_discovery)
        gviz = ts_vis_factory.apply(ts_from_log, variant=replayMeasure, parameters=parameters_viz)
    elif discoveryAlgorithm == "tsystem3":
        parameters_discovery[PARAM_KEY_WINDOW] = 3
        ts_from_log = ts_factory.apply(log, parameters=parameters_discovery)
        gviz = ts_vis_factory.apply(ts_from_log, variant=replayMeasure, parameters=parameters_viz)
    elif discoveryAlgorithm == "dfg":
        # gets the number of occurrences of the single attributes in the filtered log
        filtered_log_activities_count = activities_module.get_attribute_values(log, activity_key, parameters=parameters_autofilter)
        # gets an intermediate log that is the original log restricted to the list
        # of attributes that appears in the filtered log
        intermediate_log = activities_module.apply_events(original_log,
                                                          filtered_log_activities_count,
                                                          parameters=parameters_autofilter)
        # gets the number of occurrences of the single attributes in the intermediate log
        activities_count = activities_module.get_attribute_values(intermediate_log, activity_key, parameters=parameters_autofilter)
        # calculate DFG of the filtered log and of the intermediate log
        dfg_filtered_log = dfg_factory.apply(log, parameters=parameters_discovery, variant=replayMeasure)
        dfg_intermediate_log = dfg_factory.apply(intermediate_log, parameters=parameters_discovery,
                                                 variant=replayMeasure)
        # replace edges values in the filtered DFG from the one found in the intermediate log
        dfg_filtered_log = dfg_replacement.replace_values(dfg_filtered_log, dfg_intermediate_log)
        gviz = dfg_vis_factory.apply(dfg_filtered_log, activities_count=activities_count, variant=replayMeasure,
                                     parameters=parameters_viz)
    else:
        if discoveryAlgorithm == "inductive":
            net, initial_marking, final_marking = inductive_factory.apply(log, parameters=parameters_discovery)
        elif discoveryAlgorithm == "alpha":
            net, initial_marking, final_marking = alpha_factory.apply(log, parameters=parameters_discovery)
        if replayEnabled:
            # do the replay
            gviz = pn_vis_factory.apply(net, initial_marking, final_marking, log=original_log, variant=replayMeasure,
                                        parameters=parameters_viz)
        else:
            # return the diagram in base64
            gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters=parameters_viz)

    return gviz