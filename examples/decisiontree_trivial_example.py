import os

from sklearn import tree

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import get_class_representation
from pm4py.algo.transformation.log_to_features import algorithm as log_to_features
from pm4py.visualization.decisiontree import visualizer as dt_vis


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "roadtraffic50traces.xes")
    # log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.apply(log_path)
    # now, it is possible to get a default representation of an event log
    data, feature_names = log_to_features.apply(log, variant=log_to_features.Variants.TRACE_BASED)
    # gets classes representation by final concept:name value (end activity)
    target, classes = get_class_representation.get_class_representation_by_str_ev_attr_value_value(log, "concept:name")
    # mine the decision tree given 'data' and 'target'
    clf = tree.DecisionTreeClassifier(max_depth=7)
    clf.fit(data, target)
    # visualize the decision tree
    gviz = dt_vis.apply(clf, feature_names, classes, parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
    dt_vis.view(gviz)

    # gets classes representation by trace duration (threshold between the two classes = 200D)
    target, classes = get_class_representation.get_class_representation_by_trace_duration(log, 2 * 8640000)
    # mine the decision tree given 'data' and 'target'
    clf = tree.DecisionTreeClassifier(max_depth=7)
    clf.fit(data, target)
    # visualize the decision tree
    gviz = dt_vis.apply(clf, feature_names, classes, parameters={dt_vis.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
    dt_vis.view(gviz)


if __name__ == "__main__":
    execute_script()
