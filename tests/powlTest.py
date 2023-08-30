import pm4py
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.visualization.powl.visualizer import apply as visualize_powl
from pm4py.algo.discovery.powl import algorithm as powl_disc
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.powl.converter import apply as powl_to_pn
import os

ROOT = ""


def discover_powl(event_log):
    powl = powl_disc.apply(event_log, variant=POWLDiscoveryVariant.CLUSTER)
    vis_1 = visualize_powl(powl, parameters={"format": "svg"})
    vis_1.view()
    pn, init, final = powl_to_pn(powl)
    pm4py.view_petri_net(pn, init, final, format="svg")


if __name__ == "__main__":
    log = xes_importer.apply(os.path.join("input_data", "reviewing.xes"))
    discover_powl(log)
