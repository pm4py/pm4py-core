import pkgutil

if pkgutil.find_loader("pandas"):
    from pm4py.algo.clustering import trace_attribute_driven
