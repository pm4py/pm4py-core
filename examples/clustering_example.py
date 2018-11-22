import os

from pm4py.algo.other.clustering import factory as clusterer
from pm4py.objects.log.importer.xes import factory as xes_importer


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "roadtraffic50traces.xes")
    log = xes_importer.apply(log_path)
    clusters = clusterer.apply(log)
    for cluster in clusters:
        print("\n\n\n")
        for trace in cluster:
            print(" ".join([x["concept:name"] for x in trace]))


if __name__ == "__main__":
    execute_script()