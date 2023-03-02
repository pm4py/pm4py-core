import pm4py
from pm4py.algo.filtering.pandas.timestamp_case_grouping import timestamp_case_grouping_filter


def execute_script():
    dataframe = pm4py.read_xes("../tests/input_data/roadtraffic100traces.xes")
    print(dataframe)
    filtered_dataframe = timestamp_case_grouping_filter.apply(dataframe, parameters={"filter_type": "concat"})
    print(filtered_dataframe)
    print(filtered_dataframe["concept:name"].value_counts())


if __name__ == "__main__":
    execute_script()
