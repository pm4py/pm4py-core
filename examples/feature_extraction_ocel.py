import os
import pm4py
from pm4py.algo.transformation.ocel.features.events import algorithm as events_feature_extraction
from pm4py.util import pandas_utils, constants


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    # extracts some features on the objects and embed them in a Pandas dataframe
    objects_features_df = pm4py.extract_ocel_features(ocel, "element")
    print(objects_features_df)
    # extracts some features on the events and embed them in a Pandas dataframe
    data_events, feature_names_events = events_feature_extraction.apply(ocel)
    events_features_df = pandas_utils.instantiate_dataframe(data_events, columns=feature_names_events)
    print(events_features_df)


if __name__ == "__main__":
    execute_script()
