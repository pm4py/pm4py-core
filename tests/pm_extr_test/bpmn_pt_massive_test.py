import os

import pm4py
from pm4py.objects.process_tree.utils import generic
from pm4py.objects.bpmn.layout import layouter
from pm4py.objects.bpmn.exporter import exporter
from pm4py.objects.bpmn.importer import importer
import tempfile

LOGS_FOLDER = "../compressed_input_data"

for log_name in os.listdir(LOGS_FOLDER):
    if "xes" in log_name:
        bpmn_output_path = tempfile.NamedTemporaryFile(suffix=".bpmn")
        bpmn_output_path.close()
        bpmn_output_path = bpmn_output_path.name
        log_path = os.path.join(LOGS_FOLDER, log_name)
        print("")
        print(log_path)
        log = pm4py.read_xes(log_path)
        fp_log = pm4py.algo.discovery.footprints.log.variants.entire_event_log.apply(log)
        tree = pm4py.discover_process_tree_inductive(log)
        generic.tree_sort(tree)
        fp_tree = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(tree)
        fp_conf = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree)
        fitness0 = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree, fp_conf)
        precision0 = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree)
        print("fitness 0 = ", fitness0)
        print("precision 0 = ", precision0)
        bpmn_graph = pm4py.objects.conversion.process_tree.variants.to_bpmn.apply(tree)
        bpmn_graph = layouter.apply(bpmn_graph)
        exporter.apply(bpmn_graph, bpmn_output_path)
        bpmn_graph = importer.apply(bpmn_output_path)
        bpmn_graph = layouter.apply(bpmn_graph)
        # gets the tree back
        net, im, fm = pm4py.objects.conversion.bpmn.variants.to_petri_net.apply(bpmn_graph)
        new_tree = pm4py.objects.conversion.wf_net.variants.to_process_tree.apply(net, im, fm)
        generic.tree_sort(new_tree)
        print(tree)
        print(new_tree)
        print("are the tree equal?", tree == new_tree)
        fp_tree = pm4py.algo.discovery.footprints.tree.variants.bottomup.apply(new_tree)
        fp_conf = pm4py.algo.conformance.footprints.variants.log_extensive.apply(fp_log, fp_tree)
        fitness1 = pm4py.algo.conformance.footprints.util.evaluation.fp_fitness(fp_log, fp_tree, fp_conf)
        precision1 = pm4py.algo.conformance.footprints.util.evaluation.fp_precision(fp_log, fp_tree)
        print("fitness 1 = ", fitness1, fitness0 == fitness1)
        print("precision 1 = ", precision1, precision0 == precision1)
        if not (fitness0 == fitness1 and precision0 == precision1 and tree == new_tree):
            print("ALERT")
            input()
