import os
import unittest

import pandas as pd

import pm4py
from pm4py.objects.bpmn.bpmn_graph import BPMN
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.process_tree.process_tree import ProcessTree


class SimplifiedInterfaceTest(unittest.TestCase):
    def test_csv(self):
        df = pd.read_csv("input_data/running-example.csv")
        df = pm4py.format_dataframe(df, case_id="case:concept:name", activity_key="concept:name",
                                    timestamp_key="time:timestamp")
        log2 = pm4py.convert_to_event_log(df)
        stream1 = pm4py.convert_to_event_stream(log2)
        df2 = pm4py.convert_to_dataframe(log2)
        pm4py.write_xes(log2, "test_output_data/log.xes")
        os.remove("test_output_data/log.xes")

    def test_alpha_miner(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_alpha(log)

    def test_alpha_miner_plus(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_alpha_plus(log)

    def test_inductive_miner(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)

    def test_inductive_miner_noise(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=0.5)

    def test_heuristics_miner(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_heuristics(log)

    def test_inductive_miner_tree(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        tree = pm4py.discover_tree_inductive(log)
        tree = pm4py.discover_tree_inductive(log, noise_threshold=0.2)

    def test_heuristics_miner_heu_net(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        heu_net = pm4py.discover_heuristics_net(log)

    def test_dfg(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        dfg, sa, ea = pm4py.discover_dfg(log)

    def test_read_petri(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")

    def test_read_tree(self):
        tree = pm4py.read_ptml("input_data/running-example.ptml")

    def test_read_dfg(self):
        dfg, sa, ea = pm4py.read_dfg("input_data/running-example.dfg")

    def test_alignments(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        aligned_traces = pm4py.conformance_diagnostics_alignments(log, net, im, fm)

    def test_tbr(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        replayed_traces = pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)

    def test_fitness_alignments(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        fitness_ali = pm4py.fitness_alignments(log, net, im, fm)

    def test_fitness_tbr(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        fitness_tbr = pm4py.fitness_token_based_replay(log, net, im, fm)

    def test_precision_alignments(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        precision_ali = pm4py.precision_alignments(log, net, im, fm)

    def test_precision_tbr(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        precision_tbr = pm4py.precision_token_based_replay(log, net, im, fm)

    def test_convert_to_tree_from_petri(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        tree = pm4py.convert_to_process_tree(net, im, fm)
        self.assertTrue(isinstance(tree, ProcessTree))

    def test_convert_to_tree_from_bpmn(self):
        bpmn = pm4py.read_bpmn("input_data/running-example.bpmn")
        tree = pm4py.convert_to_process_tree(bpmn)
        self.assertTrue(isinstance(tree, ProcessTree))

    def test_convert_to_net_from_tree(self):
        tree = pm4py.read_ptml("input_data/running-example.ptml")
        net, im, fm = pm4py.convert_to_petri_net(tree)
        self.assertTrue(isinstance(net, PetriNet))

    def test_convert_to_net_from_bpmn(self):
        bpmn = pm4py.read_bpmn("input_data/running-example.bpmn")
        net, im, fm = pm4py.convert_to_petri_net(bpmn)
        self.assertTrue(isinstance(net, PetriNet))

    def test_convert_to_net_from_dfg(self):
        dfg, sa, ea = pm4py.read_dfg("input_data/running-example.dfg")
        net, im, fm = pm4py.convert_to_petri_net(dfg, sa, ea)
        self.assertTrue(isinstance(net, PetriNet))

    def test_convert_to_net_from_heu(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        heu_net = pm4py.discover_heuristics_net(log)
        net, im, fm = pm4py.convert_to_petri_net(heu_net)
        self.assertTrue(isinstance(net, PetriNet))

    def test_convert_to_bpmn_from_tree(self):
        tree = pm4py.read_ptml("input_data/running-example.ptml")
        bpmn = pm4py.convert_to_bpmn(tree)
        self.assertTrue(isinstance(bpmn, BPMN))

    def test_statistics_log(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        pm4py.get_start_activities(log)
        pm4py.get_end_activities(log)
        pm4py.get_attributes(log)
        pm4py.get_trace_attributes(log)
        pm4py.get_attribute_values(log, "org:resource")
        pm4py.get_variants(log)

    def test_statistics_df(self):
        df = pd.read_csv("input_data/running-example.csv")
        df = pm4py.format_dataframe(df, case_id="case:concept:name", activity_key="concept:name",
                                    timestamp_key="time:timestamp")
        pm4py.get_start_activities(df)
        pm4py.get_end_activities(df)
        pm4py.get_attributes(df)
        pm4py.get_attribute_values(df, "org:resource")
        pm4py.get_variants(df)

    def test_playout(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        pm4py.play_out(net, im, fm)

    def test_generator(self):
        pm4py.generate_process_tree()

    def test_mark_em_equation(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        sync_net, sync_im, sync_fm = pm4py.construct_synchronous_product_net(log[0], net, im, fm)
        m_h = pm4py.solve_marking_equation(sync_net, sync_im, sync_fm)
        em_h = pm4py.solve_extended_marking_equation(log[0], sync_net, sync_im, sync_fm)

    def test_new_statistics_log(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        pm4py.get_trace_attribute_values(log, "creator")
        pm4py.discover_eventually_follows_graph(log)
        pm4py.get_case_arrival_average(log)

    def test_new_statistics_df(self):
        df = pd.read_csv("input_data/running-example.csv")
        df = pm4py.format_dataframe(df)
        pm4py.get_trace_attribute_values(df, "case:creator")
        pm4py.discover_eventually_follows_graph(df)
        pm4py.get_case_arrival_average(df)


if __name__ == "__main__":
    unittest.main()
