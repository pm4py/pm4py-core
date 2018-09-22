import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pm4py
from pm4py.algo.discovery.inductive.versions import dfg_only
from pm4py.evaluation import factory as evaluation_factory
from pm4py.entities.log.importer.xes import factory as xes_importer

def execute_script():
    log = xes_importer.import_log(os.path.join("..","tests","inputData","reviewing.xes"))
    net, marking, final_marking = dfg_only.apply(log, None)
    metrics = evaluation_factory.apply(log, net, marking, final_marking)
    print("metrics=",metrics)

if __name__ == "__main__":
    execute_script()