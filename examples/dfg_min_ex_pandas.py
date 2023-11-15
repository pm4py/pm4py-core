import os

import pm4py
import pandas as pd
from pm4py.util import constants
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.objects.conversion.dfg import converter as dfg_conv
from pm4py.statistics.attributes.pandas import get as att_get
from pm4py.statistics.end_activities.pandas import get as ea_get
from pm4py.statistics.sojourn_time.pandas import get as soj_time_get
from pm4py.statistics.concurrent_activities.pandas import get as conc_act_get
from pm4py.statistics.eventually_follows.pandas import get as efg_get
from pm4py.statistics.start_activities.pandas import get as sa_get
from pm4py.visualization.dfg import visualizer as dfg_vis_fact
from pm4py.visualization.petri_net import visualizer as pn_vis
from examples import examples_conf


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "interval_event_log.csv")
    dataframe = pd.read_csv(log_path)
    log_path = os.path.join("..", "tests", "input_data", "reviewing.xes")
    log = pm4py.read_xes(log_path)
    dataframe = pm4py.convert_to_dataframe(log)
    parameters = {}
    #parameters[constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY] = "start_timestamp"
    parameters[constants.PARAMETER_CONSTANT_TIMESTAMP_KEY] = "time:timestamp"
    parameters[constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = "concept:name"
    parameters[constants.PARAMETER_CONSTANT_CASEID_KEY] = "case:concept:name"
    parameters["strict"] = True
    parameters["format"] = examples_conf.TARGET_IMG_FORMAT
    start_activities = sa_get.get_start_activities(dataframe, parameters=parameters)
    end_activities = ea_get.get_end_activities(dataframe, parameters=parameters)
    att_count = att_get.get_attribute_values(dataframe, "concept:name", parameters=parameters)
    parameters["start_activities"] = start_activities
    parameters["end_activities"] = end_activities
    soj_time = soj_time_get.apply(dataframe, parameters=parameters)
    print("soj_time")
    print(soj_time)
    conc_act = conc_act_get.apply(dataframe, parameters=parameters)
    print("conc_act")
    print(conc_act)
    efg = efg_get.apply(dataframe, parameters=parameters)
    print("efg")
    print(efg)
    dfg_freq, dfg_perf = df_statistics.get_dfg_graph(dataframe, measure="both", start_timestamp_key="start_timestamp")
    dfg_gv_freq = dfg_vis_fact.apply(dfg_freq, activities_count=att_count, variant=dfg_vis_fact.Variants.FREQUENCY,
                                     soj_time=soj_time, parameters=parameters)
    dfg_vis_fact.view(dfg_gv_freq)
    dfg_gv_perf = dfg_vis_fact.apply(dfg_perf, activities_count=att_count, variant=dfg_vis_fact.Variants.PERFORMANCE,
                                     soj_time=soj_time, parameters=parameters)
    dfg_vis_fact.view(dfg_gv_perf)
    net, im, fm = dfg_conv.apply(dfg_freq)
    gviz = pn_vis.apply(net, im, fm, parameters=parameters)
    pn_vis.view(gviz)


if __name__ == "__main__":
    execute_script()
