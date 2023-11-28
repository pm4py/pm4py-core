import pandas as pd
import pm4py
from pm4py.util import constants, pandas_utils
from pm4py.algo.merging.case_relations import algorithm as case_relations_merging
from examples import examples_conf
import os


def execute_script():
    dataframe1 = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_even.csv"))
    dataframe1["time:timestamp"] = pandas_utils.dataframe_column_string_to_datetime(dataframe1["time:timestamp"], utc=constants.ENABLE_DATETIME_COLUMNS_AWARE, format=constants.DEFAULT_XES_TIMESTAMP_PARSE_FORMAT)
    dataframe2 = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_odd.csv"))
    dataframe2["time:timestamp"] = pandas_utils.dataframe_column_string_to_datetime(dataframe2["time:timestamp"], utc=constants.ENABLE_DATETIME_COLUMNS_AWARE, format=constants.DEFAULT_XES_TIMESTAMP_PARSE_FORMAT)
    case_relations = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "case_relations.csv"))
    merged = case_relations_merging.apply(dataframe1, dataframe2, case_relations)
    dfg, sa, ea = pm4py.discover_dfg(merged)
    pm4py.view_dfg(dfg, sa, ea, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
