from pm4py.log import instance as log_instance
from pm4py.log.importer import csv as csv_importer
import time

e1 = log_instance.Event({'concept:name': 'b', 'trace:concept:name': 't1'})
e2 = log_instance.Event({'concept:name': 'b', 'trace:concept:name': 't1'})
e3 = log_instance.Event({'concept_name': 'b', 'trace:concept:name': 't1'})

for key, value in e1.items():
    print(key, value)

log = log_instance.EventLog([e1, e2, e3])
log.it_is_me_mario()
print(log)
log = log_instance.EventLog(filter(lambda e: 'concept:name' in e, log))
log.it_is_me_mario()
print(log)

for event in log:
    print(event)

start = time.time()
log = csv_importer.import_from_file('C:/Users/bas/Documents/tue/svn/private/logs/road_traffic.csv')
print(time.time() - start)

print(log)

