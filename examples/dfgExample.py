import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.algo.dfg import factory as dfg_factory, visualize as dfg_visualize, replacement as dfg_replacement
from pm4py.log.importer import xes as xes_importer
from pm4py.log.util import auto_filter, activities

# measure could be frequency or performance
measure = "frequency"
log = xes_importer.import_from_file_xes('..\\tests\\inputData\\running-example.xes')
filtered_log = auto_filter.apply_auto_filter(log)
filtered_log_activities_count = activities.get_activities_from_log(filtered_log)
intermediate_log = activities.filter_log_by_specified_activities(log, list(filtered_log_activities_count.keys()))
activities_count = activities.get_activities_from_log(intermediate_log)
dfg_filtered_log = dfg_factory.apply(filtered_log, variant=measure)
dfg_intermediate_log = dfg_factory.apply(intermediate_log, variant=measure)
dfg_filtered_log = dfg_replacement.replace_values(dfg_filtered_log, dfg_intermediate_log)
gviz = dfg_visualize.graphviz_visualization(activities_count, dfg_filtered_log, measure=measure)
gviz.view()
base64 = dfg_visualize.return_diagram_as_base64(activities_count, dfg_filtered_log, measure=measure)
#print(base64)