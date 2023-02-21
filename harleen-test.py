import pandas as pd
import pm4py
import os

log = pm4py.read_xes("C:/Users/harleenkaur/Documents/thesis/event logs/Artificial - Loan Process.xes")
print(f" Type of the file that is read : {type(log)}")

dfg, start_activities, end_activities = pm4py.discover_dfg_typed(log) 
pm4py.vis.view_dfg(dfg, start_activities, end_activities)  


#process_tree = pm4py.discover_process_tree_inductive(log, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
#pm4py.view_process_tree(process_tree, format='svg')


