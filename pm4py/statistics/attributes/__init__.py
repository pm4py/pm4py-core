from pm4py.statistics.attributes import common, log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.statistics.attributes import pandas

