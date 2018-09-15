import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.log.importer import xes_importer as xes_importer
from pm4py.algo.inductive.versions import dfg_only
from pm4py.models import petri
from pm4py.evaluation import factory as evaluation_factory

if __name__ == "__main__":
    log = xes_importer.import_from_file_xes('..\\tests\\inputData\\reviewing.xes')
    net, marking, final_marking = dfg_only.apply(log, None)
    metrics = evaluation_factory.apply(log, net, marking, final_marking)
    print("metrics=",metrics)