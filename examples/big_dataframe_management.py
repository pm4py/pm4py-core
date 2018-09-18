import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.algo.dfg.adapters.pandas import df_statistics
import time
from pm4py.algo.inductive import factory as inductive_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.dfg import factory as dfg_vis_factory
from pm4py.log.adapters.pandas import csv_import_adapter as csv_import_adapter
from pm4py.filtering.pandas import df_filtering
from pm4py.models.petri import vis_trans_shortest_paths

time1 = time.time()
inputLog = os.path.join("..", "tests", "inputData", "running-example.csv")
#inputLog = "C:\\road_traffic.csv"
dataframe = csv_import_adapter.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
time2 = time.time()
print("time2 - time1: "+str(time2-time1))
dataframe = df_filtering.filter_df_on_activities(dataframe, activity_key="concept:name", max_no_activities=25)
time3 = time.time()
print("time3 - time2: "+str(time3-time2))
dataframe = df_filtering.filter_df_on_ncases(dataframe, case_id_glue="case:concept:name", max_no_cases=1000)
time4 = time.time()
dataframe = csv_import_adapter.convert_timestamp_columns_in_df(dataframe)
time6 = time.time()
print("time6 - time4: "+str(time6-time4))
#dataframe = dataframe.sort_values('time:timestamp')
time7 = time.time()
print("time7 - time6: "+str(time7-time6))

# show the filtered dataframe on the screen
activities_count = df_statistics.get_activities_count(dataframe)
[dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both", perf_aggregation_key="median")
time8 = time.time()
print("time8 - time7: "+str(time8-time7))
gviz = dfg_vis_factory.apply(dfg_frequency, activities_count=activities_count)
gviz.view()
net, initial_marking, final_marking = inductive_factory.apply_dfg(dfg_frequency)
spaths = vis_trans_shortest_paths.get_shortest_paths(net)
time9 = time.time()
print("time9 - time8: "+str(time9-time8))
aggregated_statistics = vis_trans_shortest_paths.get_net_decorations_from_dfg_spaths_acticount(net, dfg_performance, spaths, activities_count, variant="performance")
gviz = pn_vis_factory.apply(net, initial_marking, final_marking, variant="performance", aggregated_statistics=aggregated_statistics)
time10 = time.time()
print("time10 - time9: "+str(time10-time9))
print("time10 - time1: "+str(time10-time1))
gviz.view()