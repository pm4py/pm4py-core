if True:
    # ignore this part in true PowerBI executions
    import os
    import pandas as pd
    from pm4py.objects.log.util import dataframe_utils

    log_path = os.path.join("..", "..", "tests", "input_data", "running-example.csv")

    dataset = pd.read_csv(log_path)
    dataset = dataframe_utils.convert_timestamp_columns_in_df(dataset)

import pandas as pd

# this part is required because the dataframe provided by PowerBI has strings
dataset["time:timestamp"] = pd.to_datetime(dataset["time:timestamp"])
dataset = dataset.sort_values("time:timestamp")

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petri_net import visualizer
from pm4py.objects.conversion.process_tree import converter as process_tree_converter

process_tree = inductive_miner.apply(dataset)
net, im, fm = process_tree_converter.apply(process_tree)
gviz = visualizer.apply(net, im, fm)
visualizer.matplotlib_view(gviz)
