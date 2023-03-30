#import pandas as pd
import pm4py

def println():
    print()

file1 = "C:/Users/harleenkaur/Documents/thesis/event logs/Artificial - Loan Process.xes"
log = pm4py.read_xes(file1)
#dfg, start_activities, end_activities = pm4py.discover_dfg_typed(log)  
#pm4py.view_dfg(dfg, start_activities, end_activities)  

mydfg = pm4py.discover_timeline_dfg(log)

