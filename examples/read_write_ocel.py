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

    print("ocel_object_type_activities")
    print(pm4py.ocel_object_type_activities(ocel))

    print("ocel_objects_ot_count")
    print(pm4py.ocel_objects_ot_count(ocel))

    print("filter_ocel_event_attribute")
    ocel1 = pm4py.filter_ocel_event_attribute(ocel, "ocel:activity", ["Create Order"])
    print(ocel1.get_extended_table())

    print("filter_ocel_object_attribute")
    ocel2 = pm4py.filter_ocel_object_attribute(ocel, "ocel:type", ["order", "delivery"])
    print(ocel2.get_extended_table())

    print("filter_ocel_object_types_allowed_activities")
    ocel3 = pm4py.filter_ocel_object_types_allowed_activities(ocel, {"order": {"Create Order"}, "element": {"Create Order"}})
    print(ocel3.get_extended_table())

    print("filter_ocel_start_events_per_object_type")
    ocel4 = pm4py.filter_ocel_start_events_per_object_type(ocel, "order")
    print(ocel4.get_extended_table())

    print("filter_ocel_end_events_per_object_type")
    ocel5 = pm4py.filter_ocel_end_events_per_object_type(ocel, "order")
    print(ocel5.get_extended_table())

    print("filter_ocel_object_per_type_count")
    ocel6 = pm4py.filter_ocel_object_per_type_count(ocel, {"order": 1, "element": 2})
    print(ocel6.get_extended_table())

    print("filter_ocel_events_timestamp")
    ocel7 = pm4py.filter_ocel_events_timestamp(ocel, "1981-01-01 00:00:00", "1982-01-01 00:00:00")
    print(ocel7.get_extended_table())


if __name__ == "__main__":
    execute_script()
