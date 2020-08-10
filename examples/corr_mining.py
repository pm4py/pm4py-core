#import pm4pycvxopt
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.algo.discovery.correlation_mining import algorithm as correlation_miner
from pm4py.visualization.dfg import visualizer as dfg_vis


def execute_script():
    df = csv_import_adapter.import_dataframe_from_path("../tests/input_data/receipt.csv")
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
