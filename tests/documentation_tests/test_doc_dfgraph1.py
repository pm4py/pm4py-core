import os
import unittest


class DfGraphDocumentationTest(unittest.TestCase):
    def test_dfdoc1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        from pm4py.objects.log.importer.xes import factory as xes_importer
        log = xes_importer.import_log(os.path.join("input_data", "running-example.xes"))
        from pm4py.algo.discovery.dfg import factory as dfg_factory
        dfg = dfg_factory.apply(log)
        from pm4py.algo.filtering.log.attributes import attributes_filter
        activities_count = attributes_filter.get_attribute_values(log, "concept:name")

        from pm4py.visualization.dfg.versions import simple_visualize as dfg_visualize
        gviz = dfg_visualize.graphviz_visualization(activities_count, dfg)
        del gviz


if __name__ == "__main__":
    unittest.main()
