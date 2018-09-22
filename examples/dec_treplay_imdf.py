import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pm4py
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.petrinet import factory as pn_vis_factory

def execute_script():
    # import the log
    logPath = os.path.join("..", "tests", "inputData", "receipt.xes")
    log = xes_importer.import_log(logPath)
    # apply Inductive Miner
    net, initial_marking, final_marking = inductive_miner.apply(log)
    # get visualization
    variant = "performance"
    parameters_viz = {"aggregationMeasure":"mean"}
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, log=log, variant=variant, parameters=parameters_viz)
    gviz.view()

if __name__ == "__main__":
    execute_script()