import pm4py
from pm4py.algo.transformation.log_to_interval_tree.variants import open_paths


def execute_script():
    """
    Scripts checking the maximum number of concurrently open paths (in distinct cases of the log)
    between two activities (in this situation, "Confirmation of receipt" and "T02 Check confirmation of receipt").
    """
    epsilon = 0.0001
    log = pm4py.read_xes('../tests/input_data/receipt.xes', return_legacy_log_object=True)
    intervals = pm4py.convert_log_to_time_intervals(log, ('Confirmation of receipt', 'T02 Check confirmation of receipt'))
    interval_tree = open_paths.interval_to_tree(intervals)
    max_conc_exec = 0
    argmax_conc_exec = None
    for inte in intervals:
        # check how many intervals in the three are open at the start and end point of this interval
        # this leads to the maximum
        at_start = interval_tree[inte[0]-epsilon:inte[0]+epsilon]
        at_end = interval_tree[inte[1]-epsilon:inte[1]+epsilon]
        if len(at_start) > max_conc_exec:
            max_conc_exec = len(at_start)
            argmax_conc_exec = (inte[0], at_start)
        if len(at_end) > max_conc_exec:
            max_conc_exec = len(at_end)
            argmax_conc_exec = (inte[1], at_end)
    # prints the maximum number of concurrent paths,
    # and the point in which the maximum was measured
    print(max_conc_exec)
    print(argmax_conc_exec)


if __name__ == "__main__":
    execute_script()
