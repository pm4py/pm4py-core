import pm4py
from pm4py.util import constants, pandas_utils
from pm4py.objects.conversion.log import converter as log_converter
import os


def execute_script():
    dataframe = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "running-example.csv"))
    dataframe = pm4py.format_dataframe(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
    log = log_converter.apply(dataframe, variant=log_converter.Variants.TO_EVENT_LOG, parameters={"stream_postprocessing": False})
    pm4py.write_xes(log, "non_postprocessed.xes")
    log = log_converter.apply(dataframe, variant=log_converter.Variants.TO_EVENT_LOG, parameters={"stream_postprocessing": True})
    pm4py.write_xes(log, "postprocessed.xes")
    os.remove("non_postprocessed.xes")
    os.remove("postprocessed.xes")


if __name__ == "__main__":
    execute_script()
