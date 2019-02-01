import os

from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_decorations_from_dfg_spaths_acticount
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_shortest_paths


def execute_script(variant="frequency"):
    # read the log using the nonstandard importer (faster)
    log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.import_log(log_path, variant="nonstandard")
    # applies Inductive Miner on the log
    net, initial_marking, final_marking = inductive_miner.apply(log)
    # find shortest paths in the net
    spaths = get_shortest_paths(net)

    # then we start to decorate the net
    # we decide if we should decorate it with frequency or performance
    # we decide the aggregation measure (sum, min, max, mean, median, stdev)
    aggregation_measure = "mean"
    if variant == "frequency":
        aggregation_measure = "sum"
    # we find the DFG
    dfg = dfg_factory.apply(log, variant=variant)
    # we find the number of activities occurrences in the log
    activities_count = attributes_filter.get_attribute_values(log, "concept:name")
    # we calculate the statistics on the Petri net applying the greedy algorithm
    aggregated_statistics = get_decorations_from_dfg_spaths_acticount(net, dfg, spaths,
                                                                      activities_count,
                                                                      variant=variant,
                                                                      aggregation_measure=aggregation_measure)
    # we find the gviz
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, variant=variant,
                                aggregated_statistics=aggregated_statistics, parameters={"format": "svg"})
    # we show the viz on screen
    pn_vis_factory.view(gviz)
    # we save the vis to file
    # pn_vis_factory.save(gviz, "receipt.pnml")


if __name__ == "__main__":
    execute_script()
