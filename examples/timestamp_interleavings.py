from pm4py.util import constants
import pandas as pd
from pm4py.algo.discovery.ocel.interleavings import algorithm as interleavings_miner
from pm4py.visualization.ocel.interleavings import visualizer as interleavings_visualizer
import os


def execute_script():
    receipt_even = pd.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_even.csv"), dtype_backend=constants.DEFAULT_PANDAS_PARSING_DTYPE_BACKEND)
    receipt_even["time:timestamp"] = pd.to_datetime(receipt_even["time:timestamp"], utc=True, format="ISO8601")
    receipt_odd = pd.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_odd.csv"), dtype_backend=constants.DEFAULT_PANDAS_PARSING_DTYPE_BACKEND)
    receipt_odd["time:timestamp"] = pd.to_datetime(receipt_odd["time:timestamp"], utc=True, format="ISO8601")
    case_relations = pd.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "case_relations.csv"), dtype_backend=constants.DEFAULT_PANDAS_PARSING_DTYPE_BACKEND)
    interleavings_dataframe = interleavings_miner.apply(receipt_even, receipt_odd, case_relations)
    print(interleavings_dataframe)
    # print the frequency and the direction of the interleavings
    print(interleavings_dataframe[["@@source_activity", "@@target_activity", "@@direction"]].value_counts())
    # print the performance of the interleavings
    print(interleavings_dataframe.groupby(["@@source_activity", "@@target_activity", "@@direction"])["@@timestamp_diff"].agg("mean"))
    # visualizes the frequency of the interleavings
    gviz_freq = interleavings_visualizer.apply(receipt_even, receipt_odd, interleavings_dataframe, parameters={"annotation": "frequency", "format": "svg"})
    interleavings_visualizer.view(gviz_freq)
    # visualizes the performance of the interleavings
    gviz_perf = interleavings_visualizer.apply(receipt_even, receipt_odd, interleavings_dataframe, parameters={"annotation": "performance", "aggregation_measure": "median", "format": "svg"})
    interleavings_visualizer.view(gviz_perf)


if __name__ == "__main__":
    execute_script()
