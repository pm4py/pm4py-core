import pm4py
import sys


def execute_script():
    ocel = pm4py.read_ocel("../tests/input_data/ocel/example_log.jsonocel")
    print(ocel)
    # filters the connected components of the OCEL in which there is at least a delivery,
    # obtaining a filtered OCEL back.
    ocel_with_del = pm4py.filter_ocel_cc_otype(ocel, "delivery")
    print(ocel_with_del)
    # filters the connected components of the OCEL with at least five different objects,
    # obtaining a filtered OCEL back.
    ocel_with_three_objs = pm4py.filter_ocel_cc_length(ocel, 5, sys.maxsize)
    print(ocel_with_three_objs)


if __name__ == "__main__":
    execute_script()
