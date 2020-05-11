from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter
from pm4py.objects.log.util import func
import os


def add_underscore_to_resource(e):
    e["org:resource"] = e["org:resource"] + "_"
    return e


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    stream = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM)
    # adds an underscore to each resource
    stream2 = func.map_(lambda e: add_underscore_to_resource(e), stream)
    print(type(stream2))
    print([e["org:resource"] for e in stream2])


if __name__ == "__main__":
    execute_script()
