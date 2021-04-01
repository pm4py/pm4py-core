import unittest
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter
from pm4py.objects.log.util import func
from pm4py.objects.log.obj import Trace
import os


class MapFilterFunctionsTest(unittest.TestCase):
    def new_trace(self, t):
        t2 = Trace()
        t2.append(t[0])
        return t2

    def add_underscore_to_resource(self, ev):
        ev["org:resource"] = ev["org:resource"] + "_"
        return ev

    def test_filter_stream(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        stream = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM)
        stream2 = func.filter_(lambda e: e["concept:name"] == "register request", stream)

    def test_filter_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        log2 = func.filter_(lambda x: len(x) > 5, log)

    def test_map_stream(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        stream = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM)
        stream2 = func.map_(lambda e: self.add_underscore_to_resource(e), stream)

    def test_map_log(self):
        log = xes_importer.apply(os.path.join("input_data", "running-example.xes"))
        log2 = func.map_(lambda x: self.new_trace(x), log)


if __name__ == "__main__":
    unittest.main()
