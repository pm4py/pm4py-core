from pm4py.log import instance as log_instance


def transform_event_log_to_trace_log(log, case_glue='case:concept:name', includes_case_attributes=True, case_attribute_prefix='case:'):
    traces = {}
    for event in log:
        glue = event[case_glue]
        if glue not in traces:
            if includes_case_attributes:
                trace_attr = {}
                for k in event.keys():
                    if k.startswith(case_attribute_prefix):
                        trace_attr[k.replace(case_attribute_prefix, '')] = event[k]
            traces[glue] = log_instance.Trace(attributes=trace_attr)

        if includes_case_attributes:
            for k in list(event.keys()):
                if k.startswith(case_attribute_prefix):
                    del event[k]

        traces[glue].append(event)
    return log_instance.TraceLog(traces.values(), attributes=log.attributes, classifiers=log.classifiers, omni_present=log.omni_present, extensions=log.extensions)


def transform_trace_log_to_event_log(trace_log, include_case_attributes=True, case_attribute_prefix='case:'):
    event_log = []
    for trace in trace_log:
        for event in trace:
            if include_case_attributes:
                for key, value in trace.attributes.items():
                    event[case_attribute_prefix + key] = value
            event_log.append(event)
    return log_instance.EventLog(trace_log.attributes,event_log)

