import pm4py


def execute_script():
    ocel = pm4py.read_ocel("../tests/input_data/ocel/example_log.jsonocel")
    # creates artificial O2O relationships based on the object interaction, descendants, inheritance, cobirth, codeath graph
    ocel = pm4py.ocel_o2o_enrichment(ocel)
    # creates artificial E2O qualifications based on the fact that an event creates/terminates the lifecycle of an object
    ocel = pm4py.ocel_e2o_lifecycle_enrichment(ocel)
    # prints the E2O table
    print(ocel.relations)
    # prints the O2O table
    print(ocel.o2o)


if __name__ == "__main__":
    execute_script()
