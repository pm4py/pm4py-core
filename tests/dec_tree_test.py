import os
import unittest

from pm4py.objects.log.util import get_log_representation, get_class_representation
from pm4py.algo.other.decisiontree import mine_decision_tree
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.decisiontree import factory as dt_vis_factory
from pm4py.algo.other.clustering import factory as clusterer
from pm4py.algo.other.conceptdrift import factory as conc_drift_detection_factory
from pm4py.algo.other.conceptdrift.utils import get_representation


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
        del gviz

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
        del gviz

    def test_clustering(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "roadtraffic50traces.xes")
        log = xes_importer.import_log(log_path)
        clusters = clusterer.apply(log)
        del clusters

    def test_conceptdrift(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "receipt.xes")
        log = xes_importer.import_log(log_path)
        drift_found, logs_list, endpoints, change_date_repr = conc_drift_detection_factory.apply(log)
        clf, feature_names, classes = get_representation.get_decision_tree(logs_list[0], logs_list[1])
        del clf
        del feature_names
        del classes


if __name__ == "__main__":
    unittest.main()