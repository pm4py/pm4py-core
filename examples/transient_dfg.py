from pm4py.objects.log.importer.xes import factory as xes_importer
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))


if __name__ == "__main__":
    execute_script()
