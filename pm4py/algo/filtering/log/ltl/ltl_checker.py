from pm4py.objects.conversion.log import factory as log_conv_factory
from pm4py.objects.log.log import EventLog
from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_ATTRIBUTE_KEY


def A_eventually_B(log, A, B, parameters=None):
    if parameters is None:
        parameters = {}

    if not isinstance(log, EventLog):
        log = log_conv_factory.apply(log, variant=log_conv_factory.TO_EVENT_LOG, parameters=parameters)

    attribute_key = parameters[
        PARAMETER_CONSTANT_ATTRIBUTE_KEY] if PARAMETER_CONSTANT_ATTRIBUTE_KEY in parameters else DEFAULT_NAME_KEY
