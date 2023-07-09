#import pandas as pd
import pm4py

file1 = 'tests/input_data/running-example.xes'
file2 = 'tests/input_data/reviewing.xes'
file3 = 'tests/input_data/roadtraffic50traces.xes'
file4 = "tests/input_data/roadtraffic100traces.xes"
file5 = "tests/input_data/interval_event_log.xes"

log = pm4py.read_xes(file5)
dfg, start_act, end_act = pm4py.discover_dfg_typed(log) 
dfg_time = pm4py.discover_timeline_dfg(log)
pm4py.view_timeline_dfg(dfg, start_act, end_act, dfg_time)






