import os
import unittest

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import  get_class_representation
from pm4py.algo.transformation.log_to_features import algorithm as log_to_features


class DecisionTreeTest(unittest.TestCase):
    def test_decisiontree_evattrvalue(self):
        from sklearn import tree
        from pm4py.visualization.decisiontree import visualizer as dt_vis

        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "roadtraffic50traces.xes")
        log = xes_importer.apply(log_path)
        data, feature_names = log_to_features.apply(log, variant=log_to_features.Variants.TRACE_BASED,
                                                    parameters={"str_tr_attr": [], "str_ev_attr": ["concept:name"],
                                                                "num_tr_attr": [], "num_ev_attr": ["amount"]})
        target, classes = get_class_representation.get_class_representation_by_str_ev_attr_value_value(log,
                                                                                                       "concept:name")
        clf = tree.DecisionTreeClassifier(max_depth=7)
        clf.fit(data, target)
        gviz = dt_vis.apply(clf, feature_names, classes,
                            parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
        del gviz

    def test_decisiontree_traceduration(self):
        from sklearn import tree
        from pm4py.visualization.decisiontree import visualizer as dt_vis

        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log_path = os.path.join("input_data", "roadtraffic50traces.xes")
        log = xes_importer.apply(log_path)
        data, feature_names = log_to_features.apply(log, variant=log_to_features.Variants.TRACE_BASED,
                                                    parameters={"str_tr_attr": [], "str_ev_attr": ["concept:name"],
                                                                "num_tr_attr": [], "num_ev_attr": ["amount"]})
        target, classes = get_class_representation.get_class_representation_by_trace_duration(log, 2 * 8640000)
        clf = tree.DecisionTreeClassifier(max_depth=7)
        clf.fit(data, target)
        gviz = dt_vis.apply(clf, feature_names, classes,
                            parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
        del gviz


if __name__ == "__main__":
    unittest.main()
