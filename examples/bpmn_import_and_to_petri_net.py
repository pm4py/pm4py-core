import os

import pm4py
from pm4py.objects.bpmn.importer import importer as bpmn_importer
from pm4py.objects.conversion.bpmn import converter as bpmn_converter


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    bpmn_graph = bpmn_importer.apply(os.path.join("..", "tests", "input_data", "running-example.bpmn"))
    net, im, fm = bpmn_converter.apply(bpmn_graph, variant=bpmn_converter.Variants.TO_PETRI_NET)
    precision_tbr = pm4py.precision_token_based_replay(log, net, im, fm)
    print("precision", precision_tbr)
    fitness_tbr = pm4py.precision_token_based_replay(log, net, im, fm)
    print("fitness", fitness_tbr)
    print(pm4py.check_soundness(net, im, fm))


if __name__ == "__main__":
    execute_script()
