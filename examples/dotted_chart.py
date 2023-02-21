import pm4py
import os


def execute_script():
    # reads a XES log
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # generates the default dotted chart (timestamp on X-axis, case ID on Y-axis, activity as color)
    pm4py.view_dotted_chart(log, format="svg")
    # generates the dotted chart with the activity on the X-axis, the resource on the Y-axis, and the group
    # as color
    pm4py.view_dotted_chart(log, format="svg", attributes=["concept:name", "org:resource", "org:group"])


if __name__ == "__main__":
    execute_script()
