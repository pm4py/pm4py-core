import os
import unittest

import pandas as pd

import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.process_tree.obj import ProcessTree


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
        tree = pm4py.discover_process_tree_inductive(log)
        tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)

    def test_heuristics_miner_heu_net(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        heu_net = pm4py.discover_heuristics_net(log)

    def test_dfg(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        dfg, sa, ea = pm4py.discover_directly_follows_graph(log)

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
        pm4py.get_event_attributes(log)
        pm4py.get_trace_attributes(log)
        pm4py.get_event_attribute_values(log, "org:resource")
        pm4py.get_variants_as_tuples(log)

    def test_statistics_df(self):
        df = pd.read_csv("input_data/running-example.csv")
        df = pm4py.format_dataframe(df, case_id="case:concept:name", activity_key="concept:name",
                                    timestamp_key="time:timestamp")
        pm4py.get_start_activities(df)
        pm4py.get_end_activities(df)
        pm4py.get_event_attributes(df)
        pm4py.get_event_attribute_values(df, "org:resource")
        pm4py.get_variants_as_tuples(df)

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

    def test_serialization_log(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        ser = pm4py.serialize(log)
        log2 = pm4py.deserialize(ser)

    def test_serialization_dataframe(self):
        df = pd.read_csv("input_data/running-example.csv")
        df = pm4py.format_dataframe(df)
        ser = pm4py.serialize(df)
        df2 = pm4py.deserialize(ser)

    def test_serialization_petri_net(self):
        net, im, fm = pm4py.read_pnml("input_data/running-example.pnml")
        ser = pm4py.serialize(net, im, fm)
        net2, im2, fm2 = pm4py.deserialize(ser)

    def test_serialization_process_tree(self):
        tree = pm4py.read_ptml("input_data/running-example.ptml")
        ser = pm4py.serialize(tree)
        tree2 = pm4py.deserialize(ser)

    def test_serialization_bpmn(self):
        bpmn = pm4py.read_bpmn("input_data/running-example.bpmn")
        ser = pm4py.serialize(bpmn)
        bpmn2 = pm4py.deserialize(ser)

    def test_serialization_dfg(self):
        dfg, sa, ea = pm4py.read_dfg("input_data/running-example.dfg")
        ser = pm4py.serialize(dfg, sa, ea)
        dfg2, sa2, ea2 = pm4py.deserialize(ser)

    def test_minimum_self_distance(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        msd = pm4py.get_minimum_self_distances(log)

    def test_minimum_self_distance_2(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        msd = pm4py.get_minimum_self_distance_witnesses(log)

    def test_marking_equation_net(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        pm4py.solve_marking_equation(net, im, fm)

    def test_marking_equation_sync_net(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        sync_net, sync_im, sync_fm = pm4py.construct_synchronous_product_net(log[0], net, im, fm)
        res = pm4py.solve_marking_equation(sync_net, sync_im, sync_fm)
        self.assertIsNotNone(res)
        self.assertEqual(res, 11)

    def test_ext_marking_equation_sync_net(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        sync_net, sync_im, sync_fm = pm4py.construct_synchronous_product_net(log[0], net, im, fm)
        res = pm4py.solve_extended_marking_equation(log[0], sync_net, sync_im, sync_fm)
        self.assertIsNotNone(res)

    def test_alignments_tree(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        tree = pm4py.read_ptml(os.path.join("input_data", "running-example.ptml"))
        res = pm4py.conformance_diagnostics_alignments(log, tree)
        self.assertIsNotNone(res)

    def test_alignments_dfg(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        dfg, sa, ea = pm4py.read_dfg(os.path.join("input_data", "running-example.dfg"))
        res = pm4py.conformance_diagnostics_alignments(log, dfg, sa, ea)
        self.assertIsNotNone(res)

    def test_alignments_bpmn(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        bpmn_graph = pm4py.read_bpmn(os.path.join("input_data", "running-example.bpmn"))
        res = pm4py.conformance_diagnostics_alignments(log, bpmn_graph)
        self.assertIsNotNone(res)

    def test_discovery_inductive_bpmn(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        bpmn_graph = pm4py.discover_bpmn_inductive(log)
        self.assertIsNotNone(bpmn_graph)

    def test_generation(self):
        import pm4py
        tree = pm4py.generate_process_tree()
        self.assertIsNotNone(tree)

    def test_play_out_tree(self):
        import pm4py
        tree = pm4py.read_ptml(os.path.join("input_data", "running-example.ptml"))
        log = pm4py.play_out(tree)

    def test_play_out_net(self):
        import pm4py
        net, im, fm = pm4py.read_pnml(os.path.join("input_data", "running-example.pnml"))
        log = pm4py.play_out(net, im, fm)

    def test_msd(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        res1 = pm4py.get_minimum_self_distance_witnesses(log)
        res2 = pm4py.get_minimum_self_distances(log)
        self.assertIsNotNone(res1)
        self.assertIsNotNone(res2)

    def test_case_arrival(self):
        import pm4py
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        avg = pm4py.get_case_arrival_average(log)
        self.assertIsNotNone(avg)

    def test_efg(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        pm4py.discover_eventually_follows_graph(log)


if __name__ == "__main__":
    unittest.main()
