if True:
    # ignore this part in true PowerBI executions
    import pandas as pd
    from pm4py.objects.log.util import dataframe_utils

    dataset = pd.read_csv("C:/running-example.csv")
    dataset = dataframe_utils.convert_timestamp_columns_in_df(dataset)

import pandas as pd

# this part is required because the dataframe provided by PowerBI has strings
dataset["time:timestamp"] = pd.to_datetime(dataset["time:timestamp"])
dataset = dataset.sort_values("time:timestamp")

from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics

dfg = df_statistics.get_dfg_graph(dataset)

from pm4py.algo.discovery.heuristics import algorithm as heu_miner

heu_net = heu_miner.apply_heu_dfg(dfg)

from pm4py.visualization.heuristics_net import visualizer as hn_visualizer

gviz = hn_visualizer.apply(heu_net)
hn_visualizer.matplotlib_view(gviz)
