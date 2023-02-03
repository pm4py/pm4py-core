import pm4py
import os
import unittest


class OcelDiscoveryTest(unittest.TestCase):
    def test_discovery_ocfg_f1(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="frequency", act_metric="events", edge_metric="ev_couples", act_threshold=2, edge_threshold=1)
        os.remove(target_path)

    def test_discovery_ocfg_f2(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="frequency", act_metric="unique_objects", edge_metric="ev_couples", act_threshold=2, edge_threshold=1)
        os.remove(target_path)

    def test_discovery_ocfg_f3(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="frequency", act_metric="total_objects", edge_metric="ev_couples", act_threshold=2, edge_threshold=1)
        os.remove(target_path)


    def test_discovery_ocfg_f4(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="frequency", act_metric="unique_objects", edge_metric="unique_objects", act_threshold=2, edge_threshold=1)
        os.remove(target_path)


    def test_discovery_ocfg_f5(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="frequency", act_metric="unique_objects", edge_metric="total_objects", act_threshold=2, edge_threshold=1)
        os.remove(target_path)


    def test_discovery_ocfg_p1(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="performance", act_metric="events", edge_metric="ev_couples", act_threshold=2, edge_threshold=1)
        os.remove(target_path)

    def test_discovery_ocfg_p2(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="performance", act_metric="unique_objects", edge_metric="ev_couples", act_threshold=2, edge_threshold=1)
        os.remove(target_path)

    def test_discovery_ocfg_p3(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="performance", act_metric="total_objects", edge_metric="ev_couples", act_threshold=2, edge_threshold=1)
        os.remove(target_path)


    def test_discovery_ocfg_p4(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="performance", act_metric="unique_objects", edge_metric="total_objects", act_threshold=2, edge_threshold=1)
        os.remove(target_path)


    def test_discovery_ocfg_p5(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel, business_hours=True)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="performance", act_metric="unique_objects", edge_metric="total_objects", act_threshold=2, edge_threshold=1)
        os.remove(target_path)


    def test_discovery_ocfg_p6(self):
        target_path = os.path.join("test_output_data", "model.svg")
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocdfg = pm4py.discover_ocdfg(ocel, business_hours=True)
        pm4py.save_vis_ocdfg(ocdfg, target_path, annotation="performance", act_metric="unique_objects", edge_metric="total_objects", act_threshold=2, edge_threshold=1, performance_aggregation="median")
        os.remove(target_path)

    def test_discovery_ocpn_im(self):
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocpn = pm4py.discover_oc_petri_net(ocel, inductive_miner_variant="im")

    def test_discovery_ocpn_imd(self):
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        ocpn = pm4py.discover_oc_petri_net(ocel, inductive_miner_variant="imd")

    def test_discovery_saw_nets_ocel(self):
        from pm4py.algo.discovery.ocel.saw_nets import algorithm as saw_nets_disc
        ocel = pm4py.read_ocel(os.path.join("input_data", "ocel", "example_log.jsonocel"))
        saw_nets_disc.apply(ocel)


if __name__ == "__main__":
    unittest.main()
