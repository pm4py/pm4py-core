if True:
    # ignore this part in true PowerBI executions
    from pm4py.objects.log.adapters.pandas import csv_import_adapter

    dataset = csv_import_adapter.import_dataframe_from_path("C:/running-example.csv")

import pandas as pd

# this part is required because the dataframe provided by PowerBI has strings
dataset["time:timestamp"] = pd.to_datetime(dataset["time:timestamp"])

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petrinet import visualizer

net, im, fm = inductive_miner.apply(dataset)
gviz = visualizer.apply(net, im, fm)
visualizer.matplotlib_view(gviz)
