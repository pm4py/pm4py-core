from collections import Counter
from pm4py.objects.log.log import EventLog, Event, Trace
from pm4py.objects.log.util import xes as xes_util


def get_log_prefixes(log, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Get log prefixes

    Parameters
    ----------
    log
        Trace log
    activity_key
        Activity key (must be provided if different from concept:name)
    """
    prefixes = {}
    prefix_count = Counter()
    for trace in log:
        for i in range(1, len(trace)):
            red_trace = trace[0:i]
            prefix = ",".join([x[activity_key] for x in red_trace])
            next_activity = trace[i][activity_key]
            if prefix not in prefixes:
                prefixes[prefix] = set()
            prefixes[prefix].add(next_activity)
            prefix_count[prefix] += 1
    return prefixes, prefix_count


def form_fake_log(prefixes_keys, activity_key=xes_util.DEFAULT_NAME_KEY):
    """
    Form fake log for replay (putting each prefix as separate trace to align)

    Parameters
    ----------
    prefixes_keys
        Keys of the prefixes (to form a log with a given order)
    activity_key
        Activity key (must be provided if different from concept:name)
    """
    fake_log = EventLog()
    for prefix in prefixes_keys:
        trace = Trace()
        prefix_activities = prefix.split(",")
        for activity in prefix_activities:
            event = Event()
            event[activity_key] = activity
            trace.append(event)
        fake_log.append(trace)
    return fake_log
