if True:
    # ignore this part in true PowerBI executions
    from pm4py.objects.log.adapters.pandas import csv_import_adapter

    dataset = csv_import_adapter.import_dataframe_from_path("C:/running-example.csv")

import pandas as pd
# this part is required because the dataframe provided by PowerBI has strings
dataset["time:timestamp"] = pd.to_datetime(dataset["time:timestamp"])

from pm4py.statistics.attributes.pandas import get as attributes_filter
from pm4py.visualization.graphs import visualizer as graphs_visualizer

# visualize events over time graph
x_dates, y_dates = attributes_filter.get_kde_date_attribute(dataset)
graph_dates = graphs_visualizer.apply(x_dates, y_dates, variant=graphs_visualizer.Variants.DATES,
                                      parameters={graphs_visualizer.Variants.DATES.value.Parameters.FORMAT: "png"})
graphs_visualizer.matplotlib_view(graph_dates)
