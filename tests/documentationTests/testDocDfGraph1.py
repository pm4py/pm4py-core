import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir2 = os.path.dirname(parentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, parentdir2)


class DfGraphDocumentationTest(unittest.TestCase):
    def test_dfdoc1(self):
        from pm4py.entities.log.importer.xes import factory as xes_importer
        log = xes_importer.import_log(os.path.join("inputData","running-example.xes"))
        from pm4py.algo.discovery.dfg import factory as dfg_factory
        dfg = dfg_factory.apply(log)
        from pm4py.algo.filtering.tracelog.attributes import attributes_filter
        activities_count = attributes_filter.get_attributes_from_log(log, "concept:name")

        from pm4py.visualization.dfg.versions import simple_visualize as dfg_visualize
        gviz = dfg_visualize.graphviz_visualization(activities_count, dfg)
        #dfg = dfg_factory.apply(log, variant="performance")
        #gviz = dfg_visualize.graphviz_visualization(activities_count, dfg, measure="performance")

if __name__ == "__main__":
    unittest.main()
