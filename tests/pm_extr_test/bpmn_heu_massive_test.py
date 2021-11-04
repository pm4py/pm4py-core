import os
import tempfile

import pm4py
from pm4py.objects.bpmn.exporter import exporter
from pm4py.objects.bpmn.importer import importer
from pm4py.objects.bpmn.layout import layouter
from pm4py.visualization.petri_net import visualizer as pn_visualizer

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
        net, im, fm = pm4py.discover_petri_net_heuristics(log)
        fitness0 = pm4py.evaluate_fitness_alignments(log, net, im, fm)
        precision0 = pm4py.evaluate_precision_alignments(log, net, im, fm)
        print("fitness 0", fitness0)
        print("precision 0", precision0)
        bpmn_graph = pm4py.objects.conversion.wf_net.variants.to_bpmn.apply(net, im, fm)
        bpmn_graph = layouter.apply(bpmn_graph)
        exporter.apply(bpmn_graph, bpmn_output_path)
        bpmn_graph = importer.apply(bpmn_output_path)
        bpmn_graph = layouter.apply(bpmn_graph)
        # gets the net back
        net, im, fm = pm4py.objects.conversion.bpmn.variants.to_petri_net.apply(bpmn_graph)
        gviz = pn_visualizer.apply(net, im, fm)
        pn_visualizer.view(gviz)
        fitness1 = pm4py.evaluate_fitness_alignments(log, net, im, fm)
        precision1 = pm4py.evaluate_precision_alignments(log, net, im, fm)
        print("fitness 1", fitness1, fitness0 == fitness1)
        print("precision 1", precision1, precision0 == precision1)
        if not (fitness0 == fitness1 and precision0 == precision1):
            print("ALERT")
            input()
