from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.objects.stochastic_petri import ctmc
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    net, im, fm = alpha_miner.apply(log)
    # the alpha miner in this case returns a sound workflow net!
    # get the tangible reachability graph and the Q-matrix
    reach_graph, tang_reach_graph, stochastic_map, q_matrix = ctmc.get_tangible_reachability_and_q_matrix_from_log_net(
        log, net, im, fm)
    print(reach_graph.states)
    # pick the source state
    state = [x for x in tang_reach_graph.states if x.name.startswith("registerrequest") or x.name.startswith("reinitiaterequest")][0]
    # analyse the distribution over the states of the system starting from the source after 86400.0 seconds (1 day)
    transient_result = ctmc.transient_analysis_from_tangible_q_matrix_and_single_state(tang_reach_graph, q_matrix, state, 86400.0)
    print(transient_result)


if __name__ == "__main__":
    execute_script()
