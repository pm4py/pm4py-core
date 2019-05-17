from pm4py.objects.log.log import EventLog
from pm4py.algo.discovery.dfg import factory as dfg_miner
import pandas
from pm4py import util as pmutil
from pm4py.objects.log.util import xes as xes_util
from pm4py.objects.log.util import general as log_util
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.algo.discovery.dfg.utils import dfg_utils
from pm4py.algo.filtering.pandas.start_activities import start_activities_filter as pd_start_act_filter
from pm4py.algo.filtering.pandas.end_activities import end_activities_filter as pd_end_act_filter
from pm4py.algo.filtering.pandas.attributes import attributes_filter as pd_attr_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter as log_start_act_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter as log_end_act_filter
from pm4py.algo.filtering.log.attributes import attributes_filter as log_attr_filter
from pm4py.objects.petri.utils import add_arc_from_to


def apply(obj, parameters=None):
    """
    Applies the DFG mining on a given object (if it is a Pandas dataframe or a log, the DFG is calculated)

    Parameters
    -------------
    obj
        Object (DFG) (if it is a Pandas dataframe or a log, the DFG is calculated)
    parameters
        Parameters
    """
    if parameters is None:
        parameters = {}

    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = xes_util.DEFAULT_TIMESTAMP_KEY
    if pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY] = log_util.CASE_ATTRIBUTE_GLUE

    if isinstance(obj, pandas.core.frame.DataFrame):
        dfg = df_statistics.get_dfg_graph(obj, case_id_glue=parameters[pmutil.constants.PARAMETER_CONSTANT_CASEID_KEY],
                                          activity_key=parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY],
                                          timestamp_key=parameters[pmutil.constants.PARAMETER_CONSTANT_TIMESTAMP_KEY])
        start_activities = list(pd_start_act_filter.get_start_activities(obj, parameters=parameters).keys())
        end_activities = list(pd_end_act_filter.get_end_activities(obj, parameters=parameters).keys())
        activities = pd_attr_filter.get_attribute_values(obj,
                                                         parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY],
                                                         parameters=parameters)
    elif type(obj) is EventLog:
        dfg = dfg_miner.apply(obj, parameters=parameters)
        start_activities = list(log_start_act_filter.get_start_activities(obj, parameters=parameters).keys())
        end_activities = list(log_end_act_filter.get_end_activities(obj, parameters=parameters).keys())
        activities = log_attr_filter.get_attribute_values(obj,
                                                          parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY],
                                                          parameters=parameters)
    else:
        dfg = obj
        start_activities = dfg_utils.infer_start_activities(obj)
        end_activities = dfg_utils.infer_end_activities(obj)
        activities = dfg_utils.get_activities_from_dfg(obj)

    net = PetriNet("")
    im = Marking()
    fm = Marking()

    source = PetriNet.Place("source")
    net.places.add(source)
    im[source] = 1
    sink = PetriNet.Place("sink")
    net.places.add(sink)
    fm[sink] = 1

    places_corr = {}
    index = 0

    for act in activities:
        places_corr[act] = PetriNet.Place(act)
        net.places.add(places_corr[act])

    for act in start_activities:
        index = index + 1
        trans = PetriNet.Transition(act + "_" + str(index), act)
        net.transitions.add(trans)
        add_arc_from_to(source, trans, net)
        add_arc_from_to(trans, places_corr[act], net)

    for act in end_activities:
        index = index + 1
        inv_trans = PetriNet.Transition(act + "_" + str(index), None)
        net.transitions.add(inv_trans)
        add_arc_from_to(places_corr[act], inv_trans, net)
        add_arc_from_to(inv_trans, sink, net)

    for el in dfg.keys():
        act1 = el[0]
        act2 = el[1]

        index = index + 1
        trans = PetriNet.Transition(act2 + "_" + str(index), act2)
        net.transitions.add(trans)

        add_arc_from_to(places_corr[act1], trans, net)
        add_arc_from_to(trans, places_corr[act2], net)

    return net, im, fm
