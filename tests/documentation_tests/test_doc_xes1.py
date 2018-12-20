import unittest


class XES1DocumentationTest(unittest.TestCase):
    def test_xes1documentation(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        import os
        from pm4py.objects.log.importer.xes import factory as xes_importer
        log = xes_importer.import_log(os.path.join("input_data", "running-example.xes"))
        log_lenth = len(log)
        first_trace_length = len(log[0])
        del log_lenth
        del first_trace_length
        first_trace_attributes = list(log[0].attributes.keys())
        first_event_first_trace_attributes = list(log[0][0].keys())
        del first_trace_attributes
        del first_event_first_trace_attributes
        first_trace_concept_name = log[0].attributes["concept:name"]
        first_event_first_trace_concept_name = log[0][0]["concept:name"]
        del first_trace_concept_name
        del first_event_first_trace_concept_name
        from pm4py.objects.log.exporter.xes import factory as xes_exporter
        xes_exporter.export_log(log, "exportedLog.xes")
        os.remove("exportedLog.xes")


if __name__ == "__main__":
    unittest.main()
