from pm4py.objects.conversion.log import converter as log_conv
from pm4py.streaming.stream import stream
import deprecation

@deprecation.deprecated(deprecated_in='1.3.0', removed_in='2.0.0', current_version='',
                        details='conversion versions are deprecated; use conversion variants instead')
def apply(obj, param=None):
    static = log_conv.apply(obj, variant=log_conv.TO_EVENT_STREAM)
    print(static)
    sorted(static, key=lambda e: e['time:timestamp'])
    print(static)
    online = stream.LiveEventStream()
    for e in static:
        online.append(e)
    return online



