from pm4py.log import instance as log_instance
from pm4py.log.importer import csv as csv_importer
from pm4py.log.importer import xes as xes_importer
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

#xes
start = time.time()
xes_importer.import_from_path_xes('C:/Users/bas/Documents/tue/svn/private/logs/road_traffic.xes')
print(time.time()-start)

