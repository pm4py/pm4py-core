import pm4py
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    temporal_features = pm4py.extract_temporal_features_dataframe(log, grouper_freq="W")
    print(temporal_features)


if __name__ == "__main__":
    execute_script()
