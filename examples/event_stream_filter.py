from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter
from pm4py.objects.log.util import func
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    stream = converter.apply(log, variant=converter.Variants.TO_EVENT_STREAM)
    print([x["concept:name"] for x in stream])
    # keeps only events having register request as activity
    stream2 = func.filter_(lambda e: e["concept:name"] == "register request", stream)
    print(type(stream2))
    print([x["concept:name"] for x in stream2])


if __name__ == "__main__":
    execute_script()
