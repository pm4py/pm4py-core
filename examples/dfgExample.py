import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.algo.dfg import factory as dfg_factory, visualize as dfg_visualize
from pm4py.log.importer import xes as xes_importer
from pm4py.log.util import auto_filter, activities

log = xes_importer.import_from_file_xes('..\\tests\\inputData\\running-example.xes')
filtered_log = auto_filter.apply_auto_filter(log)
activities_count = activities.get_activities_from_log(log)
dfg = dfg_factory.apply(filtered_log)
gviz = dfg_visualize.graphviz_visualization(activities_count, dfg)
gviz.view()
base64 = dfg_visualize.return_diagram_as_base64(activities_count, dfg)
#print(base64)