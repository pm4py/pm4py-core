import os

from sklearn import tree

from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.util import get_log_representation, get_class_representation
from pm4py.visualization.decisiontree import factory as dt_vis_factory


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "roadtraffic50traces.xes")
    # log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.import_log(log_path)
    # gets a log representation by including the concept:name event attribute (string) and the amount event attribute
    # (float)
    # data, feature_names = get_log_representation.get_representation(log, [], ["concept:name"], [], ["amount"])
    # now, it is possible to get a default representation of an event log
    data, feature_names = get_log_representation.get_default_representation(log)
    # gets classes representation by final concept:name value (end activity)
    target, classes = get_class_representation.get_class_representation_by_str_ev_attr_value_value(log, "concept:name")
    # mine the decision tree given 'data' and 'target'
    clf = tree.DecisionTreeClassifier(max_depth=7)
    clf.fit(data, target)
    # visualize the decision tree
    gviz = dt_vis_factory.apply(clf, feature_names, classes, parameters={"format": "svg"})
    dt_vis_factory.view(gviz)

    # gets classes representation by trace duration (threshold between the two classes = 200D)
    target, classes = get_class_representation.get_class_representation_by_trace_duration(log, 2 * 8640000)
    # mine the decision tree given 'data' and 'target'
    clf = tree.DecisionTreeClassifier(max_depth=7)
    clf.fit(data, target)
    # visualize the decision tree
    gviz = dt_vis_factory.apply(clf, feature_names, classes, parameters={"format": "svg"})
    dt_vis_factory.view(gviz)


if __name__ == "__main__":
    execute_script()
