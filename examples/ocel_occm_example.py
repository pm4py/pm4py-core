import pm4py
from pm4py.algo.transformation.ocel.split_ocel import algorithm as split_ocel


def execute_script():
    ocel = pm4py.read_ocel("../tests/input_data/ocel/example_log.jsonocel")
    # gets an OCEL describing the executions of the objects of a given object type
    lst_ocels = split_ocel.apply(ocel, variant=split_ocel.Variants.ANCESTORS_DESCENDANTS, parameters={"object_type": "order"})

    # CONDITION 1: check if an order is associated with at least a delivery
    for oc in lst_ocels:
        oc_filtered = pm4py.filter_ocel_event_attribute(oc, "ocel:activity", ["Create Order", "Create Delivery"])
        oc_filtered = [(x["ocel:activity"], x["ocel:timestamp"].timestamp()) for x in oc_filtered.events.to_dict("records")]
        idxs_create_order = [i for i in range(len(oc_filtered)) if oc_filtered[i][0] == "Create Order"]
        order_is_ok = True
        for i in idxs_create_order:
            deliveries = [oc_filtered[j] for j in range(i+1,len(oc_filtered)) if oc_filtered[j][0] == "Create Delivery"]
            #print(deliveries)
            if len(deliveries) < 1:
                order_is_ok = False
        if not order_is_ok:
            print("condition 1 VIOLATING order ", oc.parameters["@@central_object"])

    # CONDITION 2: check if the temporal distance between an order and the delivery is less than a specified amount of time
    for oc in lst_ocels:
        oc_filtered = pm4py.filter_ocel_event_attribute(oc, "ocel:activity", ["Create Order", "Create Delivery"])
        oc_filtered = [(x["ocel:activity"], x["ocel:timestamp"].timestamp()) for x in oc_filtered.events.to_dict("records")]
        idxs_create_order = [i for i in range(len(oc_filtered)) if oc_filtered[i][0] == "Create Order"]
        order_is_ok = True
        for i in idxs_create_order:
            time_create_order = oc_filtered[i][1]
            deliveries = [oc_filtered[j] for j in range(i+1,len(oc_filtered)) if oc_filtered[j][0] == "Create Delivery"]
            for d in deliveries:
                time_create_delivery = d[1]
                # consider anomalous when the event of create delivery happens more than 1000000 seconds than the event of create order
                if (time_create_delivery - time_create_order) > 1000000:
                    order_is_ok = False
                    break
        if not order_is_ok:
            print("condition 2 VIOLATING order ", oc.parameters["@@central_object"])

    # CONDITION 3: check conditions on the time from the previous activity (any) given 'Create Delivery'
    for oc0 in lst_ocels:
        oc = [(x["ocel:activity"], x["ocel:timestamp"].timestamp()) for x in oc0.events.to_dict("records")]
        idxs_create_delivery = [i for i in range(len(oc)) if oc[i][0] == "Create Delivery"]
        delivery_is_ok = True
        for i in idxs_create_delivery:
            if i > 0:
                time_create_delivery = oc[i][1]
                time_previous = oc[i-1][1]
                # consider anomalous when the event of create delivery happens more than 100000 after the timestamp of the previous event
                if (time_create_delivery - time_previous) > 100000:
                    delivery_is_ok = False
                    break
        if not delivery_is_ok:
            print("condition 3 VIOLATING delivery ", oc0.parameters["@@central_object"])


if __name__ == "__main__":
    execute_script()
