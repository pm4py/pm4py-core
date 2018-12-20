import os

from pm4py.algo.discovery.alpha import factory as alpha_miner
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from pm4py.objects.log.importer.csv.versions import pandas_df_imp
from pm4py.objects.petri.reachability_graph import construct_reachability_graph
from pm4py.objects.stochastic_petri import ctmc
from pm4py.objects.stochastic_petri import map as stochastic_map
from pm4py.objects.stochastic_petri import tangible_reachability
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_decorations_from_dfg_spaths_acticount
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_shortest_paths
from pm4py.visualization.transition_system import factory as ts_vis_factory


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.csv")
    dataframe = pandas_df_imp.import_dataframe_from_path(log_path)
    activities_count = dict(dataframe.groupby("concept:name").size())
    [dfg_frequency, dfg_performance] = df_statistics.get_dfg_graph(dataframe, measure="both",
                                                                   perf_aggregation_key="mean")
    net, initial_marking, final_marking = alpha_miner.apply_dfg(dfg_frequency)
    spaths = get_shortest_paths(net)
    aggregated_statistics = get_decorations_from_dfg_spaths_acticount(net, dfg_performance,
                                                                      spaths,
                                                                      activities_count,
                                                                      variant="performance")
    # obtain stochastic information for transitions in the model
    s_map = stochastic_map.get_map_exponential_from_aggstatistics(aggregated_statistics)
    # gets the reachability graph from the Petri net
    reachab_graph = construct_reachability_graph(net, initial_marking)
    # get the tangible reachability graph from the reachability graph and the stochastic map
    tang_reach_graph = tangible_reachability.get_tangible_reachability_from_reachability(reachab_graph, s_map)
    # visualize the tangible reachability graph on the screen
    viz = ts_vis_factory.apply(tang_reach_graph, parameters={"format": "svg", "show_labels": True, "show_names": True})
    ts_vis_factory.view(viz)
    # gets the Q matrix assuming exponential distributions
    q_matrix = ctmc.get_q_matrix_from_tangible_exponential(tang_reach_graph, s_map)
    # pick a state to start from
    states = sorted(list(tang_reach_graph.states), key=lambda x: x.name)
    state = states[0]
    print("\n\nstarting from state = ", state.name)
    # do transient analysis after 1 day
    transient_result = ctmc.transient_analysis_from_tangible_q_matrix_and_single_state(tang_reach_graph, q_matrix,
                                                                                       state, 86400)
    print("\nprobability for each state after 1 day = ", transient_result)
    # do transient analysis after 10 days
    transient_result = ctmc.transient_analysis_from_tangible_q_matrix_and_single_state(tang_reach_graph, q_matrix,
                                                                                       state, 864000)
    print("\nprobability for each state after 10 days = ", transient_result)
    # do transient analysis after 100 days
    transient_result = ctmc.transient_analysis_from_tangible_q_matrix_and_single_state(tang_reach_graph, q_matrix,
                                                                                       state, 8640000)
    print("\nprobability for each state after 100 days = ", transient_result)
    steady_state = ctmc.steadystate_analysis_from_tangible_q_matrix(tang_reach_graph, q_matrix)
    print("\nsteady state = ", steady_state)


if __name__ == "__main__":
    execute_script()
