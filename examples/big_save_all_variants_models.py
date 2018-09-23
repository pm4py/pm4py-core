import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.entities.log.adapters.pandas import csv_import_adapter as csv_import_adapter
from pm4py.algo.filtering.pandas.cases import case_filter
import time
from pm4py.algo.discovery.inductive import factory as inductive_factory
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.visualization.petrinet.util import vis_trans_shortest_paths
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.util import constants
from pm4py.algo.filtering.pandas.cases import case_filter
from pm4py.algo.cases.pandas import case_statistics
from pm4py.algo.filtering.pandas.variants import variants_filter
import shutil

TARGET_FOLDER_FREQ = "all_variants_freq"
TARGET_FOLDER_PERF = "all_variants_perf"
LOG_FILE = "log_file.txt"
REMOVE_TARGET_FOLDERS_WHEN_FINISHED = True
MIN_VAR_OCC = 1

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
    activities_count = attributes_filter.get_attribute_values(dataframe, attribute_key=ACTIVITY_KEY)
    [dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both", perf_aggregation_key="median", case_id_glue=CASEID_GLUE, activity_key=ACTIVITY_KEY, timestamp_key=TIMEST_KEY, sort_required=False)
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

if __name__ == "__main__":
    start_loading = time.time()
    if os.path.exists(TARGET_FOLDER_FREQ):
        shutil.rmtree(TARGET_FOLDER_FREQ)
    if os.path.exists(TARGET_FOLDER_PERF):
        shutil.rmtree(TARGET_FOLDER_PERF)

    os.mkdir(TARGET_FOLDER_FREQ)
    os.mkdir(TARGET_FOLDER_PERF)

    dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
    dataframe = csv_import_adapter.convert_caseid_column_to_str(dataframe, case_id_glue=CASEID_GLUE)
    dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe, timest_format=TIMEST_FORMAT,
                                                                   timest_columns=TIMEST_COLUMNS)
    dataframe = dataframe.sort_values([CASEID_GLUE, TIMEST_KEY])
    parameters = {constants.PARAMETER_CONSTANT_CASEID_KEY: CASEID_GLUE, constants.PARAMETER_CONSTANT_ACTIVITY_KEY: ACTIVITY_KEY, constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: TIMEST_KEY}

    end_loading = time.time()
    end_loading_str = "loading time of the log: "+str(end_loading-start_loading)

    print(end_loading_str)
    F = open(LOG_FILE, "w")
    F.write(end_loading_str + "\n")
    F.close()

    original_time = time.time()

    variantsDf = case_statistics.get_variants_df(dataframe, parameters=parameters)
    parameters["variants_df"] = variantsDf
    variants = case_statistics.get_variants_statistics(dataframe, parameters=parameters)

    for index, variant in enumerate(variants):
        if variant[CASEID_GLUE] >= MIN_VAR_OCC:
            filt0 = time.time()
            filt_dataframe = variants_filter.apply(dataframe, [variant["variant"]], parameters=parameters)
            filt1 = time.time()
            print("\t"+str(index)+" filtering time: "+str(filt1-filt0))
            IMG_FREQ = os.path.join(TARGET_FOLDER_FREQ, str(index)+".svg")
            IMG_PERF = os.path.join(TARGET_FOLDER_PERF, str(index)+".svg")
            calculate_process_schema_from_df(filt_dataframe, IMG_FREQ, IMG_PERF)
            current_time = time.time()
            stru = "variant "+str(index)+" interlapsed time: "+str(current_time - original_time)
            F = open(LOG_FILE, "a")
            F.write(stru+"\n")
            F.close()
            print(stru)

    if REMOVE_TARGET_FOLDERS_WHEN_FINISHED:
        shutil.rmtree(TARGET_FOLDER_FREQ)
        shutil.rmtree(TARGET_FOLDER_PERF)
        os.remove(LOG_FILE)