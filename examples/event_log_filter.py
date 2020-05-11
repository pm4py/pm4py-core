from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import func
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    print(len(log))
    log2 = func.filter_(lambda x: len(x) > 5, log)
    print(type(log2))
    print(len(log2))


if __name__ == "__main__":
    execute_script()
