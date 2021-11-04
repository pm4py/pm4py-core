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

from pm4py.statistics.attributes.pandas import get as attributes_filter
from pm4py.visualization.graphs import visualizer as graphs_visualizer

# visualize events over time graph
x_dates, y_dates = attributes_filter.get_kde_date_attribute(dataset)
graph_dates = graphs_visualizer.apply(x_dates, y_dates, variant=graphs_visualizer.Variants.DATES,
                                      parameters={graphs_visualizer.Variants.DATES.value.Parameters.FORMAT: "png"})
graphs_visualizer.matplotlib_view(graph_dates)
