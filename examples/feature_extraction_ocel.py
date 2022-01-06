import os
import pm4py
import pandas as pd
from pm4py.algo.transformation.ocel.features.objects import algorithm as objects_feature_extraction
from pm4py.algo.transformation.ocel.features.events import algorithm as events_feature_extraction


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    # extracts some features on the objects and embed them in a Pandas dataframe
    data_objects, feature_names_objects = objects_feature_extraction.apply(ocel)
    objects_features_df = pd.DataFrame(data_objects, columns=feature_names_objects)
    print(objects_features_df)
    # extracts some features on the events and embed them in a Pandas dataframe
    data_events, feature_names_events = events_feature_extraction.apply(ocel)
    events_features_df = pd.DataFrame(data_events, columns=feature_names_events)
    print(events_features_df)


if __name__ == "__main__":
    execute_script()
