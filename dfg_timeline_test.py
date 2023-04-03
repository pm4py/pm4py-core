#import pandas as pd
import pm4py

file1 = "C:/Users/harleenkaur/Documents/thesis/event logs/Artificial - Loan Process.xes"
file2 = 'tests/input_data/running-example.xes'


log = pm4py.read_xes(file2)

dfg, time_dic = pm4py.discover_timeline_dfg(log)
print(f" {dfg}\n\n{time_dic}" )
