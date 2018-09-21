import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from pm4py.entities.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.petrinet.util import vis_trans_shortest_paths
from pm4py.algo.filtering.tracelog.attributes import attributes_filter
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory

def execute_script():
    # read the log using the nonstandard importer (faster)
    logPath = os.path.join("..","tests","inputData","receipt.xes")
    log = xes_importer.import_log(logPath, variant="nonstandard")
    # applies Inductive Miner on the log
    net, initial_marking, final_marking = inductive_miner.apply(log)
    # find shortest paths in the net
    spaths = vis_trans_shortest_paths.get_shortest_paths(net)

    # then we start to decorate the net
    # we decide if we should decorate it with frequency or performance
    variant = "frequency"
    # we decide the aggregation measure (sum, min, max, mean, median, stdev)
    if variant == "frequency":
        aggregationMeasure = "sum"
    elif variant == "performance":
        aggregationMeasure = "mean"
    # we find the DFG
    dfg = dfg_factory.apply(log, variant=variant)
    # we find the number of activities occurrences in the trace log
    activities_count = attributes_filter.get_attributes_from_log(log, "concept:name")
    # we calculate the statistics on the Petri net applying the greedy algorithm
    aggregated_statistics = vis_trans_shortest_paths.get_net_decorations_from_dfg_spaths_acticount(net, dfg, spaths,
                                                                                                   activities_count,
                                                                                                   variant=variant,
                                                                                                   aggregationMeasure=aggregationMeasure)
    # we find the gviz
    parameters_viz = {"format":"svg"}
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, variant=variant, aggregated_statistics=aggregated_statistics)
    # we show the viz on screen
    gviz.view()
    # we save the vis to file
    #pn_vis_factory.save(gviz, "receipt.pnml")

if __name__ == "__main__":
    execute_script()