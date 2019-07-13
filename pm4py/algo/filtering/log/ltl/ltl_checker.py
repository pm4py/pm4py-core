from pm4py.objects.conversion.log import factory as log_conv_factory
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY

POSITIVE = "positive"


def A_eventually_B(log, A, B, parameters=None):
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    new_log = EventLog()

    for trace in log:
        occ_A = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == A]
        occ_B = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == B]

        if len(A) > 0 and len(occ_B) > 0 and occ_A[-1] < occ_B[-1]:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log
