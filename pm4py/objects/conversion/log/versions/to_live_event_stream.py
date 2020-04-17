from pm4py.objects.conversion.log import factory as log_conv
from pm4py.streaming.stream import stream

def apply(obj, param=None):
    static = log_conv.apply(obj, variant=log_conv.TO_EVENT_STREAM)
    print(static)
    sorted(static, key=lambda e: e['time:timestamp'])
    print(static)
    online = stream.LiveEventStream()
    for e in static:
        online.append(e)
    return online



