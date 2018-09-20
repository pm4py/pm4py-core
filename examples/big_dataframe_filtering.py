import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pm4py
from pm4py.entities.log.adapters.pandas import csv_import_adapter as csv_import_adapter
from pm4py.filtering.pandas import df_filtering
import time
from pm4py.algo.discovery.inductive import factory as inductive_factory
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.entities.petri import vis_trans_shortest_paths
from pm4py.visualization.petrinet import factory as pn_vis_factory

MAX_NO_ACTIVITIES_PER_MODEL = 25
GENERATED_IMAGES = []
REMOVE_GENERATED_IMAGES = True

inputLog = os.path.join("..", "tests", "inputData", "running-example.csv")
CASEID_GLUE = "case:concept:name"
ACTIVITY_KEY = "concept:name"
TIMEST_KEY = "time:timestamp"
TIMEST_COLUMNS = ["time:timestamp"]
TIMEST_FORMAT = None
ATTRIBUTE_TO_FILTER = "concept:name"
ATTRIBUTE_VALUES_TO_FILTER = ["reject request"]

"""
inputLog = os.path.join("C:\\road_traffic.csv")
CASEID_GLUE = "case"
ACTIVITY_KEY = "event"
TIMEST_KEY = "startTime"
TIMEST_COLUMNS = ["startTime"]
TIMEST_FORMAT = "%Y/%m/%d %H:%M:%S"
ATTRIBUTE_TO_FILTER = "event"
ATTRIBUTE_VALUES_TO_FILTER = ["Insert Fine Notification"]
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

def execute_script():
    aa = time.time()
    dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
    dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe, timest_format=TIMEST_FORMAT, timest_columns=TIMEST_COLUMNS)
    dataframe_fa = df_filtering.filter_df_on_activities(dataframe, activity_key=ACTIVITY_KEY, max_no_activities=MAX_NO_ACTIVITIES_PER_MODEL)
    bb = time.time()
    print("importing log time=",(bb-aa))
    calculate_process_schema_from_df(dataframe_fa, "NOFILTERS_FREQUENCY.svg", "NOFILTERS_PERFORMANCE.svg")
    GENERATED_IMAGES.append("NOFILTERS_FREQUENCY.svg")
    GENERATED_IMAGES.append("NOFILTERS_PERFORMANCE.svg")
    del dataframe_fa
    cc = time.time()
    print("saving initial Inductive Miner process schema along with frequency metrics=",(cc-bb))

    dataframe_cp = df_filtering.filter_df_on_case_performance(dataframe, case_id_glue=CASEID_GLUE, timestamp_key=TIMEST_KEY, min_case_performance=100000, max_case_performance=10000000)
    dataframe_cp_fa = df_filtering.filter_df_on_activities(dataframe_cp, activity_key=ACTIVITY_KEY, max_no_activities=MAX_NO_ACTIVITIES_PER_MODEL)
    dataframe_cp = None
    del dataframe_cp
    calculate_process_schema_from_df(dataframe_cp_fa, "FILTER_CP_FREQUENCY.svg", "FILTER_CP_PERFORMANCE.svg")
    GENERATED_IMAGES.append("FILTER_CP_FREQUENCY.svg")
    GENERATED_IMAGES.append("FILTER_CP_PERFORMANCE.svg")
    del dataframe_cp_fa
    dd = time.time()
    print("filtering on case performance and generating process schema=",(dd-cc))

    dataframe_att = df_filtering.filter_df_on_attribute_values(dataframe, case_id_glue=CASEID_GLUE, attribute_key=ATTRIBUTE_TO_FILTER, values=ATTRIBUTE_VALUES_TO_FILTER, positive=True)
    dataframe_att_fa = df_filtering.filter_df_on_activities(dataframe_att, activity_key=ACTIVITY_KEY, max_no_activities=MAX_NO_ACTIVITIES_PER_MODEL)
    del dataframe_att
    calculate_process_schema_from_df(dataframe_att_fa, "FILTER_ATT_FREQUENCY.svg", "FILTER_ATT_PERFORMANCE.svg")
    GENERATED_IMAGES.append("FILTER_ATT_FREQUENCY.svg")
    GENERATED_IMAGES.append("FILTER_ATT_PERFORMANCE.svg")
    del dataframe_att_fa
    ee = time.time()
    print("filtering on attribute values and generating process schema=",(ee-dd))

    if REMOVE_GENERATED_IMAGES:
        for image in GENERATED_IMAGES:
            os.remove(image)

if __name__ == '__main__':
    execute_script()