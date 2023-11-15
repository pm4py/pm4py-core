import pm4py
from examples import examples_conf
import os


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    model = pm4py.discover_oc_petri_net(ocel)
    print(model.keys())
    pm4py.view_ocpn(model, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
