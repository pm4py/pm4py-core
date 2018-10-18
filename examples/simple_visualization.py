import os

from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.util import simple_view


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.import_log(log_path)
    gviz = simple_view.apply(log, parameters={"format": "svg"})
    simple_view.view(gviz)


if __name__ == "__main__":
    execute_script()
