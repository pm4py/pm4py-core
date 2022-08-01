from pm4py.algo.discovery.dfg.variants import native, performance, freq_triples, case_attributes, clean
import pkgutil

if pkgutil.find_loader("polars"):
    from pm4py.algo.discovery.dfg.variants import clean_polars

