from pm4py.algo.discovery.temporal_profile import algorithm as temporal_profile_discovery
from pm4py.algo.conformance.temporal_profile import algorithm as temporal_profile_conformance
from pm4py.util import constants, pandas_utils
from pm4py.objects.log.util import dataframe_utils


def execute_script():
    dataframe = pandas_utils.read_csv("../tests/input_data/receipt.csv")
    dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
    tf = temporal_profile_discovery.apply(dataframe)
    conformance = temporal_profile_conformance.apply(dataframe, tf, parameters={"zeta": 6.0})
    for index, dev in enumerate(conformance):
        if len(dev) > 0:
            print(index, dev)


if __name__ == "__main__":
    execute_script()
