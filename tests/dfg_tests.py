import unittest

import pm4py


class DfgTests(unittest.TestCase):
    def test_filter_act_percentage(self):
        from pm4py.algo.filtering.dfg import dfg_filtering
        log = pm4py.read_xes("input_data/running-example.xes")
        dfg, sa, ea = pm4py.discover_dfg(log)
        act_count = pm4py.get_event_attribute_values(log, "concept:name")
        dfg_filtering.filter_dfg_on_activities_percentage(dfg, sa, ea, act_count, 0.1)

    def test_filter_paths_percentage(self):
        from pm4py.algo.filtering.dfg import dfg_filtering
        log = pm4py.read_xes("input_data/running-example.xes")
        dfg, sa, ea = pm4py.discover_dfg(log)
        act_count = pm4py.get_event_attribute_values(log, "concept:name")
        dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, act_count, 0.3)


if __name__ == "__main__":
    unittest.main()
