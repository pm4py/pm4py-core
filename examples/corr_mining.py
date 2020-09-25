#import pm4pycvxopt
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.algo.discovery.correlation_mining import algorithm as correlation_miner
from pm4py.visualization.dfg import visualizer as dfg_vis


def execute_script():
    df = pd.read_csv("../tests/input_data/receipt.csv")
    df = dataframe_utils.convert_timestamp_columns_in_df(df)
    act_count = dict(df["concept:name"].value_counts())
    dfg, performance_dfg = correlation_miner.apply(df, variant=correlation_miner.Variants.CLASSIC)
    gviz_freq = dfg_vis.apply(dfg, activities_count=act_count, variant=dfg_vis.Variants.FREQUENCY,
                              parameters={"format": "svg"})
    dfg_vis.view(gviz_freq)
    gviz_perf = dfg_vis.apply(performance_dfg, activities_count=act_count, variant=dfg_vis.Variants.PERFORMANCE,
                              parameters={"format": "svg"})
    dfg_vis.view(gviz_perf)


if __name__ == "__main__":
    execute_script()
