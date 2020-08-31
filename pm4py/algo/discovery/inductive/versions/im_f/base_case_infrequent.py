from pm4py.algo.discovery.inductive.versions.im import base_case


def single_activity_infrequent(log, noise_threshold, activity_key):
    if base_case.single_activity(log):
        activity = log[0][0][activity_key]
        number_of_traces = len(log)
        number_of_events = 0
        for trace in log:
            number_of_traces += len(trace)
        p = number_of_traces/(number_of_traces+number_of_events)
        if p-0.5 <= noise_threshold:
            logging_output = "single_activity_infr.: " + str(activity)
            logging.debug(logging_output)
            return True, activity
        else:
            return False, None
    else:
        return False, None
