from copy import deepcopy
from pm4py.objects.dcr.semantics import DcrSemantics


def apply(dcr_model, event_log):
    at_least_once_all_traces = set(dcr_model['events'])
    end_excluded_all_traces = set(dcr_model['events'])

    for trace in event_log:
        executed_events = set()
        im = deepcopy(dcr_model['marking'])
        dcr = deepcopy(dcr_model)
        complete = True
        semantics_obj = DcrSemantics(dcr)
        for event in trace:
            executed = semantics_obj.execute(event['concept:name'])
            if executed:
                executed_events.add(event['concept:name'])
            # TODO make this a filtering
            # complete = complete and event['lifecycle:transition'] == 'complete'
        if complete:
            fm = deepcopy(dcr['marking'])
            excluded_events = im['included'].difference(fm['included'])
            at_least_once_all_traces = at_least_once_all_traces.intersection(executed_events)
            end_excluded_all_traces = end_excluded_all_traces.intersection(excluded_events)

    initially_pending = at_least_once_all_traces.union(end_excluded_all_traces)
    dcr_model['marking']['pending'] = initially_pending
    return dcr_model
