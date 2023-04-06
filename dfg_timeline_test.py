#import pandas as pd
import pm4py

file1 = "C:/Users/harleenkaur/Documents/thesis/event logs/Artificial - Loan Process.xes"
file2 = 'tests/input_data/running-example.xes'
file3 = "C:/Users/harleenkaur/Downloads/1987a2a6-9f5b-4b14-8d26-ab7056b17929_1_all/BPI_Challenge_2013_closed_problems.xes.gz"
file4 = "C:/Users/harleenkaur/Downloads/6af6d5f0-f44c-49be-aac8-8eaa5fe4f6fd_1_all/Hospital Billing - Event Log.xes.gz"
file5 = "C:/Users/harleenkaur/Downloads/806acd1a-2bf2-4e39-be21-69b8cad10909_1_all/Road_Traffic_Fine_Management_Process.xes.gz"
file6 = 'tests/input_data/roadtraffic50traces.xes'

log = pm4py.read_xes(file3)
dfg, start_act, end_act = pm4py.discover_dfg_typed(log) 
dfg_time = pm4py.discover_timeline_dfg(log)

#v = pm4py.view_timeline_dfg(dfg, start_act, end_act, dfg_time)
