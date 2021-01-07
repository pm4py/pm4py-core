import pm4py


if __name__ == "__main__":
    log = pm4py.read_xes('../tests/input_data/running-example.xes')
    allowed = {'a', 'b', 'c'}
    filtered = pm4py.filter_log(lambda t: t[0] in allowed, log)
