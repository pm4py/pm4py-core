import pm4py


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")

    # gets the frequent trace segments
    traces = pm4py.get_frequent_trace_segments(log, min_occ=100)

    for t in traces:
        # filter on the given trace segment, to obtain an event log where all the cases contain the trace segment
        print(t)
        filtered_log = pm4py.filter_trace_segments(log, [t])
        print(filtered_log)

        break


if __name__ == "__main__":
    execute_script()
