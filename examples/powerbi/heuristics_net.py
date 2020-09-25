if True:
    # ignore this part in true PowerBI executions
    from pm4py.objects.log.adapters.pandas import csv_import_adapter

    dataset = csv_import_adapter.import_dataframe_from_path("C:/running-example.csv")

import pandas as pd
# this part is required because the dataframe provided by PowerBI has strings
dataset["time:timestamp"] = pd.to_datetime(dataset["time:timestamp"])

from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics

dfg = df_statistics.get_dfg_graph(dataset)

from pm4py.algo.discovery.heuristics import algorithm as heu_miner

heu_net = heu_miner.apply_heu_dfg(dfg)

from pm4py.visualization.heuristics_net import visualizer as hn_visualizer

gviz = hn_visualizer.apply(heu_net)
hn_visualizer.matplotlib_view(gviz)
