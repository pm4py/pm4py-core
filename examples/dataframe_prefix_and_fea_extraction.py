import pandas as pd

from pm4py.objects.log.util import dataframe_utils
from pm4py.util import pandas_utils, constants


def execute_script():
    # loads a dataframe. setup dates
    df = pd.read_csv("../tests/input_data/receipt.csv")
    df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format="ISO8601")
    print(df)
    # insert the case index in the dataframe
    df = pandas_utils.insert_ev_in_tr_index(df, case_id="case:concept:name", column_name="@@index_in_trace")
    # filter all the prefixes of length 5 from the dataframe
    df = df[df["@@index_in_trace"] <= 5]
    print(df)
    # performs the automatic feature extraction
    fea_df = dataframe_utils.automatic_feature_extraction_df(df)
    print("\nfea_df =")
    print(fea_df)
    print(fea_df.columns)


if __name__ == "__main__":
    execute_script()
