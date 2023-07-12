import pm4py


def execute_script():
    log = pm4py.read_xes('../tests/input_data/receipt.xes', return_legacy_log_object=True)
    intervals = pm4py.convert_log_to_time_intervals(log, ('Confirmation of receipt', 'T02 Check confirmation of receipt'))
    i = 0
    fifo = 0
    nonfifo = 0
    while i < len(intervals)-1:
        if intervals[i][1] < intervals[i+1][0]:
            fifo += 1
        else:
            nonfifo += 1

        i = i + 1

    print("Number of FIFO executions in the given path:", fifo)
    print("Number of non-FIFO executions in the given path:", nonfifo)


if __name__ == "__main__":
    execute_script()
