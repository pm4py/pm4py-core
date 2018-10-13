from pm4py.algo.discovery.inductive.versions.dfg import dfg_only
from pm4py.evaluation import factory as evaluation_factory
from pm4py.objects.log.importer.xes import factory as xes_importer
import os

def execute_script():
    log = xes_importer.import_log(os.path.join("..", "tests", "input_data", "reviewing.xes"))
    net, marking, final_marking = dfg_only.apply(log, None)
    metrics = evaluation_factory.apply(log, net, marking, final_marking)
    print("metrics=", metrics)


if __name__ == "__main__":
    execute_script()
