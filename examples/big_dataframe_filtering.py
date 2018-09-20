import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.adapters.pandas import csv_import_adapter as csv_import_adapter
from pm4py.log.importer.csv.versions import pandas_df_imp
from pm4py.filtering.pandas import df_filtering
import time
from pm4py.algo.inductive import factory as inductive_factory
from pm4py.algo.dfg.adapters.pandas import df_statistics
from pm4py.models.petri import vis_trans_shortest_paths
from pm4py.visualization.petrinet import factory as pn_vis_factory

inputLog = os.path.join("..", "tests", "inputData", "running-example.csv")
CASEID_GLUE = "case:concept:name"
ACTIVITY_KEY = "concept:name"
TIMEST_KEY = "time:timestamp"
TIMEST_COLUMNS = ["time:timestamp"]
TIMEST_FORMAT = None

"""
inputLog = os.path.join("C:\\road_traffic.csv")
CASEID_GLUE = "case"
ACTIVITY_KEY = "event"
TIMEST_KEY = "startTime"
TIMEST_COLUMNS = ["startTime"]
TIMEST_FORMAT = "%Y/%m/%d %H:%M:%S"
"""

def calculate_process_schema_from_df(dataframe, path_frequency, path_performance):
    activities_count = df_statistics.get_activities_count(dataframe, activity_key=ACTIVITY_KEY)
    [dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both", perf_aggregation_key="median", case_id_glue=CASEID_GLUE, activity_key=ACTIVITY_KEY, timestamp_key=TIMEST_KEY)
    net, initial_marking, final_marking = inductive_factory.apply_dfg(dfg_frequency)
    spaths = vis_trans_shortest_paths.get_shortest_paths(net)
    aggregated_statistics = vis_trans_shortest_paths.get_net_decorations_from_dfg_spaths_acticount(net, dfg_frequency, spaths, activities_count, variant="frequency")
    parameters_viz = {"format":"svg"}
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, variant="frequency", aggregated_statistics=aggregated_statistics, parameters=parameters_viz)
    pn_vis_factory.save(gviz, path_frequency)
    aggregated_statistics = vis_trans_shortest_paths.get_net_decorations_from_dfg_spaths_acticount(net, dfg_performance, spaths, activities_count, variant="performance")
    parameters_viz = {"format":"svg"}
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, variant="performance", aggregated_statistics=aggregated_statistics, parameters=parameters_viz)
    pn_vis_factory.save(gviz, path_performance)

aa = time.time()
dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe, timest_format=TIMEST_FORMAT, timest_columns=TIMEST_COLUMNS)
bb = time.time()
print("importing log time=",(bb-aa))
calculate_process_schema_from_df(dataframe, "NOFILTERS_FREQUENCY.svg", "NOFILTERS_PERFORMANCE.svg")
cc = time.time()
print("saving initial Inductive Miner process schema along with frequency metrics=",(cc-bb))
dataframe_cp = df_filtering.filter_df_on_case_performance(dataframe, case_id_glue=CASEID_GLUE, timestamp_key=TIMEST_KEY, min_case_performance=100000, max_case_performance=10000000)
calculate_process_schema_from_df(dataframe_cp, "FILTER_CP_FREQUENCY.svg", "FILTER_CP_PERFORMANCE.svg")
dd = time.time()
print("filtering on case performance and generating process schema=",(dd-cc))
del dataframe_cp