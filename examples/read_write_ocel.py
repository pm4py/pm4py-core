import pm4py
import os


def execute_script():
    ocel = pm4py.read_ocel("../tests/input_data/ocel/example_log.jsonocel")
    print(ocel)
    print("attribute names: ", pm4py.ocel_get_attribute_names(ocel))
    print("object types: ", pm4py.ocel_get_object_types(ocel))
    print("flattening to order: ")
    print(pm4py.ocel_flattening(ocel, "order"))
    pm4py.write_ocel(ocel, "prova.jsonocel")
    os.remove("prova.jsonocel")


if __name__ == "__main__":
    execute_script()
