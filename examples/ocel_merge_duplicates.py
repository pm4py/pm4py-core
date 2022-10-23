import pm4py


def execute_script():
    ocel = pm4py.read_ocel("../tests/input_data/ocel/example_log.jsonocel")
    print(ocel.get_extended_table())
    ocel = pm4py.ocel_merge_duplicates(ocel)
    print(ocel.get_extended_table())


if __name__ == "__main__":
    execute_script()
