import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import pm4py
from pm4py.algo.other.petrigenerator.versions import simple_generator as petri_generator
from pm4py.algo.other.playout import factory as playout_factory
from pm4py.algo.conformance.tokenreplay import factory as token_replay

def execute_script():
    net, marking, final_marking = petri_generator.generate_petri()
    #petri_exporter.export_petri_to_pnml(net, marking, "generatedNet.pnml")
    log = playout_factory.apply(net, marking)
    aligned_traces = token_replay.apply(log, net, marking, final_marking)
    print(aligned_traces)

if __name__ == "__main__":
    execute_script()