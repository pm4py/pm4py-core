import sqlite3
import pandas as pd
from copy import copy
from dateutil import parser
from pm4py.util.dt_parsing.variants import strpfromiso

import pm4py
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import constants, pandas_utils
import os


def execute_script():
    conn = sqlite3.connect("../tests/input_data/db/northwind.sqlite")
    employees = pd.read_sql("SELECT EmployeeID, BirthDate, HireDate FROM Employees", conn)
    employees = employees.to_dict("records")
    orders = pd.read_sql("SELECT OrderID, CustomerID, EmployeeID, OrderDate, RequiredDate, ShippedDate FROM Orders", conn)
    orders = orders.to_dict("records")

    events = []
    relations = []
    objects = []
    objects_ids = set()

    eid = 0
    for e in employees:
        oid = str(e["EmployeeID"])
        if oid not in objects_ids:
            obj = {"ocel:oid": oid, "ocel:type": "Employee"}
            objects.append(obj)
            objects_ids.add(oid)

        eid += 1
        ev = {"ocel:eid": str(eid), "ocel:activity": "Created Employee", "ocel:timestamp": strpfromiso.fix_naivety(parser.parse(e["HireDate"]))}
        events.append(ev)

        rel = copy(ev)
        rel["ocel:oid"] = str(e["EmployeeID"])
        rel["ocel:type"] = "Employee"
        relations.append(rel)

    for o in orders:
        oid = str(o["OrderID"])

        if oid not in objects_ids:
            obj = {"ocel:oid": oid, "ocel:type": "Order"}
            objects.append(obj)
            objects_ids.add(oid)

        eid += 1
        ev = {"ocel:eid": str(eid), "ocel:activity": "Created Order", "ocel:timestamp": strpfromiso.fix_naivety(parser.parse(o["OrderDate"]))}
        events.append(ev)

        rel1 = copy(ev)
        rel1["ocel:oid"] = str(o["OrderID"])
        rel1["ocel:type"] = "Order"
        relations.append(rel1)

        rel2 = copy(ev)
        rel2["ocel:oid"] = str(o["EmployeeID"])
        rel2["ocel:type"] = "Employee"
        relations.append(rel2)

    ocel = OCEL(events=pandas_utils.instantiate_dataframe(events), objects=pandas_utils.instantiate_dataframe(objects), relations=pandas_utils.instantiate_dataframe(relations))
    pm4py.write_ocel(ocel, "log1.jsonocel")

    events = None
    relations = None
    objects = None
    objects_ids = None
    events = []
    relations = []
    objects = []
    objects_ids = set()

    eid = 0
    oid = 0
    for e in employees:
        oid = str(e["EmployeeID"])
        if oid not in objects_ids:
            obj = {"ocel:oid": oid, "ocel:type": "Employee"}
            objects.append(obj)
            objects_ids.add(oid)

        eid += 1
        ev0 = {"ocel:eid": str(eid), "ocel:activity": "Employee Birth", "ocel:timestamp": strpfromiso.fix_naivety(parser.parse(e["BirthDate"]))}
        events.append(ev0)

        eid += 1
        ev = {"ocel:eid": str(eid), "ocel:activity": "Hired Employee", "ocel:timestamp": strpfromiso.fix_naivety(parser.parse(e["HireDate"]))}
        events.append(ev)

        rel = copy(ev0)
        rel["ocel:oid"] = str(e["EmployeeID"])
        rel["ocel:type"] = "Employee"
        relations.append(rel)

        rel = copy(ev)
        rel["ocel:oid"] = str(e["EmployeeID"])
        rel["ocel:type"] = "Employee"
        relations.append(rel)

    for o in orders:
        oid = str(o["OrderID"])

        if oid not in objects_ids:
            obj = {"ocel:oid": oid, "ocel:type": "Order"}
            objects.append(obj)
            objects_ids.add(oid)

        eid += 1
        ev = {"ocel:eid": str(eid), "ocel:activity": "Created Order", "ocel:timestamp": strpfromiso.fix_naivety(parser.parse(o["OrderDate"]))}
        events.append(ev)


        rel1 = copy(ev)
        rel1["ocel:oid"] = str(o["OrderID"])
        rel1["ocel:type"] = "Order"
        relations.append(rel1)

        rel2 = copy(ev)
        rel2["ocel:oid"] = str(o["EmployeeID"])
        rel2["ocel:type"] = "Employee"
        relations.append(rel2)

        if o["ShippedDate"] is not None:
            eid += 1
            ev3 = {"ocel:eid": str(eid), "ocel:activity": "Order Shipped", "ocel:timestamp": strpfromiso.fix_naivety(parser.parse(o["ShippedDate"]))}
            events.append(ev3)

            rel3 = copy(ev3)
            rel3["ocel:oid"] = str(o["OrderID"])
            rel3["ocel:type"] = "Order"
            relations.append(rel3)

        if o["RequiredDate"] is not None:
            eid += 1
            ev4 = {"ocel:eid": str(eid), "ocel:activity": "Order Due Date", "ocel:timestamp": strpfromiso.fix_naivety(parser.parse(o["RequiredDate"]))}
            events.append(ev4)

            rel4 = copy(ev4)
            rel4["ocel:oid"] = str(o["OrderID"])
            rel4["ocel:type"] = "Order"
            relations.append(rel4)

    ocel = OCEL(events=pandas_utils.instantiate_dataframe(events), objects=pandas_utils.instantiate_dataframe(objects), relations=pandas_utils.instantiate_dataframe(relations))
    pm4py.write_ocel(ocel, "log2.jsonocel")

    os.remove("log1.jsonocel")
    os.remove("log2.jsonocel")


if __name__ == "__main__":
    execute_script()
