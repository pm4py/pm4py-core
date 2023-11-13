import pm4py
import os
from examples import examples_conf



def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    net, im, fm = pm4py.discover_petri_net_ilp(log)
    pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
