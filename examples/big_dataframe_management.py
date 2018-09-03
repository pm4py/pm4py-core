import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer import csv as csv_importer
from pm4py.log.importer.utils import df_filtering
from pm4py.log import transform
import time

time1 = time.time()
inputLog = "..\\tests\\inputData\\running-example.csv"
dataframe = csv_importer.import_dataframe_from_path_wo_timeconversion(inputLog, sep=',')
time2 = time.time()
print("time2 - time1: "+str(time2-time1))
dataframe = df_filtering.filter_df_on_activities(dataframe, activity_key="concept:name", max_no_activities=25)
time3 = time.time()
print("time3 - time2: "+str(time3-time2))
dataframe = df_filtering.filter_df_on_ncases(dataframe, case_id_glue="case:concept:name", max_no_cases=1000)
time4 = time.time()
print("time4 - time3: "+str(time4-time3))
dataframe = df_filtering.filter_df_on_case_length(dataframe, case_id_glue="case:concept:name", min_trace_length=3, max_trace_length=50)
print(dataframe)
time5 = time.time()
print("time5 - time4: "+str(time5-time4))
dataframe = csv_importer.convert_timestamp_columns_in_df(dataframe)
time6 = time.time()
print("time6 - time5: "+str(time6-time5))
dataframe = dataframe.sort_values('time:timestamp')
time_end = time.time()
print("time_end - time1: "+str(time_end-time1))
#eventLog = csv_importer.convert_dataframe_to_event_log(dataframe)
#traceLog = transform.transform_event_log_to_trace_log(eventLog)
#print(len(traceLog))