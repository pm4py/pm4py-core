import csv
import pm4py.log.instance as log_instance


def import_from_file(path, delimiter=','):
    with open(path, 'r') as file:
        log = log_instance.EventLog()
        reader = csv.reader(file, delimiter=delimiter)
        headers = next(reader)
        for row in reader:
            attr = {}
            for i, val in enumerate(row):
                attr[headers[i]] = val
            log.append(log_instance.Event(attr))
        return log

