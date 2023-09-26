import importlib.util
from pm4py.streaming.importer import csv

if importlib.util.find_spec("lxml"):
    from pm4py.streaming.importer import xes
