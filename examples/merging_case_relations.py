import pandas as pd
import pm4py
from pm4py.util import constants
from pm4py.algo.merging.case_relations import algorithm as case_relations_merging
import os


def execute_script():
    dataframe1 = pd.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_even.csv"), dtype_backend=constants.DEFAULT_PANDAS_PARSING_DTYPE_BACKEND)
    dataframe1["time:timestamp"] = pd.to_datetime(dataframe1["time:timestamp"], utc=True, format="ISO8601")
    dataframe2 = pd.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_odd.csv"), dtype_backend=constants.DEFAULT_PANDAS_PARSING_DTYPE_BACKEND)
    dataframe2["time:timestamp"] = pd.to_datetime(dataframe2["time:timestamp"], utc=True, format="ISO8601")
    case_relations = pd.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "case_relations.csv"), dtype_backend=constants.DEFAULT_PANDAS_PARSING_DTYPE_BACKEND)
    merged = case_relations_merging.apply(dataframe1, dataframe2, case_relations)
    dfg, sa, ea = pm4py.discover_dfg(merged)
    pm4py.view_dfg(dfg, sa, ea, format="svg")


if __name__ == "__main__":
    execute_script()
