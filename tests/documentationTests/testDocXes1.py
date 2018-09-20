import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir2)


class XES1DocumentationTest(unittest.TestCase):
    def test_xes1documentation(self):
        import os

        from pm4py.entities.log.importer.xes import factory as xes_importer

        log = xes_importer.import_log("inputData\\running-example.xes")

        log_lenth = len(log)
        first_trace_length = len(log[0])
        # print(log_lenth,first_trace_length)

        first_trace_attributes = list(log[0].attributes.keys())
        first_event_first_trace_attributes = list(log[0][0].keys())
        # print(first_trace_attributes, first_event_first_trace_attributes)

        first_trace_concept_name = log[0].attributes["concept:name"]
        first_event_first_trace_concept_name = log[0][0]["concept:name"]

        for case_index, case in enumerate(log):
            # print("\n case index: %d  case id: %s" % (case_index, case.attributes["concept:name"]))
            pass
            for event_index, event in enumerate(case):
                # print("event index: %d  event activity: %s" % (event_index, event["concept:name"]))
                pass

        from pm4py.entities.log.exporter.xes import factory as xes_exporter

        xes_exporter.export_log(log, "exportedLog.xes")
        os.remove("exportedLog.xes")


if __name__ == "__main__":
    unittest.main()
