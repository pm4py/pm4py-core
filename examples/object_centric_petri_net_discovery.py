import pm4py
from pm4py.algo.discovery.ocel.ocpn import algorithm as ocpn_discovery
from pm4py.visualization.ocel.ocpn import visualizer as ocpn_visualizer
import os


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    model = ocpn_discovery.apply(ocel)
    print(model.keys())
    gviz = ocpn_visualizer.apply(model, parameters={"format": "svg"})
    ocpn_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
