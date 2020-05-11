from pm4py.objects.log.importer.xes import factory as xes_import_factory

import inspect
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

if __name__ == '__main__':
    log_path = os.path.join("..", "..", "tests", "input_data", "running-example.xes")
    log = xes_import_factory.apply(log_path)

    for case_index, case in enumerate(log):
        print("\n case index: %d  case id: %s" % (case_index, case.attributes["concept:name"]))
        for event_index, event in enumerate(case):
            print("event index: %d  event activity: %s" % (event_index, event["concept:name"]))

    parameters = {"timestamp_sort": True}

    log = xes_import_factory.apply(log_path, variant="nonstandard", parameters=parameters)

    for case_index, case in enumerate(log):
        print("\n case index: %d  case id: %s" % (case_index, case.attributes["concept:name"]))
        for event_index, event in enumerate(case):
            print("event index: %d  event activity: %s" % (event_index, event["concept:name"]))
