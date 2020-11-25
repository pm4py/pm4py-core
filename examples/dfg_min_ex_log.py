import os

from pm4py.algo.discovery.dfg import algorithm as dfg_algorithm
from pm4py.objects.conversion.dfg import converter as dfg_conv
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.statistics.end_activities.log import get as ea_get
from pm4py.statistics.start_activities.log import get as sa_get
from pm4py.statistics.sojourn_time.log import get as soj_time_get
from pm4py.statistics.concurrent_activities.log import get as conc_act_get
from pm4py.statistics.eventually_follows.log import get as efg_get
from pm4py.util import constants
from pm4py.visualization.dfg import visualizer as dfg_vis_fact
from pm4py.visualization.petrinet import visualizer as pn_vis


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "interval_event_log.xes")
    log = xes_importer.apply(log_path)
    parameters = {}
    parameters[constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] = "start_timestamp"
    parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = "time:timestamp"
    parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = "concept:name"
    parameters["format"] = "svg"
    start_activities = sa_get.get_start_activities(log, parameters=parameters)
    end_activities = ea_get.get_end_activities(log, parameters=parameters)
    parameters["start_activities"] = start_activities
    parameters["end_activities"] = end_activities
    soj_time = soj_time_get.apply(log, parameters=parameters)
    print("soj_time")
    print(soj_time)
    conc_act = conc_act_get.apply(log, parameters=parameters)
    print("conc_act")
    print(conc_act)
    efg = efg_get.apply(log, parameters=parameters)
    print("efg")
    print(efg)
    dfg_freq = dfg_algorithm.apply(log, parameters=parameters, variant=dfg_algorithm.Variants.FREQUENCY)
    dfg_perf = dfg_algorithm.apply(log, parameters=parameters, variant=dfg_algorithm.Variants.PERFORMANCE)
    dfg_gv_freq = dfg_vis_fact.apply(dfg_freq, log=log, variant=dfg_vis_fact.Variants.FREQUENCY,
                                     parameters=parameters)
    dfg_vis_fact.view(dfg_gv_freq)
    dfg_gv_perf = dfg_vis_fact.apply(dfg_perf, log=log, variant=dfg_vis_fact.Variants.PERFORMANCE,
                                     parameters=parameters)
    dfg_vis_fact.view(dfg_gv_perf)
    net, im, fm = dfg_conv.apply(dfg_freq)
    gviz = pn_vis.apply(net, im, fm, parameters=parameters)
    pn_vis.view(gviz)


if __name__ == "__main__":
    execute_script()
