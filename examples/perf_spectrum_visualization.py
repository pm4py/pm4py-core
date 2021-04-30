import pm4py
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    pm4py.view_performance_spectrum(log, ["Confirmation of receipt", "T04 Determine confirmation of receipt",
                                         "T10 Determine necessity to stop indication"], format="svg")


if __name__ == "__main__":
    execute_script()
