import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer.csv.versions import pandas_df_imp
from pm4py.log.importer.utils import df_statistics
import time
from pm4py.algo.inductive import factory as inductive_factory
from pm4py.models.petri import visualize as pn_viz
from pm4py.visualization.dfg import factory as dfg_vis_factory

time1 = time.time()
inputLog = "..\\tests\\inputData\\running-example.csv"
#inputLog = "C:\\road_traffic.csv"
dataframe = pandas_df_imp.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
time2 = time.time()
print("time2 - time1: "+str(time2-time1))
#dataframe = df_filtering.filter_df_on_activities(dataframe, activity_key="concept:name", max_no_activities=25)
time3 = time.time()
print("time3 - time2: "+str(time3-time2))
#dataframe = df_filtering.filter_df_on_ncases(dataframe, case_id_glue="case:concept:name", max_no_cases=1000)
time4 = time.time()
print("time4 - time3: "+str(time4-time3))
#dataframe = df_filtering.filter_df_on_case_length(dataframe, case_id_glue="case:concept:name", min_trace_length=3, max_trace_length=50)
print(dataframe)
time5 = time.time()
print("time5 - time4: "+str(time5-time4))
dataframe = pandas_df_imp.convert_timestamp_columns_in_df(dataframe)
time6 = time.time()
print("time6 - time5: "+str(time6-time5))
#dataframe = dataframe.sort_values('time:timestamp')
time7 = time.time()
print("time7 - time6: "+str(time7-time6))

# show the filtered dataframe on the screen
activities_count = df_statistics.get_activities_count(dataframe)
[dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both")
#activities_count = df_statistics.get_activities_count(dataframe, activity_key="event")
#[dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both", case_id_glue="case", activity_key="event", timestamp_key="startTime")
time8 = time.time()
print("time8 - time7: "+str(time8-time7))
gviz = dfg_vis_factory.apply(dfg_frequency, activities_count=activities_count)
gviz.view()
net, initial_marking, final_marking = inductive_factory.apply_dfg(dfg_frequency)
gviz = pn_viz.graphviz_visualization(net, initial_marking=initial_marking, final_marking=final_marking, debug=True)
gviz.view()
time9 = time.time()
print("time9 - time8: "+str(time9-time8))
print("time9 - time1: "+str(time9-time1))