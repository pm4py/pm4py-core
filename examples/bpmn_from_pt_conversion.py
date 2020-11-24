import os

from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_import
from pm4py.objects.bpmn.layout import layouter as bpmn_layouter
from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter


def execute_script():
    log_path = os.path.join(os.path.join("..", "tests", "input_data", "running-example.xes"))
    log = xes_import.apply(log_path)
    ptree = inductive_miner.apply_tree(log)
    bpmn = pt_converter.apply(ptree, variant=pt_converter.Variants.TO_BPMN)
    #bpmn = bpmn_layouter.apply(bpmn)
    bpmn_exporter.apply(bpmn, "stru.bpmn")
    os.remove("stru.bpmn")


if __name__ == "__main__":
    execute_script()
