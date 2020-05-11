import os
import unittest

from sklearn import tree

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import get_log_representation, get_class_representation
from pm4py.visualization.decisiontree import visualizer as dt_vis


class DecisionTreeTest(unittest.TestCase):
    def test_decisiontree_evattrvalue(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "roadtraffic50traces.xes")
        log = xes_importer.apply(log_path)
        data, feature_names = get_log_representation.get_representation(log, [], ["concept:name"], [], ["amount"])
        target, classes = get_class_representation.get_class_representation_by_str_ev_attr_value_value(log,
                                                                                                       "concept:name")
        clf = tree.DecisionTreeClassifier(max_depth=7)
        clf.fit(data, target)
        gviz = dt_vis.apply(clf, feature_names, classes,
                            parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
        del gviz

    def test_decisiontree_traceduration(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "roadtraffic50traces.xes")
        log = xes_importer.apply(log_path)
        data, feature_names = get_log_representation.get_representation(log, [], ["concept:name"], [], ["amount"])
        target, classes = get_class_representation.get_class_representation_by_trace_duration(log, 2 * 8640000)
        clf = tree.DecisionTreeClassifier(max_depth=7)
        clf.fit(data, target)
        gviz = dt_vis.apply(clf, feature_names, classes,
                            parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
        del gviz


if __name__ == "__main__":
    unittest.main()
