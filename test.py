from builtins import sorted
import functools
from pm4py.log import instance as log_instance
from pm4py.log.importer import xes as xes_importer
from pm4py.log import transform as log_transform
import time

event = log_instance.Event({'concept:name': 'a'})
event['test'] = 'test'

# csv
'''
start = time.time()
log = csv_importer.CSVImporter.import_from_path('C:/Users/bas/Documents/tue/svn/private/logs/road_traffic.csv')
print(time.time() - start)
print(len(log))
start = time.time()
log2 = log_instance.EventLog(log.attributes, filter(lambda e: e['amount'] > 50.0, log))
print(time.time() - start)
print(len(log2))
'''


def compare_time_of_first_event(t1, t2):
    return (t1[0]['time:timestamp'] - t2[0]['time:timestamp']).microseconds


# xes
start = time.time()
log = xes_importer.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/BPI_Challenge_2017.xes')
print('time to import the log: %s' % (time.time() - start))

start = time.time()
log = log_instance.TraceLog(log.attributes, sorted(log, key=functools.cmp_to_key(compare_time_of_first_event)))
print('time to sort the log: %s' % (time.time() - start))

start = time.time()
log = log_transform.transform_trace_log_to_event_log(log)
print(log[0])
log = log_instance.EventLog(log.attributes, sorted(log, key=lambda e: e['time:timestamp'], reverse=True))
print(log[0])
print('time to transform the log: %s' % (time.time() - start))

start = time.time()
log = log_transform.transform_event_log_to_trace_log(log)
print('time to transform the log: %s' % (time.time() - start))
