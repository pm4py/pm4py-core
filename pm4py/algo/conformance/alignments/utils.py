from pm4py.objects import log as pm4py_log

SKIP = '>>'
STD_MODEL_LOG_MOVE_COST = 10000
STD_TAU_COST = 1
STD_SYNC_COST = 0


def construct_standard_cost_function(synchronous_product_net, skip):
    """
    Returns the standard cost function, which is:
    * event moves: cost 1000
    * model moves: cost 1000
    * tau moves: cost 1
    * sync moves: cost 0

    :param synchronous_product_net:
    :param skip:
    :return:
    """
    costs = {}
    for t in synchronous_product_net.transitions:
        if (skip == t.label[0] or skip == t.label[1]) and (t.label[0] is not None and t.label[1] is not None):
            costs[t] = STD_MODEL_LOG_MOVE_COST
        else:
            if skip == t.label[0] and t.label[1] is None:
                costs[t] = STD_TAU_COST
            else:
                costs[t] = STD_SYNC_COST
    return costs


def construct_event_level_cost_function(log, activity_cost_map, activity_key=pm4py_log.util.xes.DEFAULT_NAME_KEY):
    log = pm4py_log.util.general.convert(log, pm4py_log.log.TRACE_LOG)
    costs = list()
    for t in log:
        t_costs = list()
        for e in t:
            t_costs.append(activity_cost_map[e[activity_key]])
        costs.append(t_costs)
    return costs
