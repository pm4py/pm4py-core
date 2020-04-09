from pm4py.objects.conversion.log import factory as log_conv_factory
from pm4py.objects.log.log import EventLog
from pm4py.util.xes_constants import DEFAULT_NAME_KEY, DEFAULT_RESOURCE_KEY, DEFAULT_TIMESTAMP_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY, PARAMETER_CONSTANT_RESOURCE_KEY, \
    PARAMETER_CONSTANT_TIMESTAMP_KEY

POSITIVE = "positive"
ENABLE_TIMESTAMP = "enable_timestamp"
TIMESTAMP_DIFF_BOUNDARIES = "timestamp_diff_boundaries"


def timestamp_list_is_ge(a, b):
    for i in range(len(a)):
        if a[i] < b[i][0]:
            return False
    return True


def timestamp_list_is_le(a, b):
    for i in range(len(a)):
        if a[i] > b[i][1]:
            return False
    return True


def A_eventually_B(log, A, B, parameters=None):
    """
    Applies the A eventually B rule

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A and B and in which A was eventually followed by B
        - If False, returns all the cases not containing A or B, or in which an instance of A was not eventually
        followed by an instance of B

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True
    enable_timestamp = parameters[ENABLE_TIMESTAMP] if ENABLE_TIMESTAMP in parameters else False
    timestamp_diff_boundaries = parameters[TIMESTAMP_DIFF_BOUNDARIES] if TIMESTAMP_DIFF_BOUNDARIES in parameters else []

    new_log = EventLog()

    for trace in log:
        if enable_timestamp:
            occ_A = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == A]
            occ_B = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == B]
            diffs = [[(occ_B[j].timestamp() - occ_A[i].timestamp())] for i in range(len(occ_A)) for j in
                     range(len(occ_B)) if occ_B[j] > occ_A[i]]
        else:
            occ_A = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == A]
            occ_B = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == B]
            diffs = [[(occ_B[j] - occ_A[i])] for i in range(len(occ_A)) for j in range(len(occ_B)) if
                     occ_B[j] > occ_A[i]]

        if enable_timestamp and timestamp_diff_boundaries:
            diffs = [d for d in diffs if
                     timestamp_list_is_ge(d, timestamp_diff_boundaries) and timestamp_list_is_le(d,
                                                                                                 timestamp_diff_boundaries)]

        if diffs:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def A_eventually_B_eventually_C(log, A, B, C, parameters=None):
    """
    Applies the A eventually B eventually C rule

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    C
        C attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was eventually followed by B and B was eventually followed by C
        - If False, returns all the cases not containing A or B or C, or in which an instance of A was not eventually
        followed by an instance of B or an instance of B was not eventually followed by C

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True
    enable_timestamp = parameters[ENABLE_TIMESTAMP] if ENABLE_TIMESTAMP in parameters else False
    timestamp_diff_boundaries = parameters[TIMESTAMP_DIFF_BOUNDARIES] if TIMESTAMP_DIFF_BOUNDARIES in parameters else []

    new_log = EventLog()

    for trace in log:
        if enable_timestamp:
            occ_A = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == A]
            occ_B = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == B]
            occ_C = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == C]
            diffs = [[occ_B[j].timestamp() - occ_A[i].timestamp(), occ_C[z].timestamp() - occ_B[j].timestamp()] for i in
                     range(len(occ_A)) for j in range(len(occ_B))
                     for z in range(len(occ_C)) if occ_B[j] > occ_A[i] and occ_C[z] > occ_B[j]]
        else:
            occ_A = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == A]
            occ_B = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == B]
            occ_C = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == C]
            diffs = [[occ_B[j] - occ_A[i], occ_C[z] - occ_B[j]] for i in range(len(occ_A)) for j in range(len(occ_B))
                     for z in range(len(occ_C)) if occ_B[j] > occ_A[i] and occ_C[z] > occ_B[j]]

        if enable_timestamp and timestamp_diff_boundaries:
            diffs = [d for d in diffs if
                     timestamp_list_is_ge(d, timestamp_diff_boundaries) and timestamp_list_is_le(d,
                                                                                                 timestamp_diff_boundaries)]

        if diffs:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def A_eventually_B_eventually_C_eventually_D(log, A, B, C, D, parameters=None):
    """
    Applies the A eventually B eventually C rule

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    C
        C attribute value
    D
        D attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was eventually followed by B and B was eventually followed by C
        - If False, returns all the cases not containing A or B or C, or in which an instance of A was not eventually
        followed by an instance of B or an instance of B was not eventually followed by C

    Returns
    ------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    timestamp_key = parameters[
        PARAMETER_CONSTANT_TIMESTAMP_KEY] if PARAMETER_CONSTANT_TIMESTAMP_KEY in parameters else DEFAULT_TIMESTAMP_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True
    enable_timestamp = parameters[ENABLE_TIMESTAMP] if ENABLE_TIMESTAMP in parameters else False
    timestamp_diff_boundaries = parameters[TIMESTAMP_DIFF_BOUNDARIES] if TIMESTAMP_DIFF_BOUNDARIES in parameters else []

    new_log = EventLog()

    for trace in log:
        if enable_timestamp:
            occ_A = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == A]
            occ_B = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == B]
            occ_C = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == C]
            occ_D = [trace[i][timestamp_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and trace[i][attribute_key] == D]
            diffs = [[occ_B[j].timestamp() - occ_A[i].timestamp(), occ_C[z].timestamp() - occ_B[j].timestamp(), occ_D[za].timestamp() - occ_C[z].timestamp()] for i in
                     range(len(occ_A)) for j in range(len(occ_B))
                     for z in range(len(occ_C)) for za in range(len(occ_D)) if occ_B[j] > occ_A[i] and occ_C[z] > occ_B[j] and occ_D[za] > occ_C[z]]
        else:
            occ_A = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == A]
            occ_B = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == B]
            occ_C = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == C]
            occ_D = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == D]

            diffs = [[occ_B[j] - occ_A[i], occ_C[z] - occ_B[j], occ_D[za] - occ_C[z]] for i in range(len(occ_A)) for j in range(len(occ_B))
                     for z in range(len(occ_C)) for za in range(len(occ_D)) if occ_B[j] > occ_A[i] and occ_C[z] > occ_B[j] and occ_D[za] > occ_C[z]]

        if enable_timestamp and timestamp_diff_boundaries:
            diffs = [d for d in diffs if
                     timestamp_list_is_ge(d, timestamp_diff_boundaries) and timestamp_list_is_le(d,
                                                                                                 timestamp_diff_boundaries)]

        if diffs:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def A_next_B_next_C(log, A, B, C, parameters=None):
    """
    Applies the A next B next C rule

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    C
        C attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - If True, returns all the cases containing A, B and C and in which A was directly followed by B and B was directly followed by C
        - If False, returns all the cases not containing A or B or C, or in which none instance of A was directly
        followed by an instance of B and B was directly followed by C

    Returns
    ------------
    filtered_log
        Filtered log
    """
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
        occ_C = [i for i in range(len(trace)) if attribute_key in trace[i] and trace[i][attribute_key] == C]

        found = False

        for a in occ_A:
            for b in occ_B:
                for c in occ_C:
                    if (b - a) == 1 and (c - b) == 1:
                        found = True

        if found:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log


def four_eyes_principle(log, A, B, parameters=None):
    """
    Verifies the Four Eyes Principle given A and B

    Parameters
    -------------
    log
        Log
    A
        A attribute value
    B
        B attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
        - if True, then filters all the cases containing A and B which have empty intersection between the set
          of resources doing A and B
        - if False, then filters all the cases containing A and B which have no empty intersection between the set
          of resources doing A and B

    Returns
    --------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    resource_key = parameters[
        PARAMETER_CONSTANT_RESOURCE_KEY] if PARAMETER_CONSTANT_RESOURCE_KEY in parameters else DEFAULT_RESOURCE_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    new_log = EventLog()

    for trace in log:
        occ_A = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == A])
        occ_B = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == B])

        if len(occ_A) > 0 and len(occ_B) > 0:
            inte = occ_A.intersection(occ_B)

            if not positive and len(inte) > 0:
                new_log.append(trace)
            elif positive and len(inte) == 0:
                new_log.append(trace)

    return new_log


def attr_value_different_persons(log, A, parameters=None):
    """
    Checks whether an attribute value is assumed on events done by different resources

    Parameters
    ------------
    log
        Log
    A
        A attribute value
    parameters
        Parameters of the algorithm, including the attribute key and the positive parameter:
            - if True, then filters all the cases containing occurrences of A done by different resources
            - if False, then filters all the cases not containing occurrences of A done by different resources

    Returns
    -------------
    filtered_log
        Filtered log
    """
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
    resource_key = parameters[
        PARAMETER_CONSTANT_RESOURCE_KEY] if PARAMETER_CONSTANT_RESOURCE_KEY in parameters else DEFAULT_RESOURCE_KEY
    positive = parameters[POSITIVE] if POSITIVE in parameters else True

    new_log = EventLog()

    for trace in log:
        occ_A = set([trace[i][resource_key] for i in range(len(trace)) if
                     attribute_key in trace[i] and resource_key in trace[i] and trace[i][attribute_key] == A])
        if len(occ_A) > 1:
            if positive:
                new_log.append(trace)
        elif not positive:
            new_log.append(trace)

    return new_log
