from pm4py.log import instance as log_instance
from pm4py.log.importer import csv as csv_importer
import time

e1 = log_instance.Event({'concept:name': 'a', 'trace:concept:name': 't1'})
e2 = log_instance.Event({'concept:name': 'b', 'trace:concept:name': 't1'})
e3 = log_instance.Event({'concept:name': 'c', 'trace:concept:name': 't1'})
t1 = log_instance.Trace({'concept:name': 't1'}, [e1, e2, e3])


t2 = log_instance.Trace(t1.attributes, filter(lambda event: event['concept:name'] in {'a', 'b'}, t1))
t3 = log_instance.Trace(t1.attributes, filter(lambda event: event['concept:name'] in {'c'}, t1))
log = log_instance.TraceLog({'concept:name': ''})

for key, value in e1.items():
    print(key, value)

log = log_instance.EventLog([e1, e2, e3])
print(log)
log = log_instance.EventLog(filter(lambda e: 'concept:name' in e, log))
print(log)

for event in log:
    print(event)

start = time.time()
importer = csv_importer.CSVImporter()
log = importer.import_from_file('C:/Users/bas/Documents/tue/svn/private/logs/road_traffic.csv', ',', False)
print(time.time() - start)
print(len(log))
start = time.time()
log2 = log_instance.EventLog(log.attributes, filter(lambda e: float(e['amount']) > 50.0, log))
print(time.time() - start)
print(len(log2))

