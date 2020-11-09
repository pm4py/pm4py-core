import pkgutil
from pm4py.streaming.importer import csv

if pkgutil.find_loader("lxml"):
    from pm4py.streaming.importer import xes

