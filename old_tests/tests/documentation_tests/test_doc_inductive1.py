import os
import unittest


class InductiveMinerDocumentationTest(unittest.TestCase):
    def test_inductivedoc1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        from pm4py.objects.log.importer.xes import factory as xes_importer
        log = xes_importer.import_log(os.path.join("input_data", "running-example.xes"))

        from pm4py.algo.discovery.inductive import factory as inductive_miner
        net, initial_marking, final_marking = inductive_miner.apply(log)
        from pm4py.visualization.petrinet.common import visualize as pn_viz
        gviz = pn_viz.graphviz_visualization(net, initial_marking=initial_marking, final_marking=final_marking)
        del gviz


if __name__ == "__main__":
    unittest.main()
