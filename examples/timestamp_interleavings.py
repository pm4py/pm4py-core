from pm4py.util import constants, pandas_utils
from pm4py.algo.discovery.ocel.interleavings import algorithm as interleavings_miner
from pm4py.visualization.ocel.interleavings import visualizer as interleavings_visualizer
from pm4py.objects.log.util import dataframe_utils
from examples import examples_conf
import os


def execute_script():
    receipt_even = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_even.csv"))
    receipt_odd = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "receipt_odd.csv"))
    receipt_even = dataframe_utils.convert_timestamp_columns_in_df(receipt_even, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT, timest_columns=["time:timestamp"])
    receipt_odd = dataframe_utils.convert_timestamp_columns_in_df(receipt_odd, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT, timest_columns=["time:timestamp"])
    case_relations = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "interleavings", "case_relations.csv"))
    interleavings_dataframe = interleavings_miner.apply(receipt_even, receipt_odd, case_relations)
    print(interleavings_dataframe)
    # print the frequency and the direction of the interleavings
    print(interleavings_dataframe[["@@source_activity", "@@target_activity", "@@direction"]].value_counts())
    # print the performance of the interleavings
    print(interleavings_dataframe.groupby(["@@source_activity", "@@target_activity", "@@direction"])["@@timestamp_diff"].agg("mean"))
    # visualizes the frequency of the interleavings
    gviz_freq = interleavings_visualizer.apply(receipt_even, receipt_odd, interleavings_dataframe, parameters={"annotation": "frequency", "format": examples_conf.TARGET_IMG_FORMAT})
    interleavings_visualizer.view(gviz_freq)
    # visualizes the performance of the interleavings
    gviz_perf = interleavings_visualizer.apply(receipt_even, receipt_odd, interleavings_dataframe, parameters={"annotation": "performance", "aggregation_measure": "median", "format": examples_conf.TARGET_IMG_FORMAT})
    interleavings_visualizer.view(gviz_perf)


if __name__ == "__main__":
    execute_script()
