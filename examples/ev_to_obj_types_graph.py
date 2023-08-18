import pm4py
from pm4py.visualization.ocel.eve_to_obj_types import visualizer


def execute_script():
    ocel = pm4py.read_ocel('../tests/input_data/ocel/example_log.jsonocel')
    gviz = visualizer.apply(ocel, parameters={"format": "svg", "annotate_frequency": True})
    visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
