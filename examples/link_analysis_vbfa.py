from pm4py.util import constants, pandas_utils
from pm4py.algo.discovery.ocel.link_analysis import algorithm as link_analysis
from pm4py.objects.log.util import dataframe_utils
import os


def execute_script():
    dataframe = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "ocel", "VBFA.zip"), compression="zip", dtype="str")
    dataframe["time:timestamp"] = dataframe["ERDAT"] + " " + dataframe["ERZET"]
    dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format="%Y%m%d %H%M%S", timest_columns=["time:timestamp"])
    dataframe["RFWRT"] = dataframe["RFWRT"].astype(float)
    dataframe = link_analysis.apply(dataframe, parameters={"out_column": "VBELN", "in_column": "VBELV",
                                                           "sorting_column": "time:timestamp", "propagate": True})

    # finds the connected documents in which the currency in one document is different from the currency in the connected document.
    df_currency = dataframe[(dataframe["WAERS_out"] != " ") & (dataframe["WAERS_in"] != " ") & (
                dataframe["WAERS_out"] != dataframe["WAERS_in"])]
    print(df_currency[["WAERS_out", "WAERS_in"]].value_counts())

    # finds the connected documents in which the amount in one document is lower than the amount in the connected document.
    df_amount = dataframe[(dataframe["RFWRT_out"] > 0) & (dataframe["RFWRT_out"] < dataframe["RFWRT_in"])]
    print(df_amount[["RFWRT_out", "RFWRT_in"]])


if __name__ == "__main__":
    execute_script()
