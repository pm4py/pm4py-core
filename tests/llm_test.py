import unittest
import pm4py


class LlmTest(unittest.TestCase):
    def test_abstract_case(self):
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        abstr = pm4py.llm.abstract_case(log[0])
        self.assertGreater(len(abstr), 0)

    def test_abstract_dfg(self):
        for ret_legacy in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=ret_legacy)
            abstr = pm4py.llm.abstract_dfg(log)
            self.assertGreater(len(abstr), 0)

    def test_abstract_variants(self):
        for ret_legacy in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=ret_legacy)
            abstr = pm4py.llm.abstract_variants(log)
            self.assertGreater(len(abstr), 0)

    def test_abstract_event_stream(self):
        for ret_legacy in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=ret_legacy)
            abstr = pm4py.llm.abstract_event_stream(log)
            self.assertGreater(len(abstr), 0)

    def test_abstract_log_attributes(self):
        for ret_legacy in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=ret_legacy)
            abstr = pm4py.llm.abstract_log_attributes(log)
            self.assertGreater(len(abstr), 0)

    def test_abstract_log_features(self):
        for ret_legacy in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=ret_legacy)
            abstr = pm4py.llm.abstract_log_features(log)
            self.assertGreater(len(abstr), 0)

    def test_abstract_temporal_profile(self):
        for ret_legacy in [True, False]:
            log = pm4py.read_xes("input_data/receipt.xes", return_legacy_log_object=ret_legacy)
            temporal_profile = pm4py.discover_temporal_profile(log)
            abstr = pm4py.llm.abstract_temporal_profile(temporal_profile)
            self.assertGreater(len(abstr), 0)

    def test_abstract_declare(self):
        for ret_legacy in [True, False]:
            log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=ret_legacy)
            declare_model = pm4py.discover_declare(log)
            abstr = pm4py.llm.abstract_declare(declare_model)
            self.assertGreater(len(abstr), 0)

    def test_abstract_log_skeleton(self):
        for ret_legacy in [True, False]:
            log = pm4py.read_xes("input_data/receipt.xes", return_legacy_log_object=ret_legacy)
            log_skeleton = pm4py.discover_log_skeleton(log)
            abstr = pm4py.llm.abstract_log_skeleton(log_skeleton)
            self.assertGreater(len(abstr), 0)

    def test_abstract_ocel(self):
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        abstr = pm4py.llm.abstract_ocel(ocel)
        self.assertGreater(len(abstr), 0)

    def test_abstract_ocel_ocdfg(self):
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        abstr = pm4py.llm.abstract_ocel_ocdfg(ocel)
        self.assertGreater(len(abstr), 0)

    def test_abstract_ocel_features(self):
        ocel = pm4py.read_ocel("input_data/ocel/example_log.jsonocel")
        abstr = pm4py.llm.abstract_ocel_features(ocel, "order")
        self.assertGreater(len(abstr), 0)

    def test_abstract_petri_net(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        abstr = pm4py.llm.abstract_petri_net(net, im, fm)
        self.assertGreater(len(abstr), 0)


if __name__ == "__main__":
    unittest.main()
