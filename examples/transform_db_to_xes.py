from dateutil.parser import parse
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.util.dt_parsing.variants import strpfromiso
import pm4py
import os


def extract_invoices(cursor):
    cursor.execute(
        "SELECT CustomerId, InvoiceId, InvoiceDate, BillingAddress, BillingCity, BillingCountry, BillingPostalCode FROM Invoice")

    invoices = {}
    for res in cursor.fetchall():
        if not res[0] in invoices:
            invoices[res[0]] = []
        invoices[res[0]].append(
            {"CustomerId": res[0], "InvoiceId": res[1], "InvoiceDate": strpfromiso.fix_naivety(parse(res[2])), "BillingAddress": res[3],
             "BillingCity": res[4], "BillingCountry": res[5], "BillingPostalCode": res[6]})

    return invoices


def extract_invoice_lines(cursor):
    cursor.execute("SELECT InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity FROM InvoiceLine")

    invoice_lines = {}
    for res in cursor.fetchall():
        if not res[1] in invoice_lines:
            invoice_lines[res[1]] = []
        invoice_lines[res[1]].append({"InvoiceLineId": res[0], "InvoiceId": res[1], "TrackId": res[2], "UnitPrice": res[3], "Category": res[4]})

    return invoice_lines


def extract_customers(cursor):
    cursor.execute("SELECT CustomerId, FirstName, LastName, Company, Address, City, State, Country FROM Customer")

    customers = {}
    for res in cursor.fetchall():
        customers[res[0]] = {"CustomerId": res[0], "FirstName": res[1], "LastName": res[2], "Company": res[3], "Address": res[4],
             "City": res[5], "State": res[6], "Country": res[7]}

    return customers


def execute_script():
    import sqlite3
    conn = sqlite3.connect("../tests/input_data/db/Chinook_Sqlite.sqlite")
    cursor = conn.cursor()

    invoices = extract_invoices(cursor)
    invoice_lines = extract_invoice_lines(cursor)
    customers = extract_customers(cursor)

    log = EventLog()
    for customer in customers:
        trace = Trace()
        trace.attributes.update(customers[customer])
        log.append(trace)
        for invoice in invoices[customer]:
            event = Event()
            for k, v in invoice.items():
                event[k] = v
            event["time:timestamp"] = event["InvoiceDate"]
            event["concept:name"] = "Sent Invoice"
            event["invoice_lines"] = []
            for item in invoice_lines[invoice["InvoiceId"]]:
                event["invoice_lines"].append(item)
            trace.append(event)

    pm4py.write_xes(log, "chinook.xes")
    os.remove("chinook.xes")


if __name__ == "__main__":
    execute_script()
