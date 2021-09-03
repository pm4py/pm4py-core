import pandas as pd
import pm4py
import os
from pm4py.streaming.conversion import from_pandas


def execute_script():
    df = pd.read_csv(os.path.join("..", "tests", "input_data", "receipt.csv"))
    df = pm4py.format_dataframe(df)
    it = from_pandas.apply(df)
    count = 0
    for trace in it:
        print(count, trace)
        count = count + 1


if __name__ == "__main__":
    execute_script()
