import pm4py
from pm4py.algo.decision_mining import algorithm as decision_mining
import os


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "roadtraffic100traces.xes")
    log = pm4py.read_xes(log_path)
    net, im, fm = pm4py.discover_petri_net_inductive(log)
    net, im, fm = decision_mining.create_data_petri_nets_with_decisions(log, net, im, fm)
    pm4py.view_petri_net(net, im, fm, format="svg")


if __name__ == "__main__":
    execute_script()
