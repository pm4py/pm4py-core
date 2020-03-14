import os
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.enhancement.comparison.petrinet import element_usage_comparison
from pm4py.objects.log.util import sorting
from pm4py.objects.log.log import EventLog
from pm4py.visualization.petrinet import factory as pn_vis_factory


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    log = sorting.sort_timestamp(log)
    net, im, fm = inductive_miner.apply(log)
    log1 = EventLog(log[:500])
    log2 = EventLog(log[len(log)-500:])
    statistics = element_usage_comparison.compare_element_usage_two_logs(net, im, fm, log1, log2)
    gviz = pn_vis_factory.apply(net, im, fm, variant="frequency", aggregated_statistics=statistics, parameters={"format": "svg"})
    pn_vis_factory.view(gviz)


if __name__ == "__main__":
    execute_script()
