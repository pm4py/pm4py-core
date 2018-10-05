from pm4py.entities.log.util import trace_log as tl_util
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.entities import petri
from pm4py.entities.petri.petrinet import Marking
import time
import sys
from collections import Counter
from pm4py import util as pmutil
from pm4py.entities.log.util import xes as xes_util
from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.algo.discovery.inductive.util import petri_cleaning, shared_constants
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.versions.dfg.util.tree_to_petri import form_petrinet
from pm4py.algo.discovery.inductive.versions.dfg.data_structures.subtree import Subtree

sys.setrecursionlimit(100000)


def apply(trace_log, parameters):
    """
    Apply the IMDF algorithm to a log

    Parameters
    -----------
    trace_log
        Trace log
    parameters
        Parameters of the algorithm

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    # apply the reduction by default only on very small logs
    enable_reduction = parameters["enable_reduction"] if "enable_reduction" in parameters else (
            shared_constants.APPLY_REDUCTION_ON_SMALL_LOG and shared_constants.MAX_LOG_SIZE_FOR_REDUCTION)

    indMinDirFollows = InductMinDirFollows()
    net, initial_marking, final_marking = indMinDirFollows.apply(trace_log, parameters, activity_key=activity_key)

    # clean net from duplicate hidden transitions
    net = petri_cleaning.clean_duplicate_transitions(net)

    if enable_reduction:
        # do the replay
        aligned_traces = token_replay.apply(trace_log, net, initial_marking, final_marking, parameters=parameters)

        # apply petri_reduction technique in order to simplify the Petri net
        net = petri_cleaning.petri_reduction_treplay(net, parameters={"aligned_traces": aligned_traces})

    return net, initial_marking, final_marking


def apply_dfg(dfg, parameters):
    """
    Apply the IMDF algorithm to a DFG graph

    Parameters
    -----------
    dfg
        Directly-Follows graph
    parameters
        Parameters of the algorithm

    Returns
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}
    if not pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    indMinDirFollows = InductMinDirFollows()
    net, initial_marking, final_marking = indMinDirFollows.apply_dfg(dfg, parameters, activity_key=activity_key)

    # clean net from duplicate hidden transitions
    net = petri_cleaning.clean_duplicate_transitions(net)

    return net, initial_marking, final_marking


class InductMinDirFollows(object):
    def apply(self, trace_log, parameters, activity_key="concept:name"):
        """
        Apply the IMDF algorithm to a log

        Parameters
        -----------
        trace_log
            Trace log
        parameters
            Parameters of the algorithm
        activity_key
            Attribute corresponding to the activity

        Returns
        -----------
        net
            Petri net
        initial_marking
            Initial marking
        final_marking
            Final marking
        """
        self.trace_log = trace_log
        labels = tl_util.get_event_labels(trace_log, activity_key)
        dfg = [(k, v) for k, v in dfg_inst.apply(trace_log, parameters={
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
        return self.apply_dfg(dfg, parameters)

    def apply_dfg(self, dfg, parameters, activity_key="concept:name"):
        """
        Apply the IMDF algorithm to a DFG graph

        Parameters
        -----------
        dfg
            Directly-Follows graph
        parameters
            Parameters of the algorithm

        Returns
        -----------
        net
            Petri net
        initial_marking
            Initial marking
        final_marking
            Final marking
        """

        if parameters is None:
            parameters = {}

        noiseThreshold = 0.0

        if "noiseThreshold" in parameters:
            noiseThreshold = parameters["noiseThreshold"]

        if type(dfg) is Counter or type(dfg) is dict:
            newdfg = []
            for key in dfg:
                value = dfg[key]
                newdfg.append((key, value))
            dfg = newdfg

        c = Counts()
        s = Subtree(dfg, dfg, None, c, 0, noiseThreshold=noiseThreshold)
        net = petri.petrinet.PetriNet('imdf_net_' + str(time.time()))
        initial_marking = Marking()
        final_marking = Marking()
        net, initial_marking, final_marking, lastAddedPlace, counts = form_petrinet(s, 0, c, net, initial_marking, final_marking)

        return net, initial_marking, final_marking
