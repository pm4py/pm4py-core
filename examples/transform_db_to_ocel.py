from datetime import datetime
import pm4py
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import pandas_utils, constants
from pm4py.util.dt_parsing.variants import strpfromiso
import os


def extract_invoices(cursor):
    cursor.execute(
        "SELECT CustomerId, InvoiceId, InvoiceDate, BillingAddress, BillingCity, BillingCountry, BillingPostalCode FROM Invoice")

    invoices = {}
    for res in cursor.fetchall():
        dct = {"ocel:oid": "inv"+str(res[0]), "ocel:type": "invoice", "CustomerId": res[0], "InvoiceId": res[1], "InvoiceDate": strpfromiso.apply(res[2]), "BillingAddress": res[3],
             "BillingCity": res[4], "BillingCountry": res[5], "BillingPostalCode": res[6]}

        invoices[res[0]] = dct

    return invoices


def extract_invoice_lines(cursor):
    cursor.execute("SELECT InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity FROM InvoiceLine")

    invoice_lines = {}
    for res in cursor.fetchall():
        invoice_lines[res[0]] = {"ocel:oid": "invline"+str(res[0]), "ocel:type": "invoiceline", "InvoiceLineId": res[0], "InvoiceId": res[1], "TrackId": res[2], "UnitPrice": res[3], "Category": res[4]}

    return invoice_lines


def extract_customers(cursor):
    cursor.execute("SELECT CustomerId, FirstName, LastName, Company, Address, City, State, Country FROM Customer")

    customers = {}
    for res in cursor.fetchall():
        customers[res[0]] = {"ocel:oid": "cust"+str(res[0]), "ocel:type": "customer", "CustomerId": res[0], "FirstName": res[1], "LastName": res[2], "Company": res[3], "Address": res[4],
             "City": res[5], "State": res[6], "Country": res[7]}

    return customers


def extract_employee(cursor):
    cursor.execute("SELECT EmployeeId, LastName, FirstName, Title, ReportsTo, BirthDate, HireDate, Address, City, State, Country, PostalCode, Phone, Fax, Email FROM Employee")

    employee = {}

    for res in cursor.fetchall():
        dct = {"ocel:oid": "emp"+str(res[0]), "ocel:type": "employee", "EmployeeId": res[0], "LastName": res[1], "FirstName": res[2], "Title": res[3], "ReportsTo": res[4], "BirthDate": strpfromiso.apply(res[5]), "HireDate": strpfromiso.apply(res[6]), "Address": res[7], "City": res[8], "State": res[9], "Country": res[10], "PostalCode": res[11], "Phone": res[12], "Fax": res[13], "Email": res[14]}

        employee[res[0]] = dct

    return employee


def execute_script():
    import sqlite3
    conn = sqlite3.connect("../tests/input_data/db/Chinook_Sqlite.sqlite")
    cursor = conn.cursor()

    invoices = extract_invoices(cursor)
    invoice_lines = extract_invoice_lines(cursor)
    customers = extract_customers(cursor)
    employee = extract_employee(cursor)

    objects = []
    events = []
    relations = []

    for i in invoices:
        objects.append(invoices[i])
    for il in invoice_lines:
        objects.append(invoice_lines[il])
    for c in customers:
        objects.append(customers[c])
    for e in employee:
        objects.append(employee[e])

    inv_line_map = {}
    for i, v in invoice_lines.items():
        if not v["InvoiceId"] in inv_line_map:
            inv_line_map[v["InvoiceId"]] = []
        inv_line_map[v["InvoiceId"]].append(v["InvoiceLineId"])

    for i in invoices:
        event = {"ocel:eid": "evinv"+str(i), "ocel:activity": "Create Invoice", "ocel:timestamp": invoices[i]["InvoiceDate"]}
        events.append(event)

        relation_inv = {"ocel:eid": "evinv"+str(i), "ocel:activity": "Create Invoice", "ocel:timestamp": invoices[i]["InvoiceDate"], "ocel:type": "invoice", "ocel:oid": "inv"+str(i)}
        relations.append(relation_inv)

        relation_cust = {"ocel:eid": "evinv"+str(i), "ocel:activity": "Create Invoice", "ocel:timestamp": invoices[i]["InvoiceDate"], "ocel:type": "customer", "ocel:oid": "cust"+str(i)}
        relations.append(relation_cust)

        for v in inv_line_map[i]:
            relation_line = {"ocel:eid": "evinv"+str(i), "ocel:activity": "Create Invoice", "ocel:timestamp": invoices[i]["InvoiceDate"], "ocel:type": "invoiceline", "ocel:oid": "invline"+str(v)}
            relations.append(relation_line)

    for e in employee:
        event = {"ocel:eid": "evempbirth"+str(e), "ocel:activity": "Employee Birth", "ocel:timestamp": employee[e]["BirthDate"]}
        events.append(event)

        relation = {"ocel:eid": "evempbirth"+str(e), "ocel:activity": "Employee Birth", "ocel:timestamp": employee[e]["BirthDate"], "ocel:type": "employee", "ocel:oid": "emp"+str(e)}
        relations.append(relation)

    for e in employee:
        event = {"ocel:eid": "evemphired"+str(e), "ocel:activity": "Employee Hired", "ocel:timestamp": employee[e]["HireDate"]}
        events.append(event)

        relation = {"ocel:eid": "evemphired"+str(e), "ocel:activity": "Employee Hired", "ocel:timestamp": employee[e]["HireDate"], "ocel:type": "employee", "ocel:oid": "emp"+str(e)}
        relations.append(relation)

    events = pandas_utils.instantiate_dataframe(events)
    objects = pandas_utils.instantiate_dataframe(objects)
    relations = pandas_utils.instantiate_dataframe(relations)

    events = events.sort_values("ocel:timestamp")
    relations = relations.sort_values("ocel:timestamp")

    ocel = OCEL()
    ocel.events = events
    ocel.objects = objects
    ocel.relations = relations

    ocel.events = ocel.events.dropna(subset=["ocel:timestamp"])
    ocel.relations = ocel.relations.dropna(subset=["ocel:timestamp"])

    pm4py.write_ocel(ocel, "chinook.jsonocel")
    ocel = pm4py.read_ocel("chinook.jsonocel")
    os.remove("chinook.jsonocel")


if __name__ == "__main__":
    execute_script()
