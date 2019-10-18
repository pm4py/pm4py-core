from pm4py.statistics.traces.log import case_arrival
from pm4py.objects.stochastic_petri import map as mapping


def apply(log, net, im, fm, parameters=None):
    if parameters is None:
        parameters = {}

    parameters["business_hours"] = True

    case_arrival_ratio = parameters[
        "case_arrival_ratio"] if "case_arrival_ratio" in parameters else case_arrival.get_case_arrival_avg(log,
                                                                                                           parameters=parameters)

    map = mapping.get_map_from_log_and_net(log, net, im, fm, force_distribution="NORMAL", parameters=parameters)

    print(case_arrival_ratio)
    print(map)