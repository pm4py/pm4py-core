#import pandas as pd
import pm4py

file1 = "C:/Users/harleenkaur/Documents/thesis/event logs/Artificial - Loan Process.xes"
file2 = 'tests/input_data/running-example.xes'
file3 = "C:/Users/harleenkaur/Downloads/1987a2a6-9f5b-4b14-8d26-ab7056b17929_1_all/BPI_Challenge_2013_closed_problems.xes.gz"
file4 = 'tests/input_data/reviewing.xes'
#file5 = "C:/Users/harleenkaur/Downloads/806acd1a-2bf2-4e39-be21-69b8cad10909_1_all/Road_Traffic_Fine_Management_Process.xes.gz"
file6 = 'tests/input_data/roadtraffic50traces.xes'
file7 = "C:/Users/harleenkaur/Documents/thesis/event logs/Artificial - Small Process.xes"
file8 = "C:/Users/harleenkaur/Documents/thesis/event logs/Artificial - Loan Process - Partial.xes.gz"
file9 = "tests/input_data/roadtraffic100traces.xes"
file10 = "C:/Users/harleenkaur/Downloads/BPI_Challenge_2019.xes"
file11 = "C:/Users/harleenkaur/Downloads/InternationalDeclarations.xes.gz"
file12 = "tests/input_data/bpic2012.xes.gz"
file13 = "tests/input_data/interval_event_log.xes"
file14 = "C:/Users/harleenkaur/Downloads/34c3f44b-3101-4ea9-8281-e38905c68b8d_1_all/BPI Challenge 2017.xes.gz"

#File 3 and File 4 are important ones in debugging
log = pm4py.read_xes(file10)
#print(log[:20])

dfg, start_act, end_act = pm4py.discover_dfg_typed(log) 

print(dfg)

print("here are start activities: ",start_act)

dfg_time = pm4py.discover_timeline_dfg(log)
#print(dfg_time)

pm4py.view_dfg(dfg, start_act, end_act)
pm4py.view_timeline_dfg(dfg, start_act, end_act, dfg_time)






