import os

from pm4py.algo.other.conceptdrift import factory as concept_drift_factory
from pm4py.algo.other.conceptdrift.utils import get_representation
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.decisiontree import factory as dec_tree_visualization


def execute_script():
    # read the event log
    log_path = os.path.join("..", "tests", "input_data", "receipt.xes")

    log = xes_importer.apply(log_path)

    # find the concept drift points, if there is any
    drift_found, logs_list, endpoints, change_date_repr = concept_drift_factory.apply(log)

    if drift_found:
        # if the concept drift has been found

        # find the decision tree that permits to understand which differences were there
        clf, feature_names, classes = get_representation.get_decision_tree(logs_list[0], logs_list[1])

        # represent the decision tree
        gviz = dec_tree_visualization.apply(clf, feature_names, classes, parameters={"format": "svg"})
        dec_tree_visualization.view(gviz)


if __name__ == "__main__":
    execute_script()
