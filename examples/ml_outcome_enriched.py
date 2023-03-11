import pm4py


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")
    log = pm4py.extract_outcome_enriched_dataframe(log)
    print(log)


if __name__ == "__main__":
    execute_script()
