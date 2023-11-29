import pm4py
from pm4py.util import constants, pandas_utils
from pm4py.objects.log.util import dataframe_utils
import os


def execute_script():
    dataframe = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "receipt.csv"))
    dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT, timest_columns=["time:timestamp"])
    # prints the summary of the positions of two activities
    print(pm4py.get_activity_position_summary(dataframe, "Confirmation of receipt"))
    print(pm4py.get_activity_position_summary(dataframe, "T02 Check confirmation of receipt"))


if __name__ == "__main__":
    execute_script()
