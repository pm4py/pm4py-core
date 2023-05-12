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

from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics

dfg = df_statistics.get_dfg_graph(dataset, measure="frequency")

from pm4py.statistics.attributes.pandas import get as attributes_get

activities_count = attributes_get.get_attribute_values(dataset, "concept:name")

from pm4py.statistics.start_activities.pandas import get as sa_get

start_activities = sa_get.get_start_activities(dataset)
from pm4py.statistics.end_activities.pandas import get as ea_get

end_activities = ea_get.get_end_activities(dataset)

from pm4py.visualization.dfg import visualizer

gviz = visualizer.apply(dfg, activities_count=activities_count, variant=visualizer.Variants.FREQUENCY,
                        parameters={"start_activities": start_activities, "end_activities": end_activities})
visualizer.matplotlib_view(gviz)
