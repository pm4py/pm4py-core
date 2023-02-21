import pm4py
from pm4py.algo.discovery.transition_system import algorithm as transition_system_discovery
from pm4py.visualization.transition_system.variants import trans_frequency
from pm4py.visualization.transition_system import visualizer as transition_system_visualizer
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    ts = transition_system_discovery.apply(log, parameters={"include_data": True, "direction": "forward"})
    gviz = trans_frequency.apply(ts, parameters={"format": "svg"})
    transition_system_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
