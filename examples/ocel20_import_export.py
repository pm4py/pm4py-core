import pm4py
import os


def execute_script():
    ocel = pm4py.read_ocel2("../tests/input_data/ocel/ocel20_example.sqlite")
    pm4py.write_ocel2(ocel, "ocel20_example_bis.sqlite")
    pm4py.write_ocel2(ocel, "ocel20_example_bis.xmlocel")
    ocel = pm4py.read_ocel2("../tests/input_data/ocel/ocel20_example.xmlocel")
    pm4py.write_ocel2(ocel, "ocel20_example_tris.sqlite")
    pm4py.write_ocel2(ocel, "ocel20_example_tris.xmlocel")
    os.remove("ocel20_example_bis.sqlite")
    os.remove("ocel20_example_bis.xmlocel")
    os.remove("ocel20_example_tris.sqlite")
    os.remove("ocel20_example_tris.xmlocel")


if __name__ == "__main__":
    execute_script()
