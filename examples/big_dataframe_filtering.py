import os
import time

from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.algo.discovery.inductive import factory as inductive_factory
from pm4py.algo.filtering.pandas.attributes import attributes_filter
from pm4py.algo.filtering.pandas.cases import case_filter
from pm4py.algo.filtering.pandas.end_activities import end_activities_filter
from pm4py.algo.filtering.pandas.start_activities import start_activities_filter
from pm4py.objects.log.adapters.pandas import csv_import_adapter as csv_import_adapter
from pm4py.statistics.traces.pandas import case_statistics
from pm4py.util import constants
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.petrinet.util import vis_trans_shortest_paths

MAX_NO_ACTIVITIES = 25
GENERATED_IMAGES = []
REMOVE_GENERATED_IMAGES = True

inputLog = os.path.join("..", "tests", "input_data", "running-example.csv")
CASEID_GLUE = "case:concept:name"
ACTIVITY_KEY = "concept:name"
TIMEST_KEY = "time:timestamp"
TIMEST_COLUMNS = ["time:timestamp"]
TIMEST_FORMAT = None
ENABLE_ATTRIBUTE_FILTER = True
ATTRIBUTE_TO_FILTER = "concept:name"
ATTRIBUTE_VALUES_TO_FILTER = ["reject request"]
ENABLE_STARTACT_FILTER = True
STARTACT_TO_FILTER = ["register request"]
ENABLE_ENDACT_FILTER = True
ENDACT_TO_FILTER = ["pay compensation"]
DELETE_VARIABLES = False

"""
inputLog = os.path.join("C:\\road_traffic.csv")
CASEID_GLUE = "case"
ACTIVITY_KEY = "event"
TIMEST_KEY = "startTime"
TIMEST_COLUMNS = ["startTime"]
TIMEST_FORMAT = "%Y/%m/%d %H:%M:%S"
ENABLE_ATTRIBUTE_FILTER = True
ATTRIBUTE_TO_FILTER = "event"
ATTRIBUTE_VALUES_TO_FILTER = ["Insert Fine Notification"]
ENABLE_STARTACT_FILTER = True
STARTACT_TO_FILTER = ["Create Fine"]
ENABLE_ENDACT_FILTER = True
ENDACT_TO_FILTER = ["Payment", "Send for Credit Collection"]
DELETE_VARIABLES = True
"""


def calculate_process_schema_from_df(dataframe, path_frequency, path_performance):
    activities_count = attributes_filter.get_attribute_values(dataframe, attribute_key=ACTIVITY_KEY)
    [dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both",
                                                                   perf_aggregation_key="median",
                                                                   case_id_glue=CASEID_GLUE, activity_key=ACTIVITY_KEY,
                                                                   timestamp_key=TIMEST_KEY, sort_caseid_required=False)
    net, initial_marking, final_marking = inductive_factory.apply_dfg(dfg_frequency)
    spaths = vis_trans_shortest_paths.get_shortest_paths(net)
    aggregated_statistics = vis_trans_shortest_paths.get_decorations_from_dfg_spaths_acticount(net, dfg_frequency,
                                                                                               spaths,
                                                                                               activities_count,
                                                                                               variant="frequency")
    parameters_viz = {"format": "svg"}
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, variant="frequency",
                                aggregated_statistics=aggregated_statistics, parameters=parameters_viz)
    pn_vis_factory.save(gviz, path_frequency)
    aggregated_statistics = vis_trans_shortest_paths.get_decorations_from_dfg_spaths_acticount(net, dfg_performance,
                                                                                               spaths,
                                                                                               activities_count,
                                                                                               variant="performance")
    parameters_viz = {"format": "svg"}
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, variant="performance",
                                aggregated_statistics=aggregated_statistics, parameters=parameters_viz)
    pn_vis_factory.save(gviz, path_performance)


def execute_script():
    aa = time.time()
    dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
    dataframe = csv_import_adapter.convert_caseid_column_to_str(dataframe, case_id_glue=CASEID_GLUE)
    dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe, timest_format=TIMEST_FORMAT,
                                                                   timest_columns=TIMEST_COLUMNS)
    dataframe = dataframe.sort_values([CASEID_GLUE, TIMEST_KEY])
    dataframe_fa = attributes_filter.filter_df_keeping_spno_activities(dataframe, activity_key=ACTIVITY_KEY,
                                                                       max_no_activities=MAX_NO_ACTIVITIES)
    bb = time.time()
    print("importing log time=", (bb - aa))

    parameters_cde = {constants.PARAMETER_CONSTANT_CASEID_KEY: CASEID_GLUE,
                      constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: TIMEST_KEY, "sort_by_column": "caseDuration",
                      "sort_ascending": False, "max_ret_cases": 1000}
    cases_desc = case_statistics.get_cases_description(dataframe, parameters=parameters_cde)

    print(cases_desc)
    bb2 = time.time()
    print("calculating and printing cases_desc = ", (bb2 - bb))
    calculate_process_schema_from_df(dataframe_fa, "NOFILTERS_FREQUENCY.svg", "NOFILTERS_PERFORMANCE.svg")
    GENERATED_IMAGES.append("NOFILTERS_FREQUENCY.svg")
    GENERATED_IMAGES.append("NOFILTERS_PERFORMANCE.svg")
    if DELETE_VARIABLES:
        del dataframe_fa
    cc = time.time()
    print("saving initial Inductive Miner process schema along with frequency metrics=", (cc - bb2))

    dataframe_cp = case_filter.filter_on_case_performance(dataframe, case_id_glue=CASEID_GLUE, timestamp_key=TIMEST_KEY,
                                                          min_case_performance=100000, max_case_performance=10000000)
    dataframe_cp_fa = attributes_filter.filter_df_keeping_spno_activities(dataframe_cp, activity_key=ACTIVITY_KEY,
                                                                          max_no_activities=MAX_NO_ACTIVITIES)
    dataframe_cp = None
    if DELETE_VARIABLES:
        del dataframe_cp
    calculate_process_schema_from_df(dataframe_cp_fa, "FILTER_CP_FREQUENCY.svg", "FILTER_CP_PERFORMANCE.svg")
    GENERATED_IMAGES.append("FILTER_CP_FREQUENCY.svg")
    GENERATED_IMAGES.append("FILTER_CP_PERFORMANCE.svg")
    if DELETE_VARIABLES:
        del dataframe_cp_fa
    dd = time.time()
    print("filtering on case performance and generating process schema=", (dd - cc))

    if ENABLE_ATTRIBUTE_FILTER:
        parameters_att = {constants.PARAMETER_CONSTANT_CASEID_KEY: CASEID_GLUE,
                          constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: ATTRIBUTE_TO_FILTER,
                          constants.PARAMETER_CONSTANT_ACTIVITY_KEY: ATTRIBUTE_TO_FILTER, "positive": True}
        dataframe_att = attributes_filter.apply(dataframe, ATTRIBUTE_VALUES_TO_FILTER, parameters=parameters_att)
        # dataframe_att = attributes_filter.apply_auto_filter(dataframe, parameters=parameters_att)
        print("all the activities in the log", attributes_filter.get_attribute_values(dataframe_att, ACTIVITY_KEY))
        dataframe_att_fa = attributes_filter.filter_df_keeping_spno_activities(dataframe_att,
                                                                               activity_key=ACTIVITY_KEY,
                                                                               max_no_activities=MAX_NO_ACTIVITIES)
        if DELETE_VARIABLES:
            del dataframe_att
        calculate_process_schema_from_df(dataframe_att_fa, "FILTER_ATT_FREQUENCY.svg", "FILTER_ATT_PERFORMANCE.svg")
        GENERATED_IMAGES.append("FILTER_ATT_FREQUENCY.svg")
        GENERATED_IMAGES.append("FILTER_ATT_PERFORMANCE.svg")
        if DELETE_VARIABLES:
            del dataframe_att_fa
        ee = time.time()
        print("filtering on attribute values and generating process schema=", (ee - dd))

    ee = time.time()
    parameters_sa = {constants.PARAMETER_CONSTANT_CASEID_KEY: CASEID_GLUE,
                     constants.PARAMETER_CONSTANT_ACTIVITY_KEY: ACTIVITY_KEY}
    parameters_ea = {constants.PARAMETER_CONSTANT_CASEID_KEY: CASEID_GLUE,
                     constants.PARAMETER_CONSTANT_ACTIVITY_KEY: ACTIVITY_KEY}
    start_act = start_activities_filter.get_start_activities(dataframe, parameters=parameters_sa)
    print("start activities in the log = ", start_act)
    end_act = end_activities_filter.get_end_activities(dataframe, parameters=parameters_ea)
    print("end activities in the log = ", end_act)
    ff = time.time()
    print("finding start and end activities along with their count", (ff - ee))

    if ENABLE_STARTACT_FILTER:
        dataframe_sa = start_activities_filter.apply(dataframe, STARTACT_TO_FILTER, parameters=parameters_sa)
        # dataframe_sa = start_activities_filter.apply_auto_filter(dataframe, parameters=parameters_sa)
        start_act = start_activities_filter.get_start_activities(dataframe_sa, parameters=parameters_sa)
        print("start activities in the filtered log = ", start_act)
        dataframe_sa_fa = attributes_filter.filter_df_keeping_spno_activities(dataframe_sa, activity_key=ACTIVITY_KEY,
                                                                              max_no_activities=MAX_NO_ACTIVITIES)
        if DELETE_VARIABLES:
            del dataframe_sa
        calculate_process_schema_from_df(dataframe_sa_fa, "FILTER_SA_FREQUENCY.svg", "FILTER_SA_PERFORMANCE.svg")
        GENERATED_IMAGES.append("FILTER_SA_FREQUENCY.svg")
        GENERATED_IMAGES.append("FILTER_SA_PERFORMANCE.svg")
        if DELETE_VARIABLES:
            del dataframe_sa_fa
    gg = time.time()
    if ENABLE_STARTACT_FILTER:
        print("filtering start activities time=", (gg - ff))

    if ENABLE_ENDACT_FILTER:
        dataframe_ea = end_activities_filter.apply(dataframe, ENDACT_TO_FILTER, parameters=parameters_ea)
        # dataframe_ea = end_activities_filter.apply_auto_filter(dataframe, parameters=parameters_ea)
        end_act = end_activities_filter.get_end_activities(dataframe_ea, parameters=parameters_ea)
        print("end activities in the filtered log = ", end_act)
        dataframe_ea_fa = attributes_filter.filter_df_keeping_spno_activities(dataframe_ea, activity_key=ACTIVITY_KEY,
                                                                              max_no_activities=MAX_NO_ACTIVITIES)
        if DELETE_VARIABLES:
            del dataframe_ea
        calculate_process_schema_from_df(dataframe_ea_fa, "FILTER_EA_FREQUENCY.svg", "FILTER_EA_PERFORMANCE.svg")
        GENERATED_IMAGES.append("FILTER_EA_FREQUENCY.svg")
        GENERATED_IMAGES.append("FILTER_EA_PERFORMANCE.svg")
        if DELETE_VARIABLES:
            del dataframe_ea_fa
    hh = time.time()
    if ENABLE_ENDACT_FILTER:
        print("filtering end activities time=", (hh - gg))

    if REMOVE_GENERATED_IMAGES:
        for image in GENERATED_IMAGES:
            os.remove(image)


if __name__ == '__main__':
    execute_script()
