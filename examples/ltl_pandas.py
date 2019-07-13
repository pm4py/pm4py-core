import os
from pm4py.objects.log.adapters.pandas import csv_import_adapter


def execute_script():
    # import the dataframe
    df = csv_import_adapter.import_dataframe_from_path(os.path.join("tests", "input_data", "running-example.csv"))



if __name__ == "__main__":
    execute_script()
