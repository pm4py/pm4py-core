import os

from pm4py.algo.other.decisiontree.applications import root_cause_part_duration
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.decisiontree import factory as dt_vis_factory


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "roadtraffic100traces.xes"))

    clf, feature_names, classes = root_cause_part_duration.perform_duration_root_cause_analysis(log, "Payment")

    gviz = dt_vis_factory.apply(clf, feature_names, classes, parameters={"format": "svg"})
    dt_vis_factory.view(gviz)


if __name__ == "__main__":
    execute_script()
