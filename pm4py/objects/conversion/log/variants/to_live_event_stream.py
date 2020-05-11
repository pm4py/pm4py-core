from pm4py.objects.conversion.log import converter as log_conv
from pm4py.streaming.stream import stream


def apply(obj, param=None):
    static = log_conv.apply(obj, variant=log_conv.TO_EVENT_STREAM)
    sorted(static, key=lambda e: e['time:timestamp'])
    online = stream.LiveEventStream()
    for e in static:
        online.append(e)
    return online
