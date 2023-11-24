import pandas as pd
import pm4py
from pm4py.util import constants, pandas_utils
import os


def execute_script():
    dataframe = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "receipt.csv"))
    dataframe["time:timestamp"] = pandas_utils.dataframe_column_string_to_datetime(dataframe["time:timestamp"], utc=constants.ENABLE_DATETIME_COLUMNS_UTC, format=constants.DEFAULT_XES_TIMESTAMP_PARSE_FORMAT)
    # prints the summary of the positions of two activities
    print(pm4py.get_activity_position_summary(dataframe, "Confirmation of receipt"))
    print(pm4py.get_activity_position_summary(dataframe, "T02 Check confirmation of receipt"))


if __name__ == "__main__":
    execute_script()
