from pm4py.objects.ocel.importer.sqlite import importer as ocel20_sqlite_importer
from pm4py.objects.ocel.exporter.sqlite import exporter as ocel20_sqlite_exporter
from pm4py.objects.ocel.importer.xmlocel import importer as ocel20_xml_importer
from pm4py.objects.ocel.exporter.xmlocel import exporter as ocel20_xml_exporter
import os


def execute_script():
    ocel = ocel20_sqlite_importer.apply("../tests/input_data/ocel/ocel20_example.sqlite", variant=ocel20_sqlite_importer.Variants.OCEL20)
    ocel20_sqlite_exporter.apply(ocel, "ocel20_example_bis.sqlite", variant=ocel20_sqlite_exporter.Variants.OCEL20)
    ocel20_xml_exporter.apply(ocel, "ocel20_example_bis.xmlocel", variant=ocel20_xml_exporter.Variants.OCEL20)
    ocel = ocel20_xml_importer.apply("../tests/input_data/ocel/ocel20_example.xmlocel", variant=ocel20_xml_importer.Variants.OCEL20)
    ocel20_sqlite_exporter.apply(ocel, "ocel20_example_tris.sqlite", variant=ocel20_sqlite_exporter.Variants.OCEL20)
    ocel20_xml_exporter.apply(ocel, "ocel20_example_tris.xmlocel", variant=ocel20_xml_exporter.Variants.OCEL20)
    os.remove("ocel20_example_bis.sqlite")
    os.remove("ocel20_example_bis.xmlocel")
    os.remove("ocel20_example_tris.sqlite")
    os.remove("ocel20_example_tris.xmlocel")


if __name__ == "__main__":
    execute_script()
