import os
import unittest

from pm4py.algo.other.decisiontree import get_class_representation
from pm4py.algo.other.decisiontree import get_log_representation
from pm4py.algo.other.decisiontree import mine_decision_tree
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.decisiontree import factory as dt_vis_factory
from pm4py.algo.other.clustering import factory as clusterer


class DecisionTreeTest(unittest.TestCase):
    def test_decisiontree_evattrvalue(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "roadtraffic50traces.xes")
        log = xes_importer.import_log(log_path)
        data, feature_names = get_log_representation.get_representation(log, [], ["concept:name"], [], ["amount"])
        target, classes = get_class_representation.get_class_representation_by_str_ev_attr_value_value(log,
                                                                                                       "concept:name")
        clf = mine_decision_tree.mine(data, target)
        gviz = dt_vis_factory.apply(clf, feature_names, classes, parameters={"format": "svg"})

    def test_decisiontree_traceduration(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "roadtraffic50traces.xes")
        log = xes_importer.import_log(log_path)
        data, feature_names = get_log_representation.get_representation(log, [], ["concept:name"], [], ["amount"])
        target, classes = get_class_representation.get_class_representation_by_trace_duration(log, 2 * 8640000)
        clf = mine_decision_tree.mine(data, target)
        gviz = dt_vis_factory.apply(clf, feature_names, classes, parameters={"format": "svg"})

    def test_clustering(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "roadtraffic50traces.xes")
        log = xes_importer.import_log(log_path)
        clusters = clusterer.apply(log)


if __name__ == "__main__":
    unittest.main()