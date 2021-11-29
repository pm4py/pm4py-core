import pm4py
import os


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    model = pm4py.discover_oc_petri_net(ocel)
    print(model.keys())
    pm4py.view_ocpn(model, format="svg")


if __name__ == "__main__":
    execute_script()
