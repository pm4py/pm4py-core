import unittest
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.log.importer.xes import factory as xes_importer
import pm4py.objects.log.transform as log_transform
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.petrinet.common import visualize as pn_viz
from pm4py.algo.conformance.tokenreplay.versions import token_replay
from pm4py.algo.conformance.tokenreplay.versions.token_replay import NoConceptNameException
from pm4py.objects import petri
from pm4py.objects.petri.exporter import pnml as petri_exporter
from tests.constants import INPUT_DATA_DIR, OUTPUT_DATA_DIR, PROBLEMATIC_XES_DIR
import logging


class InductiveMinerDFTest(unittest.TestCase):
    def obtainPetriNetThroughImdf(self, log_name):
        if ".xes" in log_name:
            trace_log = xes_importer.import_log(log_name)
        else:
            event_log = csv_importer.import_log(log_name)
            trace_log = log_transform.transform_event_log_to_trace_log(event_log)
        net, marking, final_marking = inductive_miner.apply(trace_log, None)
        return trace_log, net, marking, final_marking

    def test_applyImdfToXES(self):
        # calculate and compare Petri nets obtained on the same log to verify that instances
        # are working correctly
        log1, net1, marking1, fmarking1 = self.obtainPetriNetThroughImdf(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log2, net2, marking2, fmarking2 = self.obtainPetriNetThroughImdf(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log1.sort()
        log1 = log1.sample()
        log1.insert_trace_index_as_event_attribute()
        log2.sort()
        log2 = log2.sample()
        log2.insert_trace_index_as_event_attribute()
        petri_exporter.export_net(net1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        self.assertEqual(len(net1.places), len(net2.places))
        #self.assertEqual(len(net1.transitions), len(net2.transitions))
        #self.assertEqual(len(net1.arcs), len(net2.arcs))
        final_marking = petri.petrinet.Marking()
        for p in net1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply_log(log1, net1, marking1, final_marking)

    def test_applyImdfToCSV(self):
        # calculate and compare Petri nets obtained on the same log to verify that instances
        # are working correctly
        log1, net1, marking1, fmarking1 = self.obtainPetriNetThroughImdf(
            os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        log2, net2, marking2, fmarking2 = self.obtainPetriNetThroughImdf(
            os.path.join(INPUT_DATA_DIR, "running-example.csv"))
        log1.sort()
        log1 = log1.sample()
        log1.insert_trace_index_as_event_attribute()
        log2.sort()
        log2 = log2.sample()
        log2.insert_trace_index_as_event_attribute()
        petri_exporter.export_net(net1, marking1, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        self.assertEqual(len(net1.places), len(net2.places))
        #self.assertEqual(len(net1.transitions), len(net2.transitions))
        #self.assertEqual(len(net1.arcs), len(net2.arcs))
        final_marking = petri.petrinet.Marking()
        for p in net1.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply_log(log1, net1, marking1, final_marking)

    def test_imdfVisualizationFromXES(self):
        log, net, marking, fmarking = self.obtainPetriNetThroughImdf(
            os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        log.sort()
        log = log.sample()
        log.insert_trace_index_as_event_attribute()
        petri_exporter.export_net(net, marking, os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        os.remove(os.path.join(OUTPUT_DATA_DIR, "running-example.pnml"))
        gviz = pn_viz.graphviz_visualization(net)
        final_marking = petri.petrinet.Marking()
        for p in net.places:
            if not p.out_arcs:
                final_marking[p] = 1
        aligned_traces = token_replay.apply_log(log, net, marking, final_marking)

    def test_applyImdfToProblematicLogs(self):
        logs = os.listdir(PROBLEMATIC_XES_DIR)
        for log in logs:
            try:
                log_full_path = os.path.join(PROBLEMATIC_XES_DIR, log)
                # calculate and compare Petri nets obtained on the same log to verify that instances
                # are working correctly
                log1, net1, marking1, fmarking1 = self.obtainPetriNetThroughImdf(log_full_path)
                log2, net2, marking2, fmarking2 = self.obtainPetriNetThroughImdf(log_full_path)
                self.assertEqual(len(net1.places), len(net2.places))
                #self.assertEqual(len(net1.transitions), len(net2.transitions))
                #self.assertEqual(len(net1.arcs), len(net2.arcs))
                final_marking = petri.petrinet.Marking()
                for p in net1.places:
                    if not p.out_arcs:
                        final_marking[p] = 1
                aligned_traces = token_replay.apply_log(log1, net1, marking1, final_marking)
            except SyntaxError as e:
                logging.info("SyntaxError on log " + str(log) + ": " + str(e))
            except NoConceptNameException as e:
                logging.info("Concept name error on log " + str(log) + ": " + str(e))


if __name__ == "__main__":
    unittest.main()
