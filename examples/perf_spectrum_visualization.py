import pm4py
import os
from pm4py.util import constants
from examples import examples_conf
import pandas as pd


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    pm4py.view_performance_spectrum(log, ["Confirmation of receipt", "T04 Determine confirmation of receipt",
                                         "T10 Determine necessity to stop indication"], format=examples_conf.TARGET_IMG_FORMAT)
    df = pd.read_csv(os.path.join("..", "tests", "input_data", "receipt.csv"))
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], utc=True, format="ISO8601")
    pm4py.view_performance_spectrum(df, ["Confirmation of receipt", "T04 Determine confirmation of receipt",
                                         "T10 Determine necessity to stop indication"], format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
