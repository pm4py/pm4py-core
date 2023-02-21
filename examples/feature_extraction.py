import pm4py
from pm4py.algo.transformation.log_to_features import algorithm as feature_extraction
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    data, feature_names = feature_extraction.apply(log, variant=feature_extraction.Variants.TRACE_BASED)
    print(data)
    print(feature_names)
    data, feature_names = feature_extraction.apply(log, variant=feature_extraction.Variants.EVENT_BASED)
    print(data)
    print(feature_names)


if __name__ == "__main__":
    execute_script()
