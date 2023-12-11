import pm4py
from pm4py.util import constants, pandas_utils
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.merging.case_relations import algorithm as case_relations_merging
from examples import examples_conf
import os


def execute_script():
    dataframe1 = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_even.csv"))
    dataframe2 = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_odd.csv"))
    dataframe1 = dataframe_utils.convert_timestamp_columns_in_df(dataframe1, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT, timest_columns=["time:timestamp"])
    dataframe2 = dataframe_utils.convert_timestamp_columns_in_df(dataframe2, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT, timest_columns=["time:timestamp"])
    case_relations = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "case_relations.csv"))
    merged = case_relations_merging.apply(dataframe1, dataframe2, case_relations)
    dfg, sa, ea = pm4py.discover_dfg(merged)
    pm4py.view_dfg(dfg, sa, ea, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
