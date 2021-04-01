from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import func
from pm4py.objects.log.obj import Trace
import os


def new_trace(t):
    t2 = Trace()
    t2.append(t[0])
    return t2

def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    print([len(x) for x in log])
    log2 = func.map_(lambda x: new_trace(x), log)
    print(type(log2))
    print([len(x) for x in log2])
    print([[y["concept:name"] for y in x] for x in log2])
    print(log2)


if __name__ == "__main__":
    execute_script()
