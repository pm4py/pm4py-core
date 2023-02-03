import pm4py


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")
    log = pm4py.insert_case_service_waiting_time(log)
    print(log)


if __name__ == "__main__":
    execute_script()
