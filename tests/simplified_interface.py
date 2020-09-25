import pm4py
import unittest
import os


class SimplifiedInterfaceTest(unittest.TestCase):
    def test_csv(self):
        df = pm4py.read_csv("input_data/running-example.csv")
        df = pm4py.format_dataframe(df, case_id="case:concept:name", activity_key="concept:name",
                                    timestamp_key="time:timestamp")
        log2 = pm4py.convert_to_event_log(df)
        stream1 = pm4py.convert_to_event_stream(log2)
        df2 = pm4py.convert_to_dataframe(log2)
        pm4py.write_xes(log2, "test_output_data/log.xes")
        pm4py.write_csv(df, "test_output_data/log.csv")
        os.remove("test_output_data/log.xes")
        os.remove("test_output_data/log.csv")

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
        net, im, fm = pm4py.read_petri_net("input_data/running-example.pnml")

    def test_read_tree(self):
        tree = pm4py.read_process_tree("input_data/running-example.ptml")

    def test_read_dfg(self):
        dfg, sa, ea = pm4py.read_dfg("input_data/running-example.dfg")

    def test_alignments(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        aligned_traces = pm4py.conformance_alignments(log, net, im, fm)

    def test_tbr(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        replayed_traces = pm4py.conformance_tbr(log, net, im, fm)

    def test_fitness_alignments(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        fitness_ali = pm4py.evaluate_fitness_alignments(log, net, im, fm)

    def test_fitness_tbr(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        fitness_tbr = pm4py.evaluate_fitness_tbr(log, net, im, fm)

    def test_precision_alignments(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        precision_ali = pm4py.evaluate_precision_alignments(log, net, im, fm)

    def test_precision_tbr(self):
        log = pm4py.read_xes("input_data/running-example.xes")
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        precision_tbr = pm4py.evaluate_precision_tbr(log, net, im, fm)


if __name__ == "__main__":
    unittest.main()
