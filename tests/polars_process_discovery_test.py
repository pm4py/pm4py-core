import os
import random
import unittest

import polars as pl

import pm4py


class TestPolarsProcessDiscovery(unittest.TestCase):
    DATA_DIR = os.path.join(os.path.dirname(__file__), "input_data")
    LOG_FILE = os.path.join(DATA_DIR, "running-example.csv")

    @classmethod
    def _load_lazy_log(cls) -> pl.LazyFrame:
        df = pl.read_csv(cls.LOG_FILE)
        df = df.with_columns(
            pl.col("time:timestamp").str.strptime(
                pl.Datetime, "%Y-%m-%d %H:%M:%S%z"
            ),
            pl.col("case:concept:name").cast(pl.Utf8),
            pl.col("concept:name").cast(pl.Utf8),
            pl.col("org:resource").cast(pl.Utf8),
        )
        return df.lazy()

    def _lazy_log(self) -> pl.LazyFrame:
        return self._load_lazy_log()

    def test_discover_dfg(self):
        log = self._lazy_log()
        dfg, start_activities, end_activities = pm4py.discover_dfg(log)
        self.assertTrue(isinstance(dfg, dict) and dfg)
        self.assertTrue(isinstance(start_activities, dict) and start_activities)
        self.assertTrue(isinstance(end_activities, dict) and end_activities)

    def test_discover_performance_dfg(self):
        log = self._lazy_log()
        dfg, start_activities, end_activities = pm4py.discover_performance_dfg(log)
        self.assertTrue(isinstance(dfg, dict) and dfg)
        self.assertTrue(isinstance(start_activities, dict) and start_activities)
        self.assertTrue(isinstance(end_activities, dict) and end_activities)

    def test_discover_dfg_typed(self):
        log = self._lazy_log()
        dfg_obj = pm4py.discover_dfg_typed(log)
        self.assertIsNotNone(dfg_obj)

    def test_discover_petri_net_alpha(self):
        log = self._lazy_log()
        net, im, fm = pm4py.discover_petri_net_alpha(log)
        self.assertTrue(net.places and net.transitions)
        self.assertTrue(len(im) > 0)
        self.assertTrue(len(fm) > 0)

    def test_discover_petri_net_ilp(self):
        log = self._lazy_log()
        try:
            net, im, fm = pm4py.discover_petri_net_ilp(log)
        except (ImportError, ModuleNotFoundError) as exc:
            self.skipTest(f"ILP discovery optional dependency missing: {exc}")
        self.assertTrue(net.places and net.transitions)
        self.assertTrue(len(im) > 0)
        self.assertTrue(len(fm) > 0)

    def test_discover_petri_net_inductive(self):
        log = self._lazy_log()
        net, im, fm = pm4py.discover_petri_net_inductive(log)
        self.assertTrue(net.places and net.transitions)
        self.assertTrue(len(im) > 0)
        self.assertTrue(len(fm) > 0)

    def test_discover_petri_net_heuristics(self):
        log = self._lazy_log()
        net, im, fm = pm4py.discover_petri_net_heuristics(log)
        self.assertTrue(net.places and net.transitions)
        self.assertTrue(len(im) > 0)
        self.assertTrue(len(fm) > 0)

    def test_discover_petri_net_genetic(self):
        # Keep the compatibility check reproducible across versions and test order.
        random_state = random.getstate()
        self.addCleanup(random.setstate, random_state)
        random.seed(0)
        log = self._lazy_log()
        net, im, fm = pm4py.discover_petri_net_genetic(log, population_size = 10, generations = 10)
        self.assertTrue(net.places and net.transitions)
        self.assertTrue(len(im) > 0)
        self.assertTrue(len(fm) > 0)

    def test_discover_process_tree_inductive(self):
        log = self._lazy_log()
        process_tree = pm4py.discover_process_tree_inductive(log)
        self.assertIsNotNone(process_tree)

    def test_discover_heuristics_net(self):
        log = self._lazy_log()
        heuristics_net = pm4py.discover_heuristics_net(log)
        self.assertIsNotNone(heuristics_net)

    def test_derive_minimum_self_distance(self):
        log = self._lazy_log()
        msd = pm4py.derive_minimum_self_distance(log)
        self.assertTrue(msd)

    def test_discover_footprints(self):
        log = self._lazy_log()
        footprints = pm4py.discover_footprints(log)
        self.assertIsNotNone(footprints)

    def test_discover_eventually_follows_graph(self):
        log = self._lazy_log()
        efg = pm4py.discover_eventually_follows_graph(log)
        self.assertTrue(isinstance(efg, dict) and efg)

    def test_discover_bpmn_inductive(self):
        log = self._lazy_log()
        bpmn = pm4py.discover_bpmn_inductive(log)
        self.assertIsNotNone(bpmn)

    def test_discover_transition_system(self):
        log = self._lazy_log()
        transition_system = pm4py.discover_transition_system(log)
        self.assertIsNotNone(transition_system)

    def test_discover_prefix_tree(self):
        log = self._lazy_log()
        trie = pm4py.discover_prefix_tree(log)
        self.assertIsNotNone(trie)

    def test_discover_temporal_profile(self):
        log = self._lazy_log()
        temporal_profile = pm4py.discover_temporal_profile(log)
        self.assertTrue(isinstance(temporal_profile, dict) and temporal_profile)

    def test_discover_log_skeleton(self):
        log = self._lazy_log()
        log_skeleton = pm4py.discover_log_skeleton(log)
        self.assertIsInstance(log_skeleton, dict)

    def test_discover_declare(self):
        log = self._lazy_log()
        declare_model = pm4py.discover_declare(log)
        self.assertIsInstance(declare_model, dict)

    def test_discover_powl(self):
        log = self._lazy_log()
        try:
            powl_model = pm4py.discover_powl(log)
        except (ImportError, ModuleNotFoundError) as exc:
            self.skipTest(f"POWL discovery optional dependency missing: {exc}")
        self.assertIsNotNone(powl_model)

    def test_discover_batches(self):
        log = self._lazy_log()
        batches = pm4py.discover_batches(log)
        self.assertIsInstance(batches, list)

    def test_correlation_miner(self):
        log = self._lazy_log()
        dfg, start_activities, end_activities = pm4py.correlation_miner(log)
        self.assertIsInstance(dfg, dict)
        self.assertIsInstance(start_activities, dict)
        self.assertIsInstance(end_activities, dict)


if __name__ == "__main__":
    unittest.main()
