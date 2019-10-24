import os
import time

from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.discovery.inductive import factory as inductive_factory
from pm4py.objects.dfg.filtering import dfg_filtering
from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.auto_filter import auto_filter
from pm4py.algo.filtering.pandas.cases import case_filter
from pm4py.objects.log.adapters.pandas import csv_import_adapter as csv_import_adapter
from pm4py.util import constants
from pm4py.visualization.dfg import factory as dfg_vis_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_decorations_from_dfg_spaths_acticount
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_shortest_paths

SEP = ","
QUOTECHAR = None
inputLog = os.path.join("..", "tests", "input_data", "running-example.csv")
CASEID_GLUE = "case:concept:name"
ACTIVITY_KEY = "concept:name"
TIMEST_KEY = "time:timestamp"
TIMEST_COLUMNS = ["time:timestamp"]
TIMEST_FORMAT = None
enable_auto_filter = True
enable_filtering_on_cases = True
max_no_cases = 1000
enable_filtering_df = True
filtering_df_noise = 0.01

"""
SEP = ","
QUOTECHAR = None
inputLog = os.path.join("C:\\road_traffic.csv")
CASEID_GLUE = "case"
ACTIVITY_KEY = "event"
TIMEST_KEY = "startTime"
TIMEST_COLUMNS = ["startTime"]
TIMEST_FORMAT = "%Y/%m/%d %H:%M:%S"
enable_auto_filter=False
enable_filtering_on_activities=False
enable_filtering_on_cases=False
enable_filtering_df=True
filtering_df_noise=0.01
"""


def execute_script():
    time1 = time.time()
    dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=SEP, quotechar=QUOTECHAR)
    time2 = time.time()
    print("time2 - time1: " + str(time2 - time1))
    parameters_filtering = {constants.PARAMETER_CONSTANT_CASEID_KEY: CASEID_GLUE,
                            constants.PARAMETER_CONSTANT_ACTIVITY_KEY: ACTIVITY_KEY}
    if enable_auto_filter:
        dataframe = auto_filter.apply_auto_filter(dataframe, parameters=parameters_filtering)
    else:
        dataframe = attributes_filter.apply_auto_filter(dataframe, parameters=parameters_filtering)
    time3 = time.time()
    print("time3 - time2: " + str(time3 - time2))
    if enable_filtering_on_cases:
        dataframe = case_filter.filter_on_ncases(dataframe, case_id_glue=CASEID_GLUE, max_no_cases=max_no_cases)
    time4 = time.time()
    dataframe = csv_import_adapter.convert_caseid_column_to_str(dataframe, case_id_glue=CASEID_GLUE)
    dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe, timest_columns=TIMEST_COLUMNS,
                                                                   timest_format=TIMEST_FORMAT)
    time6 = time.time()
    print("time6 - time4: " + str(time6 - time4))
    # dataframe = dataframe.sort_values('time:timestamp')
    time7 = time.time()
    print("time7 - time6: " + str(time7 - time6))

    # show the filtered dataframe on the screen
    activities_count = attributes_filter.get_attribute_values(dataframe, attribute_key=ACTIVITY_KEY)
    [dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both",
                                                                   perf_aggregation_key="median",
                                                                   case_id_glue=CASEID_GLUE, activity_key=ACTIVITY_KEY,
                                                                   timestamp_key=TIMEST_KEY)
    if enable_filtering_df:
        print("len dfg_frequency 0=", len(dfg_frequency))
        dfg_frequency = dfg_filtering.apply(dfg_frequency, {"noiseThreshold": filtering_df_noise})
        print("len dfg_frequency 1=", len(dfg_frequency))
    time8 = time.time()
    print("time8 - time7: " + str(time8 - time7))
    gviz = dfg_vis_factory.apply(dfg_frequency, activities_count=activities_count, parameters={"format": "svg"})
    dfg_vis_factory.view(gviz)
    net, initial_marking, final_marking = inductive_factory.apply_dfg(dfg_frequency)
    # net, initial_marking, final_marking = alpha_factory.apply_dfg(dfg_frequency)
    spaths = get_shortest_paths(net)
    time9 = time.time()
    print("time9 - time8: " + str(time9 - time8))
    aggregated_statistics = get_decorations_from_dfg_spaths_acticount(net, dfg_performance,
                                                                      spaths,
                                                                      activities_count,
                                                                      variant="performance")
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, variant="performance",
                                aggregated_statistics=aggregated_statistics, parameters={"format": "svg"})
    time10 = time.time()
    print("time10 - time9: " + str(time10 - time9))
    print("time10 - time1: " + str(time10 - time1))
    pn_vis_factory.view(gviz)


if __name__ == "__main__":
    execute_script()
