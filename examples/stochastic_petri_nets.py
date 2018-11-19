import os

from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.petri.exporter import pnml as petri_exporter
from pm4py.objects.petri.importer import pnml as petri_importer
from pm4py.objects.petri.reachability_graph import construct_reachability_graph
from pm4py.objects.stochastic_petri import map as stochastic_map
from pm4py.objects.stochastic_petri import tangible_reachability
from pm4py.visualization.transition_system import factory as ts_vis_factory


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_importer.apply(log_path)
    # obtain Petri net through Alpha Miner
    net, initial_marking, final_marking = alpha_miner.apply(log)
    # obtain stochastic information for transitions in the model
    s_map = stochastic_map.get_map_from_log_and_net(log, net, initial_marking, final_marking)
    # export the current stochastic Petri net
    petri_exporter.export_net(net, initial_marking, "example.pnml", final_marking=final_marking, stochastic_map=s_map)
    # re-import the current stochastic Petri net from file
    net, initial_marking, final_marking, s_map = petri_importer.import_net("example.pnml",
                                                                           return_stochastic_information=True)
    # remove temporary file
    os.remove("example.pnml")
    # gets the reachability graph from the Petri net
    reachab_graph = construct_reachability_graph(net, initial_marking)
    # get the tangible reachability graph from the reachability graph and the stochastic map
    tang_reach_graph = tangible_reachability.get_tangible_reachability_from_reachability(reachab_graph, s_map)
    # visualize the tangible reachability graph on the screen
    viz = ts_vis_factory.apply(tang_reach_graph, parameters={"format": "svg", "show_labels": True, "show_names": False})
    ts_vis_factory.view(viz)


if __name__ == "__main__":
    execute_script()
