from copy import deepcopy
from pm4py.objects.dcr import semantics as dcr_semantics


def apply(dcr_model, event_log):
    at_least_once_all_traces = set(dcr_model['events'])
    end_excluded_all_traces = set(dcr_model['events'])

    for trace in event_log:
        executed_events = set()
        im = dcr_model['marking']
        dcr = deepcopy(dcr_model)
        complete = True
        for event in trace:
            executed = dcr_semantics.execute(event['concept:name'], dcr)
            if executed:
                executed_events.add(event['concept:name'])
            complete = complete and event['lifecycle:transition'] == 'complete'
        if complete:
            fm = dcr['marking']
            excluded_events = im['included'].difference(fm['included'])
            at_least_once_all_traces = at_least_once_all_traces.intersection(executed_events)
            end_excluded_all_traces = end_excluded_all_traces.intersection(excluded_events)

    initially_pending = at_least_once_all_traces.union(end_excluded_all_traces)
    return initially_pending
