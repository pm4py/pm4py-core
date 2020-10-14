from pm4py.statistics.start_activities import common, log
import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.statistics.start_activities import pandas
